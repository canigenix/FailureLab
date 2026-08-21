from dataclasses import dataclass
from typing import Sequence

from failurelab.failure_priority import FailurePriority


@dataclass(frozen=True)
class FailureRemediation:
    """Recommended remediation for a prioritized failure."""

    name: str
    priority_level: str
    priority_score: float
    primary_driver: str
    recommendation: str


def identify_primary_driver(
    priority: FailurePriority,
) -> str:
    """Identify the strongest contributor to a failure priority."""

    drivers = {
        "failure_rate": priority.failure_rate * 0.45,
        "prediction_instability": (
            priority.prediction_flip_rate * 0.30
        ),
        "failure_breadth": (
            priority.affected_fraction * 0.25
        ),
    }

    return max(
        drivers,
        key=drivers.get,
    )


def remediation_for_driver(
    driver: str,
) -> str:
    """Return a remediation recommendation for a failure driver."""

    recommendations = {
        "failure_rate": (
            "Investigate the stress condition and improve "
            "robustness against repeated prediction failures."
        ),
        "prediction_instability": (
            "Investigate unstable predictions and improve "
            "prediction consistency under the stress condition."
        ),
        "failure_breadth": (
            "Investigate broad failure exposure across affected "
            "samples or classes."
        ),
    }

    if driver not in recommendations:
        raise ValueError(
            f"Unknown remediation driver: {driver}"
        )

    return recommendations[driver]


def build_failure_remediations(
    priorities: Sequence[FailurePriority],
) -> list[FailureRemediation]:
    """Build ordered remediation recommendations."""

    remediations = []

    for priority in priorities:
        driver = identify_primary_driver(
            priority
        )

        remediations.append(
            FailureRemediation(
                name=priority.name,
                priority_level=priority.level,
                priority_score=priority.score,
                primary_driver=driver,
                recommendation=remediation_for_driver(
                    driver
                ),
            )
        )

    return remediations