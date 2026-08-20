from dataclasses import dataclass
from typing import Literal

from failurelab.failure_signature import FailureSignature


SignatureComparisonStatus = Literal[
    "improved",
    "stable",
    "regressed",
]


@dataclass(frozen=True)
class FailureSignatureComparison:
    """Comparison between two model failure signatures."""

    baseline_dominant_stress: str
    candidate_dominant_stress: str
    dominant_stress_changed: bool
    mean_failure_rate_delta: float
    mean_flip_rate_delta: float
    affected_stress_delta: int
    baseline_signature_type: str
    candidate_signature_type: str
    status: SignatureComparisonStatus


def classify_signature_comparison(
    baseline: FailureSignature,
    candidate: FailureSignature,
    *,
    tolerance: float = 0.0,
) -> SignatureComparisonStatus:
    """Classify whether the candidate signature improved or regressed."""

    failure_delta = (
        candidate.mean_failure_rate
        - baseline.mean_failure_rate
    )

    flip_delta = (
        candidate.mean_flip_rate
        - baseline.mean_flip_rate
    )

    affected_delta = (
        len(candidate.affected_stresses)
        - len(baseline.affected_stresses)
    )

    regression_signals = (
        failure_delta > tolerance,
        flip_delta > tolerance,
        affected_delta > 0,
    )

    improvement_signals = (
        failure_delta < -tolerance,
        flip_delta < -tolerance,
        affected_delta < 0,
    )

    if any(regression_signals) and not any(improvement_signals):
        return "regressed"

    if any(improvement_signals) and not any(regression_signals):
        return "improved"

    return "stable"


def compare_failure_signatures(
    baseline: FailureSignature,
    candidate: FailureSignature,
    *,
    tolerance: float = 0.0,
) -> FailureSignatureComparison:
    """Compare failure signatures between model versions."""

    return FailureSignatureComparison(
        baseline_dominant_stress=baseline.dominant_stress,
        candidate_dominant_stress=candidate.dominant_stress,
        dominant_stress_changed=(
            baseline.dominant_stress
            != candidate.dominant_stress
        ),
        mean_failure_rate_delta=(
            candidate.mean_failure_rate
            - baseline.mean_failure_rate
        ),
        mean_flip_rate_delta=(
            candidate.mean_flip_rate
            - baseline.mean_flip_rate
        ),
        affected_stress_delta=(
            len(candidate.affected_stresses)
            - len(baseline.affected_stresses)
        ),
        baseline_signature_type=baseline.signature_type,
        candidate_signature_type=candidate.signature_type,
        status=classify_signature_comparison(
            baseline,
            candidate,
            tolerance=tolerance,
        ),
    )