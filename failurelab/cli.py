import argparse
import json
import sys
from failurelab.failure_cluster_policy import (
    evaluate_failure_cluster_policy,
)
from failurelab.failure_cluster_policy_config import (
    load_failure_cluster_policy,
)
from failurelab.failure_cluster_report import (
    build_failure_cluster_report,
)
from failurelab.failure_correlation_policy import (
    evaluate_failure_correlation_policy,
)
from failurelab.failure_correlation_policy_config import (
    load_failure_correlation_policy,
)
from failurelab.failure_correlation_report import (
    build_failure_correlation_report,
)
from failurelab.sample_policy import (
    evaluate_sample_failure_policy,
)
from failurelab.sample_policy_config import (
    load_sample_failure_policy,
)
from failurelab.sample_report import (
    SampleFailureReport,
)
from pathlib import Path
from failurelab.class_policy_config import load_class_policy
from failurelab.cross_stress_policy import (
    evaluate_cross_stress_policy,
)
from failurelab.cross_stress_policy_config import (
    load_cross_stress_policy,
)
from failurelab.cross_stress_report import (
    build_cross_stress_report,
)

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

from failurelab.progression import (
    ProgressionPoint,
    summarize_progression_history,
)
from failurelab.progression_export import export_progression_json
from failurelab.progression_policy import evaluate_progression_policy
from failurelab.progression_risk import (
    highest_risk_checkpoint,
    score_checkpoint_risk,
)

from failurelab.failure_diagnostic_report import (
    build_failure_diagnostic_report,
)
from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_comparison import (
    compare_failure_signatures,
)
from failurelab.signature_export import (
    export_signature_json,
)
from failurelab.signature_policy import (
    evaluate_signature_policy,
)

from failurelab.signature_history import (
    SignatureCheckpoint,
    analyze_signature_history,
)
from failurelab.signature_history_export import (
    export_signature_history_json,
)
from failurelab.signature_history_policy import (
    evaluate_signature_history_policy,
)

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.failure_triage_export import (
    export_failure_triage_json,
)
from failurelab.failure_triage_policy import (
    evaluate_failure_triage_policy,
)

from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_persistence_report import (
    build_failure_persistence_report,
)
from failurelab.failure_persistence_policy import (
    evaluate_failure_persistence_policy,
)
from failurelab.failure_persistence_export import (
    export_failure_persistence_json,
)

from failurelab.failure_resolution_report import (
    build_failure_resolution_report,
)
from failurelab.failure_resolution_policy import (
    evaluate_failure_resolution_policy,
)
from failurelab.failure_resolution_export import (
    export_failure_resolution_json,
)

from failurelab.failure_forecast_report import (
    build_failure_forecast_report,
)
from failurelab.failure_forecast_policy import (
    evaluate_failure_forecast_policy,
)
from failurelab.failure_forecast_export import (
    export_failure_forecast_json,
)

from failurelab.evaluation_profile import (
    load_evaluation_profile,
)
from failurelab.evaluation_profile_validation import (
    validate_evaluation_profile,
)
from failurelab.evaluation_plan import (
    build_evaluation_plan,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)
from failurelab.evaluation_export import (
    export_evaluation_json,
)

from failurelab.evaluator import (
    run_evaluation,
)
from failurelab.evaluation_handlers import (
    build_profile_handlers,
)

