from __future__ import annotations

import json
from pathlib import Path

from failurelab.sample_policy import (
    SampleFailurePolicy,
)


def load_sample_failure_policy(
    path: str | Path,
) -> SampleFailurePolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "sample failure policy must be a JSON object."
        )

    maximum_systemic_samples = data.get(
        "maximum_systemic_samples"
    )

    if maximum_systemic_samples is not None:
        if isinstance(
            maximum_systemic_samples,
            bool,
        ):
            raise ValueError(
                "maximum_systemic_samples "
                "must be an integer."
            )

        try:
            maximum_systemic_samples = int(
                maximum_systemic_samples
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_systemic_samples "
                "must be an integer."
            ) from exc

        if maximum_systemic_samples < 0:
            raise ValueError(
                "maximum_systemic_samples "
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

    return SampleFailurePolicy(
        maximum_systemic_samples=(
            maximum_systemic_samples
        ),
        maximum_systemic_fraction=(
            maximum_systemic_fraction
        ),
    )