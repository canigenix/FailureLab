from dataclasses import dataclass
from typing import Sequence

from failurelab.progression import ProgressionPoint


@dataclass(frozen=True)
class CheckpointRisk:
    """Risk summary for one model checkpoint."""

    label: str
    failure_rate: float
    regression_from_previous: float | None
    risk_score: float


def score_checkpoint_risk(
    points: Sequence[ProgressionPoint],
) -> list[CheckpointRisk]:
    """Score checkpoints using failure rate and regression magnitude."""

    risks = []

    for index, point in enumerate(points):
        regression = None

        if index > 0:
            previous = points[index - 1]
            delta = point.failure_rate - previous.failure_rate
            regression = max(delta, 0.0)

        risk_score = point.failure_rate

        if regression is not None:
            risk_score += regression

        risks.append(
            CheckpointRisk(
                label=point.label,
                failure_rate=point.failure_rate,
                regression_from_previous=regression,
                risk_score=risk_score,
            )
        )

    return risks


def highest_risk_checkpoint(
    points: Sequence[ProgressionPoint],
) -> CheckpointRisk:
    """Return the checkpoint with the highest calculated risk."""

    if not points:
        raise ValueError(
            "At least one progression point is required."
        )

    risks = score_checkpoint_risk(points)

    return max(
        risks,
        key=lambda risk: risk.risk_score,
    )