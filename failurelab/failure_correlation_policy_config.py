from __future__ import annotations

import json
from pathlib import Path

from failurelab.failure_correlation_policy import (
    FailureCorrelationPolicy,
)


def load_failure_correlation_policy(
    path: str | Path,
) -> FailureCorrelationPolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "failure correlation policy "
            "must be a JSON object."
        )

    maximum_correlation = data.get(
        "maximum_correlation"
    )

    if maximum_correlation is not None:
        try:
            maximum_correlation = float(
                maximum_correlation
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_correlation must be numeric."
            ) from exc

        if not 0.0 <= maximum_correlation <= 1.0:
            raise ValueError(
                "maximum_correlation must be "
                "between 0.0 and 1.0."
            )

    maximum_pairs = data.get(
        "maximum_high_correlation_pairs"
    )

    if maximum_pairs is not None:
        if isinstance(maximum_pairs, bool):
            raise ValueError(
                "maximum_high_correlation_pairs "
                "must be an integer."
            )

        try:
            converted = int(
                maximum_pairs
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_high_correlation_pairs "
                "must be an integer."
            ) from exc

        if converted != maximum_pairs:
            raise ValueError(
                "maximum_high_correlation_pairs "
                "must be an integer."
            )

        if converted < 0:
            raise ValueError(
                "maximum_high_correlation_pairs "
                "cannot be negative."
            )

        maximum_pairs = converted

    threshold = data.get(
        "high_correlation_threshold",
        0.75,
    )

    try:
        threshold = float(
            threshold
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "high_correlation_threshold "
            "must be numeric."
        ) from exc

    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "high_correlation_threshold must be "
            "between 0.0 and 1.0."
        )

    return FailureCorrelationPolicy(
        maximum_correlation=maximum_correlation,
        maximum_high_correlation_pairs=maximum_pairs,
        high_correlation_threshold=threshold,
    )