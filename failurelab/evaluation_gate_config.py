from dataclasses import dataclass
from pathlib import Path
import json


VALID_HEALTH_STATUSES = {
    "healthy",
    "watch",
    "at-risk",
    "critical",
}


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
    """Load and validate evaluation gate configuration from JSON."""

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

    raw_maximum = data.get(
        "maximum_failed_analyses",
        0,
    )

    if (
        isinstance(raw_maximum, bool)
        or not isinstance(raw_maximum, int)
    ):
        raise ValueError(
            "maximum_failed_analyses must be an integer."
        )

    if raw_maximum < 0:
        raise ValueError(
            "maximum_failed_analyses cannot be negative."
        )

    raw_statuses = data.get(
        "allowed_health_statuses",
        [
            "healthy",
        ],
    )

    if not isinstance(
        raw_statuses,
        list,
    ):
        raise ValueError(
            "allowed_health_statuses must be a JSON list."
        )

    if not raw_statuses:
        raise ValueError(
            "allowed_health_statuses cannot be empty."
        )

    if not all(
        isinstance(status, str)
        for status in raw_statuses
    ):
        raise ValueError(
            "allowed_health_statuses must contain only strings."
        )

    invalid = [
        status
        for status in raw_statuses
        if status not in VALID_HEALTH_STATUSES
    ]

    if invalid:
        raise ValueError(
            "Invalid health status: "
            + ", ".join(
                invalid
            )
        )

    if len(set(raw_statuses)) != len(raw_statuses):
        raise ValueError(
            "allowed_health_statuses cannot contain duplicates."
        )

    return EvaluationGateConfig(
        maximum_failed_analyses=raw_maximum,
        allowed_health_statuses=tuple(
            raw_statuses
        ),
    )