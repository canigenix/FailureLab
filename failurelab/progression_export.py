import json
from pathlib import Path

from failurelab.progression import ProgressionHistoryReport
from failurelab.progression_policy import ProgressionPolicyResult
from failurelab.progression_risk import CheckpointRisk


def progression_report_to_dict(
    report: ProgressionHistoryReport,
) -> dict:
    """Convert a progression history report into a JSON-safe dictionary."""

    return {
        "points": [
            {
                "label": point.label,
                "failure_rate": point.failure_rate,
            }
            for point in report.points
        ],
        "transitions": [
            {
                "start": transition.start.label,
                "end": transition.end.label,
                "delta": transition.delta,
                "status": transition.status,
            }
            for transition in report.transitions
        ],
        "overall_delta": report.overall_delta,
        "overall_status": report.overall_status,
        "trend": report.trend,
        "improved_count": report.improved_count,
        "stable_count": report.stable_count,
        "regressed_count": report.regressed_count,
    }


def export_progression_json(
    report: ProgressionHistoryReport,
    path,
    *,
    policy: ProgressionPolicyResult | None = None,
    risks: list[CheckpointRisk] | None = None,
) -> Path:
    """Export progression analysis as JSON."""

    output_path = Path(path)

    data = progression_report_to_dict(report)

    if policy is not None:
        data["policy"] = {
            "passed": policy.passed,
            "violations": list(policy.violations),
        }

    if risks is not None:
        data["risks"] = [
            {
                "label": risk.label,
                "failure_rate": risk.failure_rate,
                "regression_from_previous": risk.regression_from_previous,
                "risk_score": risk.risk_score,
            }
            for risk in risks
        ]

    output_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return output_path