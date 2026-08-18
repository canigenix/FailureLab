from __future__ import annotations

import json
from pathlib import Path

from failurelab.failure_cluster_policy import (
    FailureClusterPolicy,
)


def _optional_integer(
    data: dict,
    key: str,
) -> int | None:
    value = data.get(key)

    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError(
            f"{key} must be an integer."
        )

    try:
        converted = int(value)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{key} must be an integer."
        ) from exc

    if converted != value:
        raise ValueError(
            f"{key} must be an integer."
        )

    if converted < 0:
        raise ValueError(
            f"{key} cannot be negative."
        )

    return converted


def load_failure_cluster_policy(
    path: str | Path,
) -> FailureClusterPolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "failure cluster policy must be "
            "a JSON object."
        )

    return FailureClusterPolicy(
        maximum_clusters=_optional_integer(
            data,
            "maximum_clusters",
        ),
        maximum_cluster_size=_optional_integer(
            data,
            "maximum_cluster_size",
        ),
    )