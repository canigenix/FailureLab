from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class FailureOccurrence:
    """Occurrence of a named failure at one model checkpoint."""

    checkpoint: str
    failure_name: str
    priority_score: float

    def __post_init__(self):
        if not 0.0 <= self.priority_score <= 1.0:
            raise ValueError(
                "priority_score must be between 0.0 and 1.0."
            )


@dataclass(frozen=True)
class FailureRecurrence:
    """Recurrence summary for one failure pattern."""

    failure_name: str
    occurrence_count: int
    checkpoint_count: int
    recurrence_rate: float
    mean_priority_score: float
    max_priority_score: float
    checkpoints: tuple[str, ...]


def analyze_failure_recurrence(
    occurrences: Sequence[FailureOccurrence],
) -> list[FailureRecurrence]:
    """Analyze repeated failure patterns across checkpoints."""

    if not occurrences:
        return []

    checkpoint_names = {
        occurrence.checkpoint
        for occurrence in occurrences
    }

    checkpoint_count = len(
        checkpoint_names
    )

    grouped: dict[str, list[FailureOccurrence]] = {}

    for occurrence in occurrences:
        grouped.setdefault(
            occurrence.failure_name,
            [],
        ).append(
            occurrence
        )

    results = []

    for failure_name, rows in grouped.items():
        checkpoints = tuple(
            dict.fromkeys(
                row.checkpoint
                for row in rows
            )
        )

        occurrence_count = len(
            checkpoints
        )

        scores = [
            row.priority_score
            for row in rows
        ]

        results.append(
            FailureRecurrence(
                failure_name=failure_name,
                occurrence_count=occurrence_count,
                checkpoint_count=checkpoint_count,
                recurrence_rate=(
                    occurrence_count
                    / checkpoint_count
                ),
                mean_priority_score=(
                    sum(scores)
                    / len(scores)
                ),
                max_priority_score=max(
                    scores
                ),
                checkpoints=checkpoints,
            )
        )

    return sorted(
        results,
        key=lambda result: (
            result.recurrence_rate,
            result.mean_priority_score,
        ),
        reverse=True,
    )