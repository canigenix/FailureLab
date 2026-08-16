from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from failurelab.blur import BlurTest
from failurelab.compression import CompressionTest
from failurelab.crop import CenterCropTest
from failurelab.occlusion import OcclusionTest
from failurelab.rotation import RotationTest
from failurelab.stress_tests import BrightnessTest


@dataclass(frozen=True)
class StressSpec:
    type: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class SuiteConfig:
    stresses: list[StressSpec]
    name: str = "default"
    maximum_drop: float | None = None


def load_suite_config(
    path: str | Path,
) -> SuiteConfig:
    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            "suite configuration must be a JSON object."
        )

    raw_stresses = data.get("stresses")

    if not isinstance(raw_stresses, list) or not raw_stresses:
        raise ValueError(
            "suite configuration must contain "
            "a non-empty 'stresses' list."
        )

    stresses = []

    for item in raw_stresses:
        if not isinstance(item, dict):
            raise ValueError(
                "each stress configuration "
                "must be an object."
            )

        stress_type = item.get("type")

        if (
            not isinstance(stress_type, str)
            or not stress_type.strip()
        ):
            raise ValueError(
                "each stress configuration "
                "requires a 'type'."
            )

        parameters = {
            key: value
            for key, value in item.items()
            if key != "type"
        }

        stresses.append(
            StressSpec(
                type=stress_type.strip().lower(),
                parameters=parameters,
            )
        )

    suite_name = data.get(
        "name",
        "default",
    )

    if (
        not isinstance(suite_name, str)
        or not suite_name.strip()
    ):
        raise ValueError(
            "suite configuration 'name' "
            "must be a non-empty string."
        )

    maximum_drop = data.get(
        "maximum_drop"
    )

    if maximum_drop is not None:
        try:
            maximum_drop = float(
                maximum_drop
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "suite configuration 'maximum_drop' "
                "must be numeric."
            ) from exc

        if maximum_drop < 0:
            raise ValueError(
                "suite configuration 'maximum_drop' "
                "cannot be negative."
            )

    return SuiteConfig(
        stresses=stresses,
        name=suite_name.strip(),
        maximum_drop=maximum_drop,
    )


BUILT_IN_STRESSES = {
    "blur": BlurTest,
    "brightness": BrightnessTest,
    "compression": CompressionTest,
    "crop": CenterCropTest,
    "occlusion": OcclusionTest,
    "rotation": RotationTest,
}


def build_stress_tests(
    config: SuiteConfig,
):
    stress_tests = []

    for spec in config.stresses:
        stress_class = BUILT_IN_STRESSES.get(
            spec.type
        )

        if stress_class is None:
            raise ValueError(
                f"unknown stress type: {spec.type}"
            )

        try:
            stress_test = stress_class(
                **spec.parameters
            )
        except TypeError as exc:
            raise ValueError(
                f"invalid parameters for "
                f"stress type '{spec.type}'."
            ) from exc

        stress_tests.append(
            stress_test
        )

    return stress_tests