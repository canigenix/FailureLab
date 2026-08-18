from __future__ import annotations

import json
from pathlib import Path

from failurelab.cross_stress_policy import (
    CrossStressPolicy,
)


def load_cross_stress_policy(
    path: str | Path,
) -> CrossStressPolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "cross-stress policy must be a JSON object."
        )

    maximum_systemic_classes = data.get(
        "maximum_systemic_classes"
    )

    if maximum_systemic_classes is not None:
        if isinstance(
            maximum_systemic_classes,
            bool,
        ):
            raise ValueError(
                "maximum_systemic_classes "
                "must be an integer."
            )

        try:
            maximum_systemic_classes = int(
                maximum_systemic_classes
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_systemic_classes "
                "must be an integer."
            ) from exc

        if maximum_systemic_classes < 0:
            raise ValueError(
                "maximum_systemic_classes "
                "cannot be negative."
            )

    maximum_systemic_fraction = data.get(
        "maximum_systemic_fraction"
    )

    if maximum_systemic_fraction is not None:
        try:
            maximum_systemic_fraction = float(
                maximum_systemic_fraction
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_systemic_fraction "
                "must be numeric."
            ) from exc

        if not 0.0 <= maximum_systemic_fraction <= 1.0:
            raise ValueError(
                "maximum_systemic_fraction must be "
                "between 0.0 and 1.0."
            )

    return CrossStressPolicy(
        maximum_systemic_classes=(
            maximum_systemic_classes
        ),
        maximum_systemic_fraction=(
            maximum_systemic_fraction
        ),
    )