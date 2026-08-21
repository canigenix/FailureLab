import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.failure_persistence_report import (
    build_failure_persistence_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def run_profile_persistence(
    profile: EvaluationProfile,
    *,
    input_path: str | Path | None = None,
    base_path: Path | None = None,
) -> EvaluationStepResult:
    """Execute the persistence step for an evaluation profile."""

    if not profile.run_persistence:
        raise ValueError(
            "Persistence analysis is not enabled."
        )

    source = (
        Path(input_path)
        if input_path is not None
        else (
            Path(profile.forecast_input)
            if profile.forecast_input
            else None
        )
    )

    if source is None:
        raise ValueError(
            "An occurrence input is required to execute persistence analysis."
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
            "Persistence input must be a JSON list."
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

    report = build_failure_persistence_report(
        occurrences
    )

    message = (
        f"{report.total_failures} failures analyzed; "
        f"{report.persistent_count} persistent; "
        f"{report.unresolved_count} unresolved."
    )

    return EvaluationStepResult(
        analysis="persistence",
        passed=True,
        message=message,
    )