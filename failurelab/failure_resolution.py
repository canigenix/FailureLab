from dataclasses import dataclass
from typing import Literal, Sequence

from failurelab.failure_recurrence import (
    FailureOccurrence,
)


ResolutionStatus = Literal[
    "improving",
    "unchanged",
    "worsening",
    "insufficient_history",
]


@dataclass(frozen=True)
class FailureResolution:
    """Resolution trend for one recurring failure."""

    failure_name: str
    first_score: float
    latest_score: float
    score_delta: float
    occurrence_count: int
    status: ResolutionStatus


def classify_resolution_status(
    first_score: float,
    latest_score: float,
    *,
    tolerance: float = 0.0,
) -> ResolutionStatus:
    """Classify whether a failure is improving or worsening."""

    if tolerance < 0.0:
        raise ValueError(
            "tolerance cannot be negative."
        )

    delta = latest_score - first_score

    if delta > tolerance:
        return "worsening"

    if delta < -tolerance:
        return "improving"

    return "unchanged"


def analyze_failure_resolution(
    occurrences: Sequence[FailureOccurrence],
    *,
    tolerance: float = 0.0,
) -> list[FailureResolution]:
    """Analyze resolution trends for recurring failures."""

    grouped: dict[
        str,
        list[FailureOccurrence],
    ] = {}

    for occurrence in occurrences:
        grouped.setdefault(
            occurrence.failure_name,
            [],
        ).append(
            occurrence
        )

    results = []

    for failure_name, rows in grouped.items():
        if len(rows) < 2:
            results.append(
                FailureResolution(
                    failure_name=failure_name,
                    first_score=rows[0].priority_score,
                    latest_score=rows[-1].priority_score,
                    score_delta=0.0,
                    occurrence_count=1,
                    status="insufficient_history",
                )
            )
            continue

        first_score = rows[0].priority_score
        latest_score = rows[-1].priority_score

        results.append(
            FailureResolution(
                failure_name=failure_name,
                first_score=first_score,
                latest_score=latest_score,
                score_delta=(
                    latest_score
                    - first_score
                ),
                occurrence_count=len(rows),
                status=classify_resolution_status(
                    first_score,
                    latest_score,
                    tolerance=tolerance,
                ),
            )
        )

    return results