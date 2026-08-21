from dataclasses import dataclass
from typing import Literal, Sequence


PriorityLevel = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


@dataclass(frozen=True)
class FailurePrioritySignal:
    """Failure characteristics used for prioritization."""

    name: str
    failure_rate: float
    prediction_flip_rate: float
    affected_fraction: float
    severity_weight: float = 1.0

    def __post_init__(self):
        for field_name in (
            "failure_rate",
            "prediction_flip_rate",
            "affected_fraction",
        ):
            value = getattr(self, field_name)

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be between 0.0 and 1.0."
                )

        if self.severity_weight < 0.0:
            raise ValueError(
                "severity_weight cannot be negative."
            )


@dataclass(frozen=True)
class FailurePriority:
    """Priority score for one detected failure pattern."""

    name: str
    score: float
    level: PriorityLevel
    failure_rate: float
    prediction_flip_rate: float
    affected_fraction: float


def classify_priority_level(
    score: float,
) -> PriorityLevel:
    """Convert a priority score into a severity level."""

    if score >= 0.75:
        return "critical"

    if score >= 0.50:
        return "high"

    if score >= 0.25:
        return "medium"

    return "low"


def calculate_priority_score(
    signal: FailurePrioritySignal,
) -> float:
    """Calculate a normalized failure-priority score."""

    base_score = (
        signal.failure_rate * 0.45
        + signal.prediction_flip_rate * 0.30
        + signal.affected_fraction * 0.25
    )

    weighted_score = (
        base_score
        * signal.severity_weight
    )

    return min(
        max(weighted_score, 0.0),
        1.0,
    )


def rank_failure_priorities(
    signals: Sequence[FailurePrioritySignal],
) -> list[FailurePriority]:
    """Rank failure patterns from highest to lowest priority."""

    priorities = []

    for signal in signals:
        score = calculate_priority_score(
            signal
        )

        priorities.append(
            FailurePriority(
                name=signal.name,
                score=score,
                level=classify_priority_level(
                    score
                ),
                failure_rate=signal.failure_rate,
                prediction_flip_rate=(
                    signal.prediction_flip_rate
                ),
                affected_fraction=(
                    signal.affected_fraction
                ),
            )
        )

    return sorted(
        priorities,
        key=lambda priority: priority.score,
        reverse=True,
    )