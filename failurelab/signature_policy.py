from dataclasses import dataclass

from failurelab.signature_comparison import (
    FailureSignatureComparison,
)

SIGNATURE_SEVERITY = {
    "low-risk": 0,
    "localized": 1,
    "systemic": 2,
    "unstable": 3,
}


@dataclass(frozen=True)
class SignaturePolicyResult:
    """Result of evaluating a failure-signature comparison."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_signature_policy(
    comparison: FailureSignatureComparison,
    *,
    max_failure_rate_increase: float = 0.0,
    max_flip_rate_increase: float = 0.0,
    max_affected_stress_increase: int = 0,
    allow_dominant_stress_change: bool = True,
    allow_severity_regression: bool = False,
) -> SignaturePolicyResult:
    """Evaluate failure-signature changes against policy limits."""

    if max_failure_rate_increase < 0:
        raise ValueError(
            "max_failure_rate_increase must be greater than or equal to 0."
        )

    if max_flip_rate_increase < 0:
        raise ValueError(
            "max_flip_rate_increase must be greater than or equal to 0."
        )

    if max_affected_stress_increase < 0:
        raise ValueError(
            "max_affected_stress_increase must be greater than or equal to 0."
        )

    violations = []

    if (
        comparison.mean_failure_rate_delta
        > max_failure_rate_increase
    ):
        violations.append(
            "Mean failure-rate increase "
            f"{comparison.mean_failure_rate_delta:.4f} exceeds allowed "
            f"{max_failure_rate_increase:.4f}."
        )

    if (
        comparison.mean_flip_rate_delta
        > max_flip_rate_increase
    ):
        violations.append(
            "Mean prediction-flip-rate increase "
            f"{comparison.mean_flip_rate_delta:.4f} exceeds allowed "
            f"{max_flip_rate_increase:.4f}."
        )

    if (
        comparison.affected_stress_delta
        > max_affected_stress_increase
    ):
        violations.append(
            "Affected-stress increase "
            f"{comparison.affected_stress_delta} exceeds allowed "
            f"{max_affected_stress_increase}."
        )

    if (
        comparison.dominant_stress_changed
        and not allow_dominant_stress_change
    ):
        violations.append(
            "Dominant failure stress changed from "
            f"{comparison.baseline_dominant_stress} to "
            f"{comparison.candidate_dominant_stress}."
        )

    baseline_severity = SIGNATURE_SEVERITY[
        comparison.baseline_signature_type
    ]

    candidate_severity = SIGNATURE_SEVERITY[
        comparison.candidate_signature_type
    ]

    if (
        candidate_severity > baseline_severity
        and not allow_severity_regression
    ):
        violations.append(
            "Failure signature severity regressed from "
            f"{comparison.baseline_signature_type} to "
            f"{comparison.candidate_signature_type}."
        )

    return SignaturePolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )