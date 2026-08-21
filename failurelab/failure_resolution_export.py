import json
from pathlib import Path

from failurelab.failure_resolution_policy import (
    FailureResolutionPolicyResult,
)
from failurelab.failure_resolution_report import (
    FailureResolutionReport,
)


def failure_resolution_to_dict(
    report: FailureResolutionReport,
) -> dict:
    """Convert a resolution report into a JSON-safe dictionary."""

    return {
        "total_failures": report.total_failures,
        "improving_count": report.improving_count,
        "unchanged_count": report.unchanged_count,
        "worsening_count": report.worsening_count,
        "insufficient_history_count": (
            report.insufficient_history_count
        ),
        "unresolved_count": report.unresolved_count,
        "worst_resolution": (
            {
                "failure_name": (
                    report.worst_resolution.failure_name
                ),
                "first_score": (
                    report.worst_resolution.first_score
                ),
                "latest_score": (
                    report.worst_resolution.latest_score
                ),
                "score_delta": (
                    report.worst_resolution.score_delta
                ),
                "occurrence_count": (
                    report.worst_resolution.occurrence_count
                ),
                "status": (
                    report.worst_resolution.status
                ),
            }
            if report.worst_resolution is not None
            else None
        ),
        "failures": [
            {
                "failure_name": failure.failure_name,
                "first_score": failure.first_score,
                "latest_score": failure.latest_score,
                "score_delta": failure.score_delta,
                "occurrence_count": failure.occurrence_count,
                "status": failure.status,
            }
            for failure in report.failures
        ],
    }


def export_failure_resolution_json(
    report: FailureResolutionReport,
    path,
    *,
    policy: FailureResolutionPolicyResult | None = None,
) -> Path:
    """Export failure resolution analysis as JSON."""

    output_path = Path(path)

    data = failure_resolution_to_dict(
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