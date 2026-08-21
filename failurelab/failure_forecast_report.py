from dataclasses import dataclass
from typing import Sequence

from failurelab.failure_forecast import (
    FailureForecast,
    forecast_failure_trajectory,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


@dataclass(frozen=True)
class FailureForecastReport:
    """Summary of projected failure trajectories."""

    forecasts: tuple[FailureForecast, ...]
    total_failures: int
    improving_count: int
    stable_count: int
    worsening_count: int
    insufficient_history_count: int
    highest_projected_risk: FailureForecast | None

    @property
    def projected_risk_count(self) -> int:
        return sum(
            forecast.projected_score >= 0.5
            for forecast in self.forecasts
        )


def build_failure_forecast_report(
    occurrences: Sequence[FailureOccurrence],
    *,
    tolerance: float = 0.0,
) -> FailureForecastReport:
    """Build a summary report from failure forecasts."""

    forecasts = tuple(
        forecast_failure_trajectory(
            occurrences,
            tolerance=tolerance,
        )
    )

    highest_projected_risk = (
        max(
            forecasts,
            key=lambda forecast: (
                forecast.projected_score
            ),
        )
        if forecasts
        else None
    )

    return FailureForecastReport(
        forecasts=forecasts,
        total_failures=len(forecasts),
        improving_count=sum(
            forecast.status == "improving"
            for forecast in forecasts
        ),
        stable_count=sum(
            forecast.status == "stable"
            for forecast in forecasts
        ),
        worsening_count=sum(
            forecast.status == "worsening"
            for forecast in forecasts
        ),
        insufficient_history_count=sum(
            forecast.status
            == "insufficient_history"
            for forecast in forecasts
        ),
        highest_projected_risk=(
            highest_projected_risk
        ),
    )