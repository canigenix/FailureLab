from dataclasses import dataclass
from typing import Literal, Sequence

from failurelab.failure_recurrence import (
    FailureRecurrence,
)


PersistenceLevel = Literal[
    "isolated",
    "recurring",
    "persistent",
]


@dataclass(frozen=True)
class FailurePersistence:
    """Persistence classification for a recurring failure."""

    failure_name: str
    level: PersistenceLevel
    recurrence_rate: float
    occurrence_count: int
    checkpoint_count: int
    mean_priority_score: float
    max_priority_score: float


def classify_persistence(
    recurrence_rate: float,
) -> PersistenceLevel:
    """Classify a failure by how often it recurs."""

    if not 0.0 <= recurrence_rate <= 1.0:
        raise ValueError(
            "recurrence_rate must be between 0.0 and 1.0."
        )

    if recurrence_rate >= 0.75:
        return "persistent"

    if recurrence_rate >= 0.40:
        return "recurring"

    return "isolated"


def analyze_failure_persistence(
    recurrences: Sequence[FailureRecurrence],
) -> list[FailurePersistence]:
    """Classify recurrence results by persistence."""

    results = []

    for recurrence in recurrences:
        results.append(
            FailurePersistence(
                failure_name=recurrence.failure_name,
                level=classify_persistence(
                    recurrence.recurrence_rate
                ),
                recurrence_rate=(
                    recurrence.recurrence_rate
                ),
                occurrence_count=(
                    recurrence.occurrence_count
                ),
                checkpoint_count=(
                    recurrence.checkpoint_count
                ),
                mean_priority_score=(
                    recurrence.mean_priority_score
                ),
                max_priority_score=(
                    recurrence.max_priority_score
                ),
            )
        )

    return results