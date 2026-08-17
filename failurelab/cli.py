import argparse
import json
import sys
from pathlib import Path
from failurelab.class_policy_config import load_class_policy

from failurelab.config import (
    build_stress_tests,
    load_suite_config,
)
from failurelab.history import SuiteHistory
from failurelab.policy_config import load_robustness_policy
from failurelab.robustness_policy import evaluate_policy
from failurelab.vision_report import VisionWeakness

from .comparison import (
    BoundaryComparison,
    ModelComparison,
    RobustnessRegressionError,
)
from .policy import load_policy

try:
    from . import __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="failurelab",
        description=(
            "Stress-test machine-learning models "
            "and enforce robustness policies."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    check_parser = subparsers.add_parser(
        "check",
        help="Validate a saved robustness policy.",
    )

    check_parser.add_argument(
        "--policy",
        type=Path,
        required=True,
    )

    compare_parser = subparsers.add_parser(
        "compare",
        help="Enforce a saved model-comparison robustness gate.",
    )

    compare_parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Baseline robustness snapshot JSON file.",
    )

    compare_parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="Candidate robustness snapshot JSON file.",
    )

    compare_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.02,
        help=(
            "Maximum allowed increase in worst-case degradation "
            "before a regression is reported. Default: 0.02."
        ),
    )

    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Generate a robustness visualization from a report.",
    )

    visualize_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing vision robustness weaknesses.",
    )

    visualize_parser.add_argument(
        "--output",
        type=Path,
        default=Path("failurelab_robustness.png"),
        help="Output path for the generated PNG chart.",
    )

    suite_parser = subparsers.add_parser(
        "suite",
        help="Validate and inspect a configured stress suite.",
    )

    suite_parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to a FailureLab stress-suite JSON configuration.",
    )

    history_parser = subparsers.add_parser(
        "history",
        help="Inspect robustness history for a suite or model.",
    )

    history_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a FailureLab suite-history JSON file.",
    )

    history_target = history_parser.add_mutually_exclusive_group(
        required=True
    )

    history_target.add_argument(
        "--suite",
        help="Suite name to inspect.",
    )

    history_target.add_argument(
        "--model",
        help="Model ID to inspect.",
    )

    history_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help=(
            "Maximum change treated as stable. "
            "Default: 0.01."
        ),
    )

    policy_parser = subparsers.add_parser(
        "policy-evaluate",
        help="Evaluate saved suite results against a robustness policy.",
    )

    policy_parser.add_argument(
        "--result",
        type=Path,
        required=True,
        help="Saved FailureLab suite-result JSON file.",
    )

    policy_parser.add_argument(
        "--policy",
        type=Path,
        required=True,
        help="Robustness policy JSON file.",
    )

    policy_parser.add_argument(
        "--class-policy",
        type=Path,
        default=None,
        help="Optional class-level robustness policy JSON file.",
    )

    return parser


def _load_model_snapshot(
    path: Path,
) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"FailureLab comparison file not found: {path}"
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    required = {
        "score",
        "boundaries",
    }

    missing = required - set(
        data.keys()
    )

    if missing:
        missing_text = ", ".join(
            sorted(missing)
        )

        raise ValueError(
            f"Comparison file {path} is missing "
            f"required field(s): {missing_text}"
        )

    if not isinstance(
        data["boundaries"],
        list,
    ):
        raise ValueError(
            f"Comparison file {path} has invalid "
            "'boundaries' data."
        )

    return data


