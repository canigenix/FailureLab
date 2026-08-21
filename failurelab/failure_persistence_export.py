import json
from pathlib import Path

from failurelab.failure_persistence_policy import (
    FailurePersistencePolicyResult,
)
from failurelab.failure_persistence_report import (
    FailurePersistenceReport,
)


def failure_persistence_to_dict(
    report: FailurePersistenceReport,
) -> dict:
    """Convert a persistence report into a JSON-safe dictionary."""

    return {
        "total_failures": report.total_failures,
        "persistent_count": report.persistent_count,
        "recurring_count": report.recurring_count,
        "isolated_count": report.isolated_count,
        "unresolved_count": report.unresolved_count,
        "highest_persistence": (
            {
                "failure_name": (
                    report.highest_persistence.failure_name
                ),
                "level": (
                    report.highest_persistence.level
                ),
                "recurrence_rate": (
                    report.highest_persistence.recurrence_rate
                ),
                "occurrence_count": (
                    report.highest_persistence.occurrence_count
                ),
                "checkpoint_count": (
                    report.highest_persistence.checkpoint_count
                ),
                "mean_priority_score": (
                    report.highest_persistence.mean_priority_score
                ),
                "max_priority_score": (
                    report.highest_persistence.max_priority_score
                ),
            }
            if report.highest_persistence is not None
            else None
        ),
        "failures": [
            {
                "failure_name": failure.failure_name,
                "level": failure.level,
                "recurrence_rate": failure.recurrence_rate,
                "occurrence_count": failure.occurrence_count,
                "checkpoint_count": failure.checkpoint_count,
                "mean_priority_score": (
                    failure.mean_priority_score
                ),
                "max_priority_score": (
                    failure.max_priority_score
                ),
            }
            for failure in report.failures
        ],
    }


def export_failure_persistence_json(
    report: FailurePersistenceReport,
    path,
    *,
    policy: FailurePersistencePolicyResult | None = None,
) -> Path:
    """Export failure persistence analysis as JSON."""

    output_path = Path(path)

    data = failure_persistence_to_dict(
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