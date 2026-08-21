from dataclasses import dataclass
from typing import Literal

from failurelab.failure_triage import (
    FailureTriageReport,
)


TriageComparisonStatus = Literal[
    "improved",
    "stable",
    "regressed",
]


@dataclass(frozen=True)
class FailureTriageComparison:
    """Comparison of failure triage between model versions."""

    baseline_actionable: int
    candidate_actionable: int
    actionable_delta: int

    baseline_critical: int
    candidate_critical: int
    critical_delta: int

    baseline_highest_score: float
    candidate_highest_score: float
    highest_score_delta: float

    status: TriageComparisonStatus


def _highest_score(
    report: FailureTriageReport,
) -> float:
    if report.highest_priority is None:
        return 0.0

    return report.highest_priority.score


def compare_failure_triage(
    baseline: FailureTriageReport,
    candidate: FailureTriageReport,
    *,
    score_tolerance: float = 0.0,
) -> FailureTriageComparison:
    """Compare failure-triage burden between model versions."""

    if score_tolerance < 0.0:
        raise ValueError(
            "score_tolerance cannot be negative."
        )

    baseline_score = _highest_score(
        baseline
    )
    candidate_score = _highest_score(
        candidate
    )

    actionable_delta = (
        candidate.actionable_count
        - baseline.actionable_count
    )

    critical_delta = (
        candidate.critical_count
        - baseline.critical_count
    )

    score_delta = (
        candidate_score
        - baseline_score
    )

    regressed = (
        actionable_delta > 0
        or critical_delta > 0
        or score_delta > score_tolerance
    )

    improved = (
        actionable_delta < 0
        or critical_delta < 0
        or score_delta < -score_tolerance
    )

    if regressed:
        status = "regressed"
    elif improved:
        status = "improved"
    else:
        status = "stable"

    return FailureTriageComparison(
        baseline_actionable=(
            baseline.actionable_count
        ),
        candidate_actionable=(
            candidate.actionable_count
        ),
        actionable_delta=actionable_delta,
        baseline_critical=(
            baseline.critical_count
        ),
        candidate_critical=(
            candidate.critical_count
        ),
        critical_delta=critical_delta,
        baseline_highest_score=baseline_score,
        candidate_highest_score=candidate_score,
        highest_score_delta=score_delta,
        status=status,
    )