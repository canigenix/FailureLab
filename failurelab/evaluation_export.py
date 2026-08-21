import json
from pathlib import Path

from failurelab.evaluation_report import (
    EvaluationReport,
)


def evaluation_report_to_dict(
    report: EvaluationReport,
) -> dict:
    """Convert an evaluation report to a JSON-safe dictionary."""

    return {
        "profile_name": report.profile_name,
        "suite_config": report.suite_config,
        "passed": report.passed,
        "passed_count": report.passed_count,
        "failed_count": report.failed_count,
        "steps": [
            {
                "analysis": step.analysis,
                "passed": step.passed,
                "message": step.message,
            }
            for step in report.steps
        ],
    }


def export_evaluation_json(
    report: EvaluationReport,
    path,
) -> Path:
    """Export an evaluation report as JSON."""

    output_path = Path(path)

    output_path.write_text(
        json.dumps(
            evaluation_report_to_dict(
                report
            ),
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path