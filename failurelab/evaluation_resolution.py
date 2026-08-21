import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution_report import (
    build_failure_resolution_report,
)


def run_profile_resolution(
    profile: EvaluationProfile,
    *,
    input_path: str | Path | None = None,
    base_path: Path | None = None,
    tolerance: float = 0.0,
) -> EvaluationStepResult:
    """Execute the resolution step for an evaluation profile."""

    if not profile.run_resolution:
        raise ValueError(
            "Resolution analysis is not enabled."
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
            "An occurrence input is required to execute resolution analysis."
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
            "Resolution input must be a JSON list."
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

    report = build_failure_resolution_report(
        occurrences,
        tolerance=tolerance,
    )

    message = (
        f"{report.total_failures} failures analyzed; "
        f"{report.improving_count} improving; "
        f"{report.worsening_count} worsening."
    )

    return EvaluationStepResult(
        analysis="resolution",
        passed=True,
        message=message,
    )