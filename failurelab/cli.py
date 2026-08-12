from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .comparison import (
    BoundaryComparison,
    ModelComparison,
    RobustnessRegressionError,
)
from .policy import load_policy


def build_parser():
    parser = argparse.ArgumentParser(
        prog="failurelab",
        description=(
            "Stress-test machine-learning models "
            "and enforce robustness policies."
        ),
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
        help="Baseline comparison JSON file.",
    )

    compare_parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
        help="Candidate comparison JSON file.",
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

    missing = (
        required
        - set(data.keys())
    )

    if missing:
        missing_text = ", ".join(
            sorted(missing)
        )

        raise ValueError(
            f"Comparison file {path} is missing "
            f"required field(s): {missing_text}"
        )

    return data


def _build_comparison_from_snapshots(
    baseline_data: dict,
    candidate_data: dict,
    regression_tolerance: float = 0.02,
) -> ModelComparison:
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

        baseline_worst_drop = baseline[
            "worst_top1_drop"
        ]

        candidate_worst_drop = candidate[
            "worst_top1_drop"
        ]

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
            )

    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
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