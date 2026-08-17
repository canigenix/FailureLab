from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from failurelab.class_policy import ClassPolicy


@dataclass(frozen=True)
class LoadedClassPolicy:
    default_policy: ClassPolicy
    class_policies: dict[int, ClassPolicy]
    minimum_class_coverage: float | None = None

    def __iter__(self):
        yield self.default_policy
        yield self.class_policies


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
            f"class policy field '{key}' must be numeric."
        ) from exc

    if value < 0:
        raise ValueError(
            f"class policy field '{key}' cannot be negative."
        )

    return value


def _minimum_samples(
    data: dict,
) -> int:
    value = data.get(
        "minimum_samples",
        1,
    )

    if isinstance(value, bool):
        raise ValueError(
            "class policy field 'minimum_samples' "
            "must be an integer."
        )

    try:
        converted = int(value)
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "class policy field 'minimum_samples' "
            "must be an integer."
        ) from exc

    if converted != value:
        raise ValueError(
            "class policy field 'minimum_samples' "
            "must be an integer."
        )

    if converted < 1:
        raise ValueError(
            "class policy field 'minimum_samples' "
            "must be at least 1."
        )

    return converted


def _minimum_class_coverage(
    data: dict,
) -> float | None:
    value = data.get(
        "minimum_class_coverage"
    )

    if value is None:
        return None

    try:
        converted = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "class policy field "
            "'minimum_class_coverage' must be numeric."
        ) from exc

    if not 0.0 <= converted <= 1.0:
        raise ValueError(
            "class policy field "
            "'minimum_class_coverage' must be "
            "between 0.0 and 1.0."
        )

    return converted


def _build_policy(
    data: dict,
) -> ClassPolicy:
    return ClassPolicy(
        maximum_accuracy_drop=_optional_float(
            data,
            "maximum_accuracy_drop",
        ),
        maximum_confidence_drop=_optional_float(
            data,
            "maximum_confidence_drop",
        ),
        maximum_failure_rate=_optional_float(
            data,
            "maximum_failure_rate",
        ),
        maximum_flip_rate=_optional_float(
            data,
            "maximum_flip_rate",
        ),
        warning_accuracy_drop=_optional_float(
            data,
            "warning_accuracy_drop",
        ),
        warning_confidence_drop=_optional_float(
            data,
            "warning_confidence_drop",
        ),
        warning_failure_rate=_optional_float(
            data,
            "warning_failure_rate",
        ),
        warning_flip_rate=_optional_float(
            data,
            "warning_flip_rate",
        ),
        minimum_samples=_minimum_samples(
            data
        ),
    )


def load_class_policy(
    path: str | Path,
) -> LoadedClassPolicy:
    path = Path(path)

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "class policy must be a JSON object."
        )

    default_data = data.get(
        "default",
        {},
    )

    if not isinstance(
        default_data,
        dict,
    ):
        raise ValueError(
            "class policy 'default' must be an object."
        )

    raw_classes = data.get(
        "classes",
        {},
    )

    if not isinstance(
        raw_classes,
        dict,
    ):
        raise ValueError(
            "class policy 'classes' must be an object."
        )

    class_policies: dict[int, ClassPolicy] = {}

    for class_key, class_data in raw_classes.items():
        if not isinstance(
            class_data,
            dict,
        ):
            raise ValueError(
                f"class policy '{class_key}' must be an object."
            )

        try:
            class_index = int(
                class_key
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"class policy key '{class_key}' "
                "must be an integer class index."
            ) from exc

        if class_index < 0:
            raise ValueError(
                "class policy indices cannot be negative."
            )

        class_policies[
            class_index
        ] = _build_policy(
            class_data
        )

    return LoadedClassPolicy(
        default_policy=_build_policy(
            default_data
        ),
        class_policies=class_policies,
        minimum_class_coverage=(
            _minimum_class_coverage(
                data
            )
        ),
    )