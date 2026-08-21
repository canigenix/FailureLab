import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.failure_forecast_report import (
    build_failure_forecast_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def run_profile_forecast(
    profile: EvaluationProfile,
    *,
    base_path: Path | None = None,
    tolerance: float = 0.0,
) -> EvaluationStepResult:
    """Execute the forecast step for an evaluation profile."""

    if not profile.run_forecast:
        raise ValueError(
            "Forecast analysis is not enabled."
        )

    source_value = (
        profile.occurrence_input
        if profile.occurrence_input is not None
        else profile.forecast_input
    )

    if source_value is None:
        raise ValueError(
            "An occurrence input is required to execute forecast analysis."
        )

    input_path = Path(
        source_value
    )

    if (
        base_path is not None
        and not input_path.is_absolute()
    ):
        input_path = (
            base_path
            / input_path
        )

    data = json.loads(
        input_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Forecast input must be a JSON list."
        )

    occurrences = [
        FailureOccurrence(
            checkpoint=row["checkpoint"],
            failure_name=row["failure_name"],
            priority_score=float(
                row["priority_score"]
            ),
        )
        for row in data
    ]

    report = build_failure_forecast_report(
        occurrences,
        tolerance=tolerance,
    )

    message = (
        f"{report.total_failures} failures analyzed; "
        f"{report.worsening_count} worsening; "
        f"{report.projected_risk_count} projected risk."
    )

    return EvaluationStepResult(
        analysis="forecast",
        passed=True,
        message=message,
    )