def _build_comparison_from_snapshots(
    baseline_data: dict,
    candidate_data: dict,
    regression_tolerance: float = 0.02,
) -> ModelComparison:
    if regression_tolerance < 0:
        raise ValueError(
            "regression tolerance cannot be negative."
        )

    baseline_boundaries = {
        boundary["stress_name"]: boundary
        for boundary in baseline_data["boundaries"]
    }

    candidate_boundaries = {
        boundary["stress_name"]: boundary
        for boundary in candidate_data["boundaries"]
    }

    comparisons = []

    higher_is_better = {
        "blur",
        "occlusion",
        "rotation",
    }

    lower_is_better = {
        "brightness",
        "compression",
        "crop",
    }

    for stress_name in baseline_boundaries:
        if stress_name not in candidate_boundaries:
            continue

        baseline = baseline_boundaries[
            stress_name
        ]

        candidate = candidate_boundaries[
            stress_name
        ]

        baseline_threshold = baseline.get(
            "failure_threshold"
        )

        candidate_threshold = candidate.get(
            "failure_threshold"
        )

        if (
            baseline_threshold is None
            and candidate_threshold is None
        ):
            threshold_status = "unchanged"

        elif (
            baseline_threshold is not None
            and candidate_threshold is None
        ):
            threshold_status = "improved"

        elif (
            baseline_threshold is None
            and candidate_threshold is not None
        ):
            threshold_status = "regressed"

        elif stress_name in higher_is_better:
            if candidate_threshold > baseline_threshold:
                threshold_status = "improved"

            elif candidate_threshold < baseline_threshold:
                threshold_status = "regressed"

            else:
                threshold_status = "unchanged"

        elif stress_name in lower_is_better:
            if candidate_threshold < baseline_threshold:
                threshold_status = "improved"

            elif candidate_threshold > baseline_threshold:
                threshold_status = "regressed"

            else:
                threshold_status = "unchanged"

        else:
            threshold_status = "unchanged"

        baseline_worst_drop = float(
            baseline[
                "worst_top1_drop"
            ]
        )

        candidate_worst_drop = float(
            candidate[
                "worst_top1_drop"
            ]
        )

        worst_drop_delta = (
            candidate_worst_drop
            - baseline_worst_drop
        )

        threshold_regressed = (
            threshold_status
            == "regressed"
        )

        drop_regressed = (
            worst_drop_delta
            > regression_tolerance
        )

        if (
            threshold_regressed
            and drop_regressed
        ):
            reason = "both"

        elif threshold_regressed:
            reason = "threshold"

        elif drop_regressed:
            reason = "worst_drop"

        else:
            reason = "none"

        comparisons.append(
            BoundaryComparison(
                stress_name=stress_name,
                baseline_threshold=baseline_threshold,
                candidate_threshold=candidate_threshold,
                baseline_worst_drop=baseline_worst_drop,
                candidate_worst_drop=candidate_worst_drop,
                worst_drop_delta=worst_drop_delta,
                threshold_status=threshold_status,
                regression=(
                    threshold_regressed
                    or drop_regressed
                ),
                regression_reason=reason,
            )
        )

    baseline_score = float(
        baseline_data["score"]
    )

    candidate_score = float(
        candidate_data["score"]
    )

    return ModelComparison(
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        score_delta=(
            candidate_score
            - baseline_score
        ),
        boundaries=comparisons,
    )


def run_check(
    policy_path: Path,
) -> int:
    thresholds = load_policy(
        policy_path
    )

    print(
        f"Loaded {len(thresholds)} "
        f"robustness requirement(s)."
    )

    return 0


def run_compare(
    baseline_path: Path,
    candidate_path: Path,
    regression_tolerance: float = 0.02,
) -> int:
    baseline_data = _load_model_snapshot(
        baseline_path
    )

    candidate_data = _load_model_snapshot(
        candidate_path
    )

    comparison = (
        _build_comparison_from_snapshots(
            baseline_data,
            candidate_data,
            regression_tolerance=regression_tolerance,
        )
    )

    print(
        comparison.summary()
    )

    try:
        comparison.require_pass()

    except RobustnessRegressionError as exc:
        print()
        print(
            "RESULT: FAILED"
        )

        print(
            str(exc)
        )

        return 1

    print()
    print(
        "RESULT: PASSED"
    )

    return 0


def run_visualize(
    input_path: Path,
    output_path: Path,
) -> int:
    from failurelab.visualization import plot_robustness_drops

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    if isinstance(data, dict):
        rows = data.get(
            "weaknesses",
            [],
        )

    elif isinstance(data, list):
        rows = data

    else:
        raise ValueError(
            "Visualization input must be a JSON list "
            "or contain a 'weaknesses' list."
        )

    weaknesses = [
        VisionWeakness(
            name=row["name"],
            severity=row["severity"],
            top1_drop=float(
                row["top1_drop"]
            ),
            top5_drop=float(
                row["top5_drop"]
            ),
            confidence_drop=float(
                row["confidence_drop"]
            ),
        )
        for row in rows
    ]

    plot_robustness_drops(
        weaknesses,
        output_path=output_path,
    )

    print(
        f"Robustness visualization saved to {output_path}"
    )

    return 0


