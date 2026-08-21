import json
from pathlib import Path

from failurelab.failure_remediation import (
    build_failure_remediations,
)
from failurelab.failure_triage import (
    FailureTriageReport,
)
from failurelab.failure_triage_policy import (
    FailureTriagePolicyResult,
)


def failure_triage_to_dict(
    report: FailureTriageReport,
) -> dict:
    """Convert a failure triage report into a JSON-safe dictionary."""

    remediations = build_failure_remediations(
        report.priorities
    )

    return {
        "total_failures": report.total_failures,
        "actionable_count": report.actionable_count,
        "critical_count": report.critical_count,
        "high_count": report.high_count,
        "medium_count": report.medium_count,
        "low_count": report.low_count,
        "highest_priority": (
            {
                "name": report.highest_priority.name,
                "score": report.highest_priority.score,
                "level": report.highest_priority.level,
            }
            if report.highest_priority is not None
            else None
        ),
        "priorities": [
            {
                "name": priority.name,
                "score": priority.score,
                "level": priority.level,
                "failure_rate": priority.failure_rate,
                "prediction_flip_rate": (
                    priority.prediction_flip_rate
                ),
                "affected_fraction": (
                    priority.affected_fraction
                ),
            }
            for priority in report.priorities
        ],
        "remediations": [
            {
                "name": remediation.name,
                "priority_level": (
                    remediation.priority_level
                ),
                "priority_score": (
                    remediation.priority_score
                ),
                "primary_driver": (
                    remediation.primary_driver
                ),
                "recommendation": (
                    remediation.recommendation
                ),
            }
            for remediation in remediations
        ],
    }


def export_failure_triage_json(
    report: FailureTriageReport,
    path,
    *,
    policy: FailureTriagePolicyResult | None = None,
) -> Path:
    """Export failure triage analysis as JSON."""

    output_path = Path(path)

    data = failure_triage_to_dict(
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