from failurelab.triage_comparison import (
    compare_failure_triage,
)
from failurelab.triage_comparison_export import (
    export_triage_comparison_json,
)
from failurelab.triage_comparison_policy import (
    evaluate_triage_comparison_policy,
)

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

    cross_stress_parser = subparsers.add_parser(
        "cross-stress",
        help=(
            "Analyze class vulnerabilities across "
            "multiple stresses."
        ),
    )

    cross_stress_parser.add_argument(
        "--result",
        type=Path,
        required=True,
        help="Saved FailureLab suite-result JSON file.",
    )

    cross_stress_parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help=(
            "Optional cross-stress policy JSON file."
        ),
    )

    cross_stress_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Optional path for the cross-stress "
            "JSON report."
        ),
    )

    sample_report_parser = subparsers.add_parser(
        "sample-report",
        help=(
            "Inspect a saved sample failure report "
            "and optionally enforce a policy."
        ),
    )

    sample_report_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Saved sample failure report JSON file.",
    )

    sample_report_parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Optional sample failure policy JSON file.",
    )

    correlation_parser = subparsers.add_parser(
        "correlation",
        help=(
            "Analyze failure correlation between stresses."
        ),
    )

    correlation_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Saved sample failure report JSON file.",
    )

    correlation_parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Optional failure correlation policy JSON file.",
    )

    correlation_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for correlation JSON.",
    )

    cluster_parser = subparsers.add_parser(
        "clusters",
        help="Analyze correlated failure clusters.",
    )

    cluster_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Saved sample failure report JSON file.",
    )

    cluster_parser.add_argument(
        "--minimum-correlation",
        type=float,
        default=0.75,
        help="Minimum correlation used to form clusters.",
    )

    cluster_parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Optional failure cluster policy JSON file.",
    )

    cluster_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for cluster JSON.",
    )

    progression_parser = subparsers.add_parser(
        "progression",
        help="Analyze failure-rate progression across model checkpoints.",
    )

    progression_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing model checkpoints and failure rates.",
    )

    progression_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="Maximum failure-rate change treated as stable.",
    )

    progression_parser.add_argument(
        "--max-regression",
        type=float,
        default=None,
        help="Optional maximum allowed overall failure-rate regression.",
    )

    progression_parser.add_argument(
        "--max-regressed-transitions",
        type=int,
        default=None,
        help="Optional maximum number of regressed transitions.",
    )

    progression_parser.add_argument(
        "--reject-volatile",
        action="store_true",
        help="Fail the policy when progression is volatile.",
    )

    progression_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for progression JSON.",
    )

    signature_parser = subparsers.add_parser(
        "signature",
        help="Analyze a model failure signature across stresses.",
    )

    signature_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing stress failure signals.",
    )

    signature_parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Optional baseline stress-signal JSON for comparison.",
    )

    signature_parser.add_argument(
        "--affected-threshold",
        type=float,
        default=0.10,
        help="Failure-rate threshold for an affected stress.",
    )

    signature_parser.add_argument(
        "--systemic-fraction",
        type=float,
        default=0.50,
        help="Affected-stress fraction classified as systemic.",
    )

    signature_parser.add_argument(
        "--instability-threshold",
        type=float,
        default=0.20,
        help="Mean prediction-flip rate classified as unstable.",
    )

    signature_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="Tolerance used when comparing failure signatures.",
    )

    signature_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for signature JSON.",
    )

    signature_history_parser = subparsers.add_parser(
        "signature-history",
        help="Analyze failure-signature evolution across model checkpoints.",
    )

    signature_history_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing labeled signature checkpoints.",
    )

    signature_history_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="Tolerance used when comparing adjacent signatures.",
    )

    signature_history_parser.add_argument(
        "--affected-threshold",
        type=float,
        default=0.10,
        help="Failure-rate threshold for an affected stress.",
    )

    signature_history_parser.add_argument(
        "--systemic-fraction",
        type=float,
        default=0.50,
        help="Affected-stress fraction classified as systemic.",
    )

    signature_history_parser.add_argument(
        "--instability-threshold",
        type=float,
        default=0.20,
        help="Mean prediction-flip rate classified as unstable.",
    )

    signature_history_parser.add_argument(
        "--max-regressed-transitions",
        type=int,
        default=None,
        help="Optional maximum number of regressed transitions.",
    )

    signature_history_parser.add_argument(
        "--max-severity-regressions",
        type=int,
        default=None,
        help="Optional maximum number of severity regressions.",
    )

    signature_history_parser.add_argument(
        "--max-dominant-stress-changes",
        type=int,
        default=None,
        help="Optional maximum number of dominant-stress changes.",
    )

    signature_history_parser.add_argument(
        "--reject-volatile",
        action="store_true",
        help="Fail the policy when signature history is volatile.",
    )

    signature_history_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for signature-history JSON.",
    )

    triage_parser = subparsers.add_parser(
        "triage",
        help="Prioritize detected failure patterns for remediation.",
    )

    triage_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing failure-priority signals.",
    )

    triage_parser.add_argument(
        "--max-critical",
        type=int,
        default=None,
        help="Optional maximum number of critical failures.",
    )

    triage_parser.add_argument(
        "--max-high",
        type=int,
        default=None,
        help="Optional maximum number of high-priority failures.",
    )

    triage_parser.add_argument(
        "--max-actionable",
        type=int,
        default=None,
        help="Optional maximum number of actionable failures.",
    )

    triage_parser.add_argument(
        "--max-priority-score",
        type=float,
        default=None,
        help="Optional maximum allowed highest priority score.",
    )

    triage_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for triage JSON.",
    )

    triage_compare_parser = subparsers.add_parser(
        "triage-compare",
        help="Compare failure triage between baseline and candidate models.",
    )

    triage_compare_parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Baseline failure-priority signal JSON file.",
    )

    triage_compare_parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="Candidate failure-priority signal JSON file.",
    )

    triage_compare_parser.add_argument(
        "--score-tolerance",
        type=float,
        default=0.0,
        help="Priority-score increase treated as stable.",
    )

    triage_compare_parser.add_argument(
        "--allow-regression",
        action="store_true",
        help="Allow an overall triage regression.",
    )

    triage_compare_parser.add_argument(
        "--max-actionable-increase",
        type=int,
        default=None,
        help="Optional maximum actionable-failure increase.",
    )

    triage_compare_parser.add_argument(
        "--max-critical-increase",
        type=int,
        default=None,
        help="Optional maximum critical-failure increase.",
    )

    triage_compare_parser.add_argument(
        "--max-score-increase",
        type=float,
        default=None,
        help="Optional maximum highest-priority-score increase.",
    )

    triage_compare_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for triage-comparison JSON.",
    )

    persistence_parser = subparsers.add_parser(
        "persistence",
        help="Analyze recurring failures across model checkpoints.",
    )

    persistence_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing failure occurrences.",
    )

    persistence_parser.add_argument(
        "--max-persistent",
        type=int,
        default=None,
        help="Optional maximum number of persistent failures.",
    )

    persistence_parser.add_argument(
        "--max-recurring",
        type=int,
        default=None,
        help="Optional maximum number of recurring failures.",
    )

    persistence_parser.add_argument(
        "--max-unresolved",
        type=int,
        default=None,
        help="Optional maximum number of unresolved failures.",
    )

    persistence_parser.add_argument(
        "--max-recurrence-rate",
        type=float,
        default=None,
        help="Optional maximum allowed recurrence rate.",
    )

    persistence_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for persistence JSON.",
    )

    resolution_parser = subparsers.add_parser(
        "resolution",
        help="Analyze whether recurring failures improve or worsen.",
    )

    resolution_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing failure occurrences.",
    )

    resolution_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="Maximum score change treated as unchanged.",
    )

    resolution_parser.add_argument(
        "--max-worsening",
        type=int,
        default=None,
        help="Optional maximum number of worsening failures.",
    )

    resolution_parser.add_argument(
        "--max-unchanged",
        type=int,
        default=None,
        help="Optional maximum number of unchanged failures.",
    )

    resolution_parser.add_argument(
        "--max-unresolved",
        type=int,
        default=None,
        help="Optional maximum number of unresolved failures.",
    )

    resolution_parser.add_argument(
        "--max-score-regression",
        type=float,
        default=None,
        help="Optional maximum allowed failure-score regression.",
    )

    resolution_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for resolution JSON.",
    )


    forecast_parser = subparsers.add_parser(
        "forecast",
        help="Forecast failure trajectories from checkpoint history.",
    )

    forecast_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="JSON file containing failure occurrences.",
    )

    forecast_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="Maximum average score change treated as stable.",
    )

    forecast_parser.add_argument(
        "--max-worsening",
        type=int,
        default=None,
        help="Optional maximum number of worsening forecasts.",
    )

    forecast_parser.add_argument(
        "--max-projected-risk",
        type=int,
        default=None,
        help="Optional maximum number of projected-risk failures.",
    )

    forecast_parser.add_argument(
        "--max-projected-score",
        type=float,
        default=None,
        help="Optional maximum allowed projected failure score.",
    )

    forecast_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for forecast JSON.",
    )


    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Load and inspect a complete FailureLab evaluation profile.",
    )

    evaluate_parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to a FailureLab evaluation-profile JSON file.",
    )

    evaluate_parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for the evaluation-plan JSON report.",
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
        loaded_class_policy = load_class_policy(
            class_policy_path
        )

        (
            default_class_policy,
            class_policies,
        ) = loaded_class_policy

        minimum_class_coverage = (
            loaded_class_policy.minimum_class_coverage
        )
    else:
        default_class_policy = None
        class_policies = None
        minimum_class_coverage = None

    report = build_policy_report(
        result,
        policy,
        default_class_policy=default_class_policy,
        class_policies=class_policies,
        minimum_class_coverage=minimum_class_coverage,
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

        print(
            f"Class coverage: "
            f"{report.class_evaluation.class_coverage:.2%}"
        )

        if (
            report.class_evaluation.minimum_class_coverage
            is not None
        ):
            print(
                f"Required coverage: "
                f"{report.class_evaluation.minimum_class_coverage:.2%}"
            )

    for violation in report.evaluation.violations:
        print(
            f"- {violation.stress_name}: "
            f"{violation.metric} "
            f"{violation.observed:.2%} "
            f"> {violation.allowed:.2%}"
        )

    for warning in report.evaluation.warnings:
        print(
            f"- WARNING {warning.stress_name}: "
            f"{warning.metric} "
            f"{warning.observed:.2%} "
            f"> {warning.allowed:.2%}"
        )

    for warning in report.class_evaluation.warnings:
        print(
            f"- WARNING class {warning.class_index}: "
            f"{warning.metric} "
            f"{warning.observed:.2%} "
            f"> {warning.allowed:.2%}"
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

    if report.has_warnings:
        print(
            "RESULT: PASSED WITH WARNINGS"
        )
    else:
        print(
            "RESULT: PASSED"
        )

    return 0

def run_cross_stress(
    result_path: Path,
    policy_path: Path | None = None,
    output_path: Path | None = None,
) -> int:
    from failurelab.suite_runner import SuiteResult

    result = SuiteResult.load_json(
        result_path
    )

    report = build_cross_stress_report(
        result
    )

    print(
        f"Suite: {report.suite_name}"
    )

    print(
        f"Classes analyzed: {report.class_count}"
    )

    print(
        f"Systemic: {report.systemic_count}"
    )

    print(
        f"Localized: {report.localized_count}"
    )

    print(
        f"Stable: {report.stable_count}"
    )

    for row in report.classes:
        print(
            f"- class {row.class_index}: "
            f"{row.severity} "
            f"(failure frequency "
            f"{row.failure_frequency:.2%}, "
            f"worst stress {row.worst_stress})"
        )

    if output_path is not None:
        report.save_json(
            output_path
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy_path is None:
        return 0

    policy = load_cross_stress_policy(
        policy_path
    )

    evaluation = evaluate_cross_stress_policy(
        report,
        policy,
    )

    for violation in evaluation.violations:
        if violation.metric == "systemic_fraction":
            observed = f"{violation.observed:.2%}"
            allowed = f"{violation.allowed:.2%}"
        else:
            observed = f"{violation.observed:g}"
            allowed = f"{violation.allowed:g}"

        print(
            f"- {violation.metric}: "
            f"{observed} > {allowed}"
        )

    print()

    if not evaluation.passed:
        print(
            "RESULT: FAILED"
        )
        return 1

    print(
        "RESULT: PASSED"
    )

    return 0

def run_sample_report(
    input_path: Path,
    policy_path: Path | None = None,
) -> int:
    report = SampleFailureReport.load_json(
        input_path
    )

    print(
        f"Suite: {report.suite_name}"
    )

    print(
        f"Samples analyzed: {report.sample_count}"
    )

    print(
        f"Systemic: {report.systemic_count}"
    )

    print(
        f"Localized: {report.localized_count}"
    )

    print(
        f"Stable: {report.stable_count}"
    )

    for row in report.samples:
        print(
            f"- sample {row.sample_index}: "
            f"{row.severity} "
            f"(failure frequency "
            f"{row.failure_frequency:.2%})"
        )

    if policy_path is None:
        return 0

    policy = load_sample_failure_policy(
        policy_path
    )

    evaluation = evaluate_sample_failure_policy(
        report,
        policy,
    )

    for violation in evaluation.violations:
        if violation.metric == "systemic_fraction":
            observed = f"{violation.observed:.2%}"
            allowed = f"{violation.allowed:.2%}"
        else:
            observed = f"{violation.observed:g}"
            allowed = f"{violation.allowed:g}"

        print(
            f"- {violation.metric}: "
            f"{observed} > {allowed}"
        )

    print()

    if not evaluation.passed:
        print(
            "RESULT: FAILED"
        )
        return 1

    print(
        "RESULT: PASSED"
    )

    return 0

def run_correlation(
    input_path: Path,
    policy_path: Path | None = None,
    output_path: Path | None = None,
) -> int:
    report = SampleFailureReport.load_json(
        input_path
    )

    correlation_report = (
        build_failure_correlation_report(
            report
        )
    )

    print(
        f"Suite: {correlation_report.suite_name}"
    )

    print(
        f"Stress pairs: {correlation_report.pair_count}"
    )

    strongest = correlation_report.strongest_pair

    if strongest is not None:
        print(
            f"Strongest pair: "
            f"{strongest.stress_a} + "
            f"{strongest.stress_b} "
            f"({strongest.correlation:.2%})"
        )

    for row in correlation_report.correlations:
        print(
            f"- {row.stress_a} + {row.stress_b}: "
            f"{row.correlation:.2%} "
            f"({row.shared_failures} shared failures)"
        )

    if output_path is not None:
        correlation_report.save_json(
            output_path
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy_path is None:
        return 0

    policy = load_failure_correlation_policy(
        policy_path
    )

    evaluation = evaluate_failure_correlation_policy(
        correlation_report,
        policy,
    )

    for violation in evaluation.violations:
        if violation.metric == "maximum_correlation":
            observed = f"{violation.observed:.2%}"
            allowed = f"{violation.allowed:.2%}"
        else:
            observed = f"{violation.observed:g}"
            allowed = f"{violation.allowed:g}"

        print(
            f"- {violation.metric}: "
            f"{observed} > {allowed}"
        )

    print()

    if not evaluation.passed:
        print(
            "RESULT: FAILED"
        )
        return 1

    print(
        "RESULT: PASSED"
    )

    return 0

def run_clusters(
    input_path: Path,
    minimum_correlation: float = 0.75,
    policy_path: Path | None = None,
    output_path: Path | None = None,
) -> int:
    sample_report = SampleFailureReport.load_json(
        input_path
    )

    correlation_report = (
        build_failure_correlation_report(
            sample_report
        )
    )

    cluster_report = build_failure_cluster_report(
        correlation_report,
        minimum_correlation=minimum_correlation,
    )

    print(
        f"Suite: {cluster_report.suite_name}"
    )

    print(
        f"Clusters: {cluster_report.cluster_count}"
    )

    largest = cluster_report.largest_cluster

    if largest is not None:
        print(
            f"Largest cluster: "
            f"{len(largest.stresses)} stresses"
        )

    for index, cluster in enumerate(
        cluster_report.clusters,
        start=1,
    ):
        print(
            f"- cluster {index}: "
            f"{', '.join(cluster.stresses)} "
            f"({cluster.mean_correlation:.2%})"
        )

    if output_path is not None:
        cluster_report.save_json(
            output_path
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy_path is None:
        return 0

    policy = load_failure_cluster_policy(
        policy_path
    )

    evaluation = evaluate_failure_cluster_policy(
        cluster_report,
        policy,
    )

    for violation in evaluation.violations:
        print(
            f"- {violation.metric}: "
            f"{violation.observed:g} > "
            f"{violation.allowed:g}"
        )

    print()

    if not evaluation.passed:
        print("RESULT: FAILED")
        return 1

    print("RESULT: PASSED")
    return 0


def run_progression(
    input_path: Path,
    tolerance: float = 0.0,
    max_regression: float | None = None,
    max_regressed_transitions: int | None = None,
    reject_volatile: bool = False,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Progression input must be a JSON list."
        )

    points = [
        ProgressionPoint(
            label=row["label"],
            failure_rate=float(
                row["failure_rate"]
            ),
        )
        for row in data
    ]

    report = summarize_progression_history(
        points,
        tolerance=tolerance,
    )

    print(
        f"Overall status: {report.overall_status}"
    )
    print(
        f"Trend: {report.trend}"
    )
    print(
        f"Overall delta: {report.overall_delta:.2%}"
    )
    print(
        f"Improved transitions: {report.improved_count}"
    )
    print(
        f"Stable transitions: {report.stable_count}"
    )
    print(
        f"Regressed transitions: {report.regressed_count}"
    )

    highest_risk = highest_risk_checkpoint(
        points
    )

    print(
        f"Highest-risk checkpoint: "
        f"{highest_risk.label} "
        f"({highest_risk.risk_score:.2%})"
    )

    policy = None

    if (
        max_regression is not None
        or max_regressed_transitions is not None
        or reject_volatile
    ):
        policy = evaluate_progression_policy(
            report,
            max_overall_regression=(
                max_regression
                if max_regression is not None
                else float("inf")
            ),
            max_regressed_transitions=(
                max_regressed_transitions
                if max_regressed_transitions is not None
                else len(report.transitions)
            ),
            allow_volatile=not reject_volatile,
        )

        for violation in policy.violations:
            print(
                f"- {violation}"
            )

    risks = score_checkpoint_risk(
        points
    )

    if output_path is not None:
        export_progression_json(
            report,
            output_path,
            policy=policy,
            risks=risks,
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy is not None and not policy.passed:
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

def run_signature(
    input_path: Path,
    baseline_path: Path | None = None,
    affected_threshold: float = 0.10,
    systemic_fraction: float = 0.50,
    instability_threshold: float = 0.20,
    tolerance: float = 0.0,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Signature input must be a JSON list."
        )

    signals = [
        StressFailureSignal(
            stress_name=row["stress_name"],
            failure_rate=float(
                row["failure_rate"]
            ),
            prediction_flip_rate=float(
                row["prediction_flip_rate"]
            ),
        )
        for row in data
    ]

    signature = build_failure_signature(
        signals,
        affected_threshold=affected_threshold,
        systemic_fraction=systemic_fraction,
        instability_threshold=instability_threshold,
    )

    diagnostic_report = build_failure_diagnostic_report(
        signature
    )

    print(
        f"Signature type: {signature.signature_type}"
    )
    print(
        f"Dominant stress: {signature.dominant_stress}"
    )
    print(
        f"Dominant failure rate: "
        f"{signature.dominant_failure_rate:.2%}"
    )
    print(
        f"Mean failure rate: "
        f"{signature.mean_failure_rate:.2%}"
    )
    print(
        f"Mean flip rate: "
        f"{signature.mean_flip_rate:.2%}"
    )
    print(
        f"Affected stresses: "
        f"{len(signature.affected_stresses)}"
    )

    print()
    print(
        diagnostic_report.diagnosis.diagnosis
    )

    comparison = None

    if baseline_path is not None:
        baseline_data = json.loads(
            baseline_path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(
            baseline_data,
            list,
        ):
            raise ValueError(
                "Baseline signature input must be a JSON list."
            )

        baseline_signals = [
            StressFailureSignal(
                stress_name=row["stress_name"],
                failure_rate=float(
                    row["failure_rate"]
                ),
                prediction_flip_rate=float(
                    row["prediction_flip_rate"]
                ),
            )
            for row in baseline_data
        ]

        baseline_signature = build_failure_signature(
            baseline_signals,
            affected_threshold=affected_threshold,
            systemic_fraction=systemic_fraction,
            instability_threshold=instability_threshold,
        )

        comparison = compare_failure_signatures(
            baseline_signature,
            signature,
            tolerance=tolerance,
        )

        print()
        print(
            f"Comparison status: {comparison.status}"
        )
        print(
            f"Mean failure-rate delta: "
            f"{comparison.mean_failure_rate_delta:.2%}"
        )
        print(
            f"Mean flip-rate delta: "
            f"{comparison.mean_flip_rate_delta:.2%}"
        )

    if output_path is not None:
        export_signature_json(
            signature,
            output_path,
            diagnostic_report=diagnostic_report,
            comparison=comparison,
        )

        print(
            f"Report saved to {output_path}"
        )

    print()
    print(
        "RESULT: PASSED"
    )

    return 0


def run_signature_history(
    input_path: Path,
    tolerance: float = 0.0,
    affected_threshold: float = 0.10,
    systemic_fraction: float = 0.50,
    instability_threshold: float = 0.20,
    max_regressed_transitions: int | None = None,
    max_severity_regressions: int | None = None,
    max_dominant_stress_changes: int | None = None,
    reject_volatile: bool = False,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Signature history input must be a JSON list."
        )

    checkpoints = []

    for row in data:
        label = row["label"]
        signal_rows = row.get(
            "signals",
            row.get("signature"),
        )

        if not isinstance(signal_rows, list):
            raise ValueError(
                "Each signature history checkpoint must contain "
                "a 'signals' list."
            )

        signals = [
            StressFailureSignal(
                stress_name=signal["stress_name"],
                failure_rate=float(
                    signal["failure_rate"]
                ),
                prediction_flip_rate=float(
                    signal["prediction_flip_rate"]
                ),
            )
            for signal in signal_rows
        ]

        signature = build_failure_signature(
            signals,
            affected_threshold=affected_threshold,
            systemic_fraction=systemic_fraction,
            instability_threshold=instability_threshold,
        )

        checkpoints.append(
            SignatureCheckpoint(
                label=label,
                signature=signature,
            )
        )

    report = analyze_signature_history(
        checkpoints,
        tolerance=tolerance,
    )

    print(
        f"Trend: {report.trend}"
    )
    print(
        f"Checkpoints: {len(report.checkpoints)}"
    )
    print(
        f"Improved transitions: {report.improved_transitions}"
    )
    print(
        f"Stable transitions: {report.stable_transitions}"
    )
    print(
        f"Regressed transitions: {report.regressed_transitions}"
    )
    print(
        f"Severity regressions: {report.severity_regressions}"
    )
    print(
        f"Dominant stress changes: {report.dominant_stress_changes}"
    )

    policy = None

    if (
        max_regressed_transitions is not None
        or max_severity_regressions is not None
        or max_dominant_stress_changes is not None
        or reject_volatile
    ):
        policy = evaluate_signature_history_policy(
            report,
            max_regressed_transitions=(
                max_regressed_transitions
                if max_regressed_transitions is not None
                else len(report.transitions)
            ),
            max_severity_regressions=(
                max_severity_regressions
                if max_severity_regressions is not None
                else len(report.transitions)
            ),
            max_dominant_stress_changes=(
                max_dominant_stress_changes
            ),
            allow_volatile=not reject_volatile,
        )

        for violation in policy.violations:
            print(
                f"- {violation}"
            )

    if output_path is not None:
        export_signature_history_json(
            report,
            output_path,
            policy=policy,
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy is not None and not policy.passed:
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


def run_triage(
    input_path: Path,
    max_critical: int | None = None,
    max_high: int | None = None,
    max_actionable: int | None = None,
    max_priority_score: float | None = None,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Triage input must be a JSON list."
        )

    signals = [
        FailurePrioritySignal(
            name=row["name"],
            failure_rate=float(row["failure_rate"]),
            prediction_flip_rate=float(row["prediction_flip_rate"]),
            affected_fraction=float(row["affected_fraction"]),
            severity_weight=float(row.get("severity_weight", 1.0)),
        )
        for row in data
    ]

    report = build_failure_triage_report(signals)

    print(f"Failures: {report.total_failures}")
    print(f"Actionable: {report.actionable_count}")
    print(f"Critical: {report.critical_count}")
    print(f"High: {report.high_count}")
    print(f"Medium: {report.medium_count}")
    print(f"Low: {report.low_count}")

    if report.highest_priority is not None:
        print(
            f"Highest priority: {report.highest_priority.name} "
            f"({report.highest_priority.score:.2%}, "
            f"{report.highest_priority.level})"
        )

    policy = None
    if (
        max_critical is not None
        or max_high is not None
        or max_actionable is not None
        or max_priority_score is not None
    ):
        policy = evaluate_failure_triage_policy(
            report,
            max_critical=(
                max_critical
                if max_critical is not None
                else report.critical_count
            ),
            max_high=max_high,
            max_actionable=max_actionable,
            max_priority_score=max_priority_score,
        )

        for violation in policy.violations:
            print(f"- {violation}")

    if output_path is not None:
        export_failure_triage_json(
            report,
            output_path,
            policy=policy,
        )
        print(f"Report saved to {output_path}")

    if policy is not None and not policy.passed:
        print()
        print("RESULT: FAILED")
        return 1

    print()
    print("RESULT: PASSED")
    return 0


def _load_triage_report(
    path: Path,
):
    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Triage comparison input must be a JSON list."
        )

    signals = [
        FailurePrioritySignal(
            name=row["name"],
            failure_rate=float(
                row["failure_rate"]
            ),
            prediction_flip_rate=float(
                row["prediction_flip_rate"]
            ),
            affected_fraction=float(
                row["affected_fraction"]
            ),
            severity_weight=float(
                row.get(
                    "severity_weight",
                    1.0,
                )
            ),
        )
        for row in data
    ]

    return build_failure_triage_report(
        signals
    )


def run_triage_compare(
    baseline_path: Path,
    candidate_path: Path,
    score_tolerance: float = 0.0,
    allow_regression: bool = False,
    max_actionable_increase: int | None = None,
    max_critical_increase: int | None = None,
    max_score_increase: float | None = None,
    output_path: Path | None = None,
) -> int:
    baseline = _load_triage_report(
        baseline_path
    )
    candidate = _load_triage_report(
        candidate_path
    )

    comparison = compare_failure_triage(
        baseline,
        candidate,
        score_tolerance=score_tolerance,
    )

    print(
        f"Status: {comparison.status}"
    )
    print(
        f"Actionable: "
        f"{comparison.baseline_actionable} -> "
        f"{comparison.candidate_actionable} "
        f"({comparison.actionable_delta:+d})"
    )
    print(
        f"Critical: "
        f"{comparison.baseline_critical} -> "
        f"{comparison.candidate_critical} "
        f"({comparison.critical_delta:+d})"
    )
    print(
        f"Highest priority score: "
        f"{comparison.baseline_highest_score:.2%} -> "
        f"{comparison.candidate_highest_score:.2%} "
        f"({comparison.highest_score_delta:+.2%})"
    )

    policy = evaluate_triage_comparison_policy(
        comparison,
        allow_regression=allow_regression,
        max_actionable_increase=max_actionable_increase,
        max_critical_increase=max_critical_increase,
        max_score_increase=max_score_increase,
    )

    for violation in policy.violations:
        print(
            f"- {violation}"
        )

    if output_path is not None:
        export_triage_comparison_json(
            comparison,
            output_path,
            policy=policy,
        )

        print(
            f"Report saved to {output_path}"
        )

    if not policy.passed:
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


def run_persistence(
    input_path: Path,
    max_persistent: int | None = None,
    max_recurring: int | None = None,
    max_unresolved: int | None = None,
    max_recurrence_rate: float | None = None,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Persistence input must be a JSON list."
        )

    occurrences = [
        FailureOccurrence(
            checkpoint=row["checkpoint"],
            failure_name=row["failure_name"],
            priority_score=float(
                row["priority_score"]
            ),
        )
        for row in data
    ]

    report = build_failure_persistence_report(
        occurrences
    )

    print(
        f"Failures: {report.total_failures}"
    )
    print(
        f"Persistent: {report.persistent_count}"
    )
    print(
        f"Recurring: {report.recurring_count}"
    )
    print(
        f"Isolated: {report.isolated_count}"
    )
    print(
        f"Unresolved: {report.unresolved_count}"
    )

    if report.highest_persistence is not None:
        print(
            f"Highest persistence: "
            f"{report.highest_persistence.failure_name} "
            f"({report.highest_persistence.recurrence_rate:.2%}, "
            f"{report.highest_persistence.level})"
        )

    policy = None

    if (
        max_persistent is not None
        or max_recurring is not None
        or max_unresolved is not None
        or max_recurrence_rate is not None
    ):
        policy = evaluate_failure_persistence_policy(
            report,
            max_persistent=max_persistent,
            max_recurring=max_recurring,
            max_unresolved=max_unresolved,
            max_recurrence_rate=max_recurrence_rate,
        )

        for violation in policy.violations:
            print(
                f"- {violation}"
            )

    if output_path is not None:
        export_failure_persistence_json(
            report,
            output_path,
            policy=policy,
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy is not None and not policy.passed:
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



def run_resolution(
    input_path: Path,
    tolerance: float = 0.0,
    max_worsening: int | None = None,
    max_unchanged: int | None = None,
    max_unresolved: int | None = None,
    max_score_regression: float | None = None,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Resolution input must be a JSON list."
        )

    occurrences = [
        FailureOccurrence(
            checkpoint=row["checkpoint"],
            failure_name=row["failure_name"],
            priority_score=float(
                row["priority_score"]
            ),
        )
        for row in data
    ]

    report = build_failure_resolution_report(
        occurrences,
        tolerance=tolerance,
    )

    print(
        f"Failures: {report.total_failures}"
    )
    print(
        f"Improving: {report.improving_count}"
    )
    print(
        f"Unchanged: {report.unchanged_count}"
    )
    print(
        f"Worsening: {report.worsening_count}"
    )
    print(
        f"Insufficient history: "
        f"{report.insufficient_history_count}"
    )
    print(
        f"Unresolved: {report.unresolved_count}"
    )

    if report.worst_resolution is not None:
        print(
            f"Worst resolution: "
            f"{report.worst_resolution.failure_name} "
            f"({report.worst_resolution.score_delta:+.2%})"
        )

    policy = None

    if (
        max_worsening is not None
        or max_unchanged is not None
        or max_unresolved is not None
        or max_score_regression is not None
    ):
        policy = evaluate_failure_resolution_policy(
            report,
            max_worsening=max_worsening,
            max_unchanged=max_unchanged,
            max_unresolved=max_unresolved,
            max_score_regression=max_score_regression,
        )

        for violation in policy.violations:
            print(
                f"- {violation}"
            )

    if output_path is not None:
        export_failure_resolution_json(
            report,
            output_path,
            policy=policy,
        )

        print(
            f"Report saved to {output_path}"
        )

    if policy is not None and not policy.passed:
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


def run_forecast(
    input_path: Path,
    tolerance: float = 0.0,
    max_worsening: int | None = None,
    max_projected_risk: int | None = None,
    max_projected_score: float | None = None,
    output_path: Path | None = None,
) -> int:
    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Forecast input must be a JSON list."
        )

    occurrences = [
        FailureOccurrence(
            checkpoint=row["checkpoint"],
            failure_name=row["failure_name"],
            priority_score=float(
                row["priority_score"]
            ),
        )
        for row in data
    ]

    report = build_failure_forecast_report(
        occurrences,
        tolerance=tolerance,
    )

    print(f"Failures: {report.total_failures}")
    print(f"Improving: {report.improving_count}")
    print(f"Stable: {report.stable_count}")
    print(f"Worsening: {report.worsening_count}")
    print(
        "Insufficient history: "
        f"{report.insufficient_history_count}"
    )
    print(
        f"Projected risk: {report.projected_risk_count}"
    )

    if report.highest_projected_risk is not None:
        highest = report.highest_projected_risk
        print(
            f"Highest projected risk: "
            f"{highest.failure_name} "
            f"({highest.projected_score:.2%})"
        )

    policy = None

    if (
        max_worsening is not None
        or max_projected_risk is not None
        or max_projected_score is not None
    ):
        policy = evaluate_failure_forecast_policy(
            report,
            max_worsening=max_worsening,
            max_projected_risk=max_projected_risk,
            max_projected_score=max_projected_score,
        )

        for violation in policy.violations:
            print(f"- {violation}")

    if output_path is not None:
        export_failure_forecast_json(
            report,
            output_path,
            policy=policy,
        )
        print(f"Report saved to {output_path}")

    if policy is not None and not policy.passed:
        print()
        print("RESULT: FAILED")
        return 1

    print()
    print("RESULT: PASSED")
    return 0




def run_evaluate(
    config_path: Path,
    output_path: Path | None = None,
) -> int:
    """Load, validate, and execute an evaluation profile."""

    profile = load_evaluation_profile(
        config_path
    )

    validation = validate_evaluation_profile(
        profile
    )

    if not validation.passed:
        for error in validation.errors:
            print(
                f"- {error}",
                file=sys.stderr,
            )
        return 1

    plan = build_evaluation_plan(
        profile
    )

    print(
        f"Evaluation profile: {plan.profile_name}"
    )
    print(
        f"Suite config: {plan.suite_config}"
    )
    print(
        f"Analyses: {plan.analysis_count}"
    )

    for analysis in plan.analyses:
        print(
            f"- {analysis}"
        )

    handlers = build_profile_handlers(
        profile,
        base_path=config_path.parent,
    )

    report = run_evaluation(
        profile,
        handlers,
    )

    print()

    for step in report.steps:
        status = (
            "PASSED"
            if step.passed
            else "FAILED"
        )

        if step.message:
            print(
                f"{step.analysis}: "
                f"{status} - {step.message}"
            )
        else:
            print(
                f"{step.analysis}: {status}"
            )

    if output_path is not None:
        export_evaluation_json(
            report,
            output_path,
        )
        print(
            f"Report saved to {output_path}"
        )

    print()

    if not report.passed:
        print(
            "RESULT: FAILED"
        )
        return 1

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

        if args.command == "cross-stress":
            return run_cross_stress(
                result_path=args.result,
                policy_path=args.policy,
                output_path=args.output,
            )

        if args.command == "sample-report":
            return run_sample_report(
                input_path=args.input,
                policy_path=args.policy,
            )

        if args.command == "correlation":
            return run_correlation(
                input_path=args.input,
                policy_path=args.policy,
                output_path=args.output,
            )

        if args.command == "clusters":
            return run_clusters(
                input_path=args.input,
                minimum_correlation=args.minimum_correlation,
                policy_path=args.policy,
                output_path=args.output,
            )

        if args.command == "progression":
            return run_progression(
                input_path=args.input,
                tolerance=args.tolerance,
                max_regression=args.max_regression,
                max_regressed_transitions=(
                    args.max_regressed_transitions
                ),
                reject_volatile=args.reject_volatile,
                output_path=args.output,
            )

        if args.command == "signature":
            return run_signature(
                input_path=args.input,
                baseline_path=args.baseline,
                affected_threshold=args.affected_threshold,
                systemic_fraction=args.systemic_fraction,
                instability_threshold=args.instability_threshold,
                tolerance=args.tolerance,
                output_path=args.output,
            )

        if args.command == "signature-history":
            return run_signature_history(
                input_path=args.input,
                tolerance=args.tolerance,
                affected_threshold=args.affected_threshold,
                systemic_fraction=args.systemic_fraction,
                instability_threshold=args.instability_threshold,
                max_regressed_transitions=args.max_regressed_transitions,
                max_severity_regressions=args.max_severity_regressions,
                max_dominant_stress_changes=(
                    args.max_dominant_stress_changes
                ),
                reject_volatile=args.reject_volatile,
                output_path=args.output,
            )

        if args.command == "triage":
            return run_triage(
                input_path=args.input,
                max_critical=args.max_critical,
                max_high=args.max_high,
                max_actionable=args.max_actionable,
                max_priority_score=args.max_priority_score,
                output_path=args.output,
            )

        if args.command == "triage-compare":
            return run_triage_compare(
                baseline_path=args.baseline,
                candidate_path=args.candidate,
                score_tolerance=args.score_tolerance,
                allow_regression=args.allow_regression,
                max_actionable_increase=(
                    args.max_actionable_increase
                ),
                max_critical_increase=(
                    args.max_critical_increase
                ),
                max_score_increase=args.max_score_increase,
                output_path=args.output,
            )

        if args.command == "persistence":
            return run_persistence(
                input_path=args.input,
                max_persistent=args.max_persistent,
                max_recurring=args.max_recurring,
                max_unresolved=args.max_unresolved,
                max_recurrence_rate=args.max_recurrence_rate,
                output_path=args.output,
            )

        if args.command == "resolution":
            return run_resolution(
                input_path=args.input,
                tolerance=args.tolerance,
                max_worsening=args.max_worsening,
                max_unchanged=args.max_unchanged,
                max_unresolved=args.max_unresolved,
                max_score_regression=args.max_score_regression,
                output_path=args.output,
            )


        if args.command == "evaluate":
            return run_evaluate(
                config_path=args.config,
                output_path=args.output,
            )

        if args.command == "forecast":
            return run_forecast(
                input_path=args.input,
                tolerance=args.tolerance,
                max_worsening=args.max_worsening,
                max_projected_risk=args.max_projected_risk,
                max_projected_score=args.max_projected_score,
                output_path=args.output,
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

    