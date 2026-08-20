from dataclasses import dataclass
from typing import Literal, Sequence

from failurelab.failure_signature import FailureSignature
from failurelab.signature_comparison import (
    FailureSignatureComparison,
    compare_failure_signatures,
)


SignatureHistoryTrend = Literal[
    "improving",
    "stable",
    "degrading",
    "volatile",
]


@dataclass(frozen=True)
class SignatureCheckpoint:
    """One model version and its failure signature."""

    label: str
    signature: FailureSignature


@dataclass(frozen=True)
class SignatureHistoryReport:
    """Summary of failure-signature evolution across model versions."""

    checkpoints: tuple[SignatureCheckpoint, ...]
    transitions: tuple[FailureSignatureComparison, ...]
    dominant_stress_changes: int
    severity_regressions: int
    improved_transitions: int
    stable_transitions: int
    regressed_transitions: int
    trend: SignatureHistoryTrend


_SIGNATURE_SEVERITY = {
    "low-risk": 0,
    "localized": 1,
    "systemic": 2,
    "unstable": 3,
}


def classify_signature_history_trend(
    transitions: Sequence[FailureSignatureComparison],
) -> SignatureHistoryTrend:
    """Classify the overall direction of signature evolution."""

    if not transitions:
        return "stable"

    improved = sum(
        transition.status == "improved"
        for transition in transitions
    )

    regressed = sum(
        transition.status == "regressed"
        for transition in transitions
    )

    if improved and regressed:
        return "volatile"

    if improved:
        return "improving"

    if regressed:
        return "degrading"

    return "stable"


def analyze_signature_history(
    checkpoints: Sequence[SignatureCheckpoint],
    *,
    tolerance: float = 0.0,
) -> SignatureHistoryReport:
    """Analyze how failure signatures evolve across model versions."""

    if len(checkpoints) < 2:
        raise ValueError(
            "At least two signature checkpoints are required."
        )

    transitions = [
        compare_failure_signatures(
            checkpoints[index].signature,
            checkpoints[index + 1].signature,
            tolerance=tolerance,
        )
        for index in range(len(checkpoints) - 1)
    ]

    dominant_stress_changes = sum(
        transition.dominant_stress_changed
        for transition in transitions
    )

    severity_regressions = sum(
        _SIGNATURE_SEVERITY[
            transition.candidate_signature_type
        ]
        > _SIGNATURE_SEVERITY[
            transition.baseline_signature_type
        ]
        for transition in transitions
    )

    improved_transitions = sum(
        transition.status == "improved"
        for transition in transitions
    )

    stable_transitions = sum(
        transition.status == "stable"
        for transition in transitions
    )

    regressed_transitions = sum(
        transition.status == "regressed"
        for transition in transitions
    )

    return SignatureHistoryReport(
        checkpoints=tuple(checkpoints),
        transitions=tuple(transitions),
        dominant_stress_changes=dominant_stress_changes,
        severity_regressions=severity_regressions,
        improved_transitions=improved_transitions,
        stable_transitions=stable_transitions,
        regressed_transitions=regressed_transitions,
        trend=classify_signature_history_trend(
            transitions
        ),
    )