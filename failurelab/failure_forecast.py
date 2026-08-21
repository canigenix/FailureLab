from dataclasses import dataclass
from typing import Literal, Sequence

from failurelab.failure_recurrence import (
    FailureOccurrence,
)


ForecastStatus = Literal[
    "improving",
    "stable",
    "worsening",
    "insufficient_history",
]


@dataclass(frozen=True)
class FailureForecast:
    """Forecast for one recurring failure."""

    failure_name: str
    observation_count: int
    latest_score: float
    average_change: float
    projected_score: float
    status: ForecastStatus


def classify_forecast_status(
    average_change: float,
    *,
    tolerance: float = 0.0,
) -> ForecastStatus:
    """Classify the direction of a failure forecast."""

    if tolerance < 0.0:
        raise ValueError(
            "tolerance cannot be negative."
        )

    if average_change > tolerance:
        return "worsening"

    if average_change < -tolerance:
        return "improving"

    return "stable"


def forecast_failure_trajectory(
    occurrences: Sequence[FailureOccurrence],
    *,
    tolerance: float = 0.0,
) -> list[FailureForecast]:
    """Project failure priority from recent checkpoint history."""

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

    forecasts = []

    for failure_name, rows in grouped.items():
        latest_score = rows[-1].priority_score

        if len(rows) < 2:
            forecasts.append(
                FailureForecast(
                    failure_name=failure_name,
                    observation_count=1,
                    latest_score=latest_score,
                    average_change=0.0,
                    projected_score=latest_score,
                    status="insufficient_history",
                )
            )
            continue

        changes = [
            current.priority_score
            - previous.priority_score
            for previous, current in zip(
                rows,
                rows[1:],
            )
        ]

        average_change = (
            sum(changes)
            / len(changes)
        )

        projected_score = min(
            max(
                latest_score
                + average_change,
                0.0,
            ),
            1.0,
        )

        forecasts.append(
            FailureForecast(
                failure_name=failure_name,
                observation_count=len(rows),
                latest_score=latest_score,
                average_change=average_change,
                projected_score=projected_score,
                status=classify_forecast_status(
                    average_change,
                    tolerance=tolerance,
                ),
            )
        )

    return forecasts