def run_suite(
    config_path: Path,
) -> int:
    config = load_suite_config(
        config_path
    )

    stress_tests = build_stress_tests(
        config
    )

    print(
        f"Suite: {config.name}"
    )

    print(
        f"Loaded {len(stress_tests)} configured stress test(s)."
    )

    if config.maximum_drop is not None:
        print(
            f"Maximum drop: {config.maximum_drop:.2%}"
        )

    for stress_test in stress_tests:
        print(
            f"- {stress_test.name}"
        )

    return 0


def run_history(
    input_path: Path,
    suite_name: str | None,
    model_id: str | None,
    tolerance: float,
) -> int:
    history = SuiteHistory.load_json(
        input_path
    )

    if suite_name is not None:
        latest = history.latest_for_suite(
            suite_name
        )

        if latest is None:
            raise ValueError(
                f"no history found for suite '{suite_name}'."
            )

        trend = history.trend(
            suite_name,
            tolerance=tolerance,
        )

        print(
            f"Suite: {suite_name}"
        )

    else:
        latest = history.latest_for_model(
            model_id
        )

        if latest is None:
            raise ValueError(
                f"no history found for model '{model_id}'."
            )

        trend = history.model_trend(
            model_id,
            tolerance=tolerance,
        )

        print(
            f"Model: {model_id}"
        )

        print(
            f"Suite: {latest.suite_name}"
        )

    print(
        f"Latest status: {latest.status}"
    )

    print(
        f"Worst stress: {latest.worst_stress}"
    )

    print(
        f"Worst drop: {latest.worst_drop:.2%}"
    )

    print(
        f"Trend: {trend}"
    )

    if latest.run_id is not None:
        print(
            f"Run ID: {latest.run_id}"
        )

    return 0


def run_policy_evaluate(
    result_path: Path,
    policy_path: Path,
    class_policy_path: Path | None = None,
) -> int:
    from failurelab.policy_report import build_policy_report
    from failurelab.suite_runner import SuiteResult

    result = SuiteResult.load_json(
        result_path
    )

    policy = load_robustness_policy(
        policy_path
    )

    if class_policy_path is not None:
        (
            default_class_policy,
            class_policies,
        ) = load_class_policy(
            class_policy_path
        )
    else:
        default_class_policy = None
        class_policies = None

    report = build_policy_report(
        result,
        policy,
        default_class_policy=default_class_policy,
        class_policies=class_policies,
    )

    print(
        f"Suite: {result.name}"
    )

    print(
        f"Policy status: {report.policy_status}"
    )

    if class_policy_path is not None:
        print(
            f"Class policy status: "
            f"{report.class_policy_status}"
        )

        print(
            f"Classes evaluated: "
            f"{report.class_evaluation.evaluated_classes}"
        )

        print(
            f"Classes skipped: "
            f"{report.class_evaluation.skipped_classes}"
        )

    for violation in report.evaluation.violations:
        print(
            f"- {violation.stress_name}: "
            f"{violation.metric} "
            f"{violation.observed:.2%} "
            f"> {violation.allowed:.2%}"
        )

    for violation in report.class_evaluation.violations:
        print(
            f"- class {violation.class_index}: "
            f"{violation.metric} "
            f"{violation.observed:.2%} "
            f"> {violation.allowed:.2%}"
        )

    if not report.passed:
        print()
        print(
            "RESULT: FAILED"
        )

        return 1

    print()
    print(
        "RESULT: PASSED"
    )

    return 0

def main():
    args = build_parser().parse_args()

    try:
        if args.command == "check":
            return run_check(
                args.policy
            )

        if args.command == "compare":
            return run_compare(
                baseline_path=args.baseline,
                candidate_path=args.candidate,
                regression_tolerance=args.tolerance,
            )

        if args.command == "visualize":
            return run_visualize(
                input_path=args.input,
                output_path=args.output,
            )

        if args.command == "suite":
            return run_suite(
                config_path=args.config,
            )

        if args.command == "history":
            return run_history(
                input_path=args.input,
                suite_name=args.suite,
                model_id=args.model,
                tolerance=args.tolerance,
            )

        if args.command == "policy-evaluate":
            return run_policy_evaluate(
                result_path=args.result,
                policy_path=args.policy,
                class_policy_path=args.class_policy,
            )

    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as exc:
        print(
            f"FailureLab error: {exc}",
            file=sys.stderr,
        )

        return 2

    return 2


if __name__ == "__main__":
    sys.exit(
        main()
    )