import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)


def run_profile_triage(
    profile: EvaluationProfile,
    *,
    input_path: str | Path | None = None,
    base_path: Path | None = None,
) -> EvaluationStepResult:
    """Execute the triage step for an evaluation profile."""

    if not profile.run_triage:
        raise ValueError(
            "Triage analysis is not enabled."
        )

    source = (
        Path(input_path)
        if input_path is not None
        else None
    )

    if source is None:
        raise ValueError(
            "A triage input is required to execute triage analysis."
        )

    if (
        base_path is not None
        and not source.is_absolute()
    ):
        source = base_path / source

    data = json.loads(
        source.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, list):
        raise ValueError(
            "Triage input must be a JSON list."
        )

    signals = [
        FailurePrioritySignal(
            name=row["name"],
            failure_rate=float(
                row["failure_rate"]
            ),
            prediction_flip_rate=float(
                row["prediction_flip_rate"]
            ),
            affected_fraction=float(
                row["affected_fraction"]
            ),
            severity_weight=float(
                row.get(
                    "severity_weight",
                    1.0,
                )
            ),
        )
        for row in data
    ]

    report = build_failure_triage_report(
        signals
    )

    message = (
        f"{report.total_failures} failures analyzed; "
        f"{report.actionable_count} actionable; "
        f"{report.critical_count} critical."
    )

    return EvaluationStepResult(
        analysis="triage",
        passed=True,
        message=message,
    )