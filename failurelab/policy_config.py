from __future__ import annotations

import json
from pathlib import Path

from failurelab.robustness_policy import (
    RobustnessPolicy,
    StressPolicy,
)


def _optional_float(
    data: dict,
    key: str,
) -> float | None:
    value = data.get(key)

    if value is None:
        return None

    try:
        value = float(value)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"policy field '{key}' must be numeric."
        ) from exc

    if value < 0:
        raise ValueError(
            f"policy field '{key}' cannot be negative."
        )

    return value


def load_robustness_policy(
    path: str | Path,
) -> RobustnessPolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "robustness policy must be a JSON object."
        )

    raw_stresses = data.get(
        "stresses",
        {},
    )

    if not isinstance(raw_stresses, dict):
        raise ValueError(
            "policy 'stresses' must be an object."
        )

    stresses: dict[str, StressPolicy] = {}

    for stress_name, stress_data in raw_stresses.items():
        if not isinstance(stress_name, str) or not stress_name.strip():
            raise ValueError(
                "stress policy names must be non-empty strings."
            )

        if not isinstance(stress_data, dict):
            raise ValueError(
                f"stress policy '{stress_name}' must be an object."
            )

        stresses[
            stress_name.strip().lower()
        ] = StressPolicy(
            maximum_top1_drop=_optional_float(
                stress_data,
                "maximum_top1_drop",
            ),
            maximum_top5_drop=_optional_float(
                stress_data,
                "maximum_top5_drop",
            ),
            maximum_confidence_drop=_optional_float(
                stress_data,
                "maximum_confidence_drop",
            ),
        )

    return RobustnessPolicy(
        maximum_top1_drop=_optional_float(
            data,
            "maximum_top1_drop",
        ),
        maximum_top5_drop=_optional_float(
            data,
            "maximum_top5_drop",
        ),
        maximum_confidence_drop=_optional_float(
            data,
            "maximum_confidence_drop",
        ),
        stresses=stresses,
    )