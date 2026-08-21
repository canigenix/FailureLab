import json
from pathlib import Path

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.progression import (
    ProgressionPoint,
    summarize_progression_history,
)


def run_profile_progression(
    profile: EvaluationProfile,
    *,
    input_path: str | Path | None = None,
    base_path: Path | None = None,
    tolerance: float = 0.0,
) -> EvaluationStepResult:
    """Execute the progression step for an evaluation profile."""

    if not profile.run_progression:
        raise ValueError(
            "Progression analysis is not enabled."
        )

    source = (
        Path(input_path)
        if input_path is not None
        else None
    )

    if source is None:
        raise ValueError(
            "A progression input is required to execute progression analysis."
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
            "Progression input must be a JSON list."
        )

    points = [
        ProgressionPoint(
            label=row["label"],
            failure_rate=float(
                row["failure_rate"]
            ),
        )
        for row in data
    ]

    report = summarize_progression_history(
        points,
        tolerance=tolerance,
    )

    message = (
        f"{len(points)} checkpoints analyzed; "
        f"{report.improved_count} improved; "
        f"{report.regressed_count} regressed; "
        f"trend {report.trend}."
    )

    return EvaluationStepResult(
        analysis="progression",
        passed=True,
        message=message,
    )