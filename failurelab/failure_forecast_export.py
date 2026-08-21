import json
from pathlib import Path

from failurelab.failure_forecast_policy import (
    FailureForecastPolicyResult,
)
from failurelab.failure_forecast_report import (
    FailureForecastReport,
)


def failure_forecast_to_dict(
    report: FailureForecastReport,
) -> dict:
    """Convert a forecast report into a JSON-safe dictionary."""

    return {
        "total_failures": report.total_failures,
        "improving_count": report.improving_count,
        "stable_count": report.stable_count,
        "worsening_count": report.worsening_count,
        "insufficient_history_count": (
            report.insufficient_history_count
        ),
        "projected_risk_count": (
            report.projected_risk_count
        ),
        "highest_projected_risk": (
            {
                "failure_name": (
                    report.highest_projected_risk.failure_name
                ),
                "observation_count": (
                    report.highest_projected_risk.observation_count
                ),
                "latest_score": (
                    report.highest_projected_risk.latest_score
                ),
                "average_change": (
                    report.highest_projected_risk.average_change
                ),
                "projected_score": (
                    report.highest_projected_risk.projected_score
                ),
                "status": (
                    report.highest_projected_risk.status
                ),
            }
            if report.highest_projected_risk is not None
            else None
        ),
        "forecasts": [
            {
                "failure_name": forecast.failure_name,
                "observation_count": forecast.observation_count,
                "latest_score": forecast.latest_score,
                "average_change": forecast.average_change,
                "projected_score": forecast.projected_score,
                "status": forecast.status,
            }
            for forecast in report.forecasts
        ],
    }


def export_failure_forecast_json(
    report: FailureForecastReport,
    path,
    *,
    policy: FailureForecastPolicyResult | None = None,
) -> Path:
    """Export failure forecast analysis as JSON."""

    output_path = Path(path)

    data = failure_forecast_to_dict(
        report
    )

    if policy is not None:
        data["policy"] = {
            "passed": policy.passed,
            "violations": list(
                policy.violations
            ),
        }

    output_path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path