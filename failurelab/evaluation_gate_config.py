from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class EvaluationGateConfig:
    """Configuration for a unified evaluation release gate."""

    maximum_failed_analyses: int = 0
    allowed_health_statuses: tuple[str, ...] = (
        "healthy",
    )


def load_evaluation_gate_config(
    path: str | Path,
) -> EvaluationGateConfig:
    """Load evaluation gate configuration from JSON."""

    config_path = Path(path)

    data = json.loads(
        config_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Evaluation gate config must be a JSON object."
        )

    maximum_failed_analyses = int(
        data.get(
            "maximum_failed_analyses",
            0,
        )
    )

    if maximum_failed_analyses < 0:
        raise ValueError(
            "maximum_failed_analyses cannot be negative."
        )

    allowed_health_statuses = tuple(
        data.get(
            "allowed_health_statuses",
            [
                "healthy",
            ],
        )
    )

    if not allowed_health_statuses:
        raise ValueError(
            "allowed_health_statuses cannot be empty."
        )

    valid_statuses = {
        "healthy",
        "watch",
        "at-risk",
        "critical",
    }

    invalid = [
        status
        for status in allowed_health_statuses
        if status not in valid_statuses
    ]

    if invalid:
        raise ValueError(
            "Invalid health status: "
            + ", ".join(
                invalid
            )
        )

    return EvaluationGateConfig(
        maximum_failed_analyses=maximum_failed_analyses,
        allowed_health_statuses=allowed_health_statuses,
    )