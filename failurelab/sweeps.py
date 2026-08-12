"""Stress-test sweep utilities for FailureLab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .blur import BlurTest
from .compression import CompressionTest
from .crop import CenterCropTest
from .occlusion import OcclusionTest
from .rotation import RotationTest
from .runner import StressTestResult
from .stress_tests import BrightnessTest
from .vision_runner import (
    VisionStressResult,
    VisionStressRunner,
)


# ============================================================
# Original FailureLab sweep API
# ============================================================


@dataclass
class SweepResult:
    test_name: str
    results: list[StressTestResult]

    def worst_result(self) -> StressTestResult:
        if not self.results:
            raise ValueError(
                "sweep contains no results."
            )

        return max(
            self.results,
            key=lambda result: result.accuracy_drop,
        )

    def severity(self) -> str:
        return self.worst_result().severity

    def first_failure(
        self,
        minimum_drop: float = 0.05,
    ):
        if minimum_drop < 0:
            raise ValueError(
                "minimum_drop cannot be negative."
            )

        for result in self.results:
            if result.accuracy_drop >= minimum_drop:
                return result

        return None


class BrightnessSweep:
    def __init__(
        self,
        factors=None,
    ):
        self.factors = factors or [
            0.90,
            0.75,
            0.60,
            0.45,
            0.30,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "brightness",
            [
                runner.run(
                    dataset,
                    BrightnessTest(factor),
                )
                for factor in self.factors
            ],
        )


class BlurSweep:
    def __init__(
        self,
        radii=None,
    ):
        self.radii = radii or [
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "blur",
            [
                runner.run(
                    dataset,
                    BlurTest(radius),
                )
                for radius in self.radii
            ],
        )


class CompressionSweep:
    def __init__(
        self,
        qualities=None,
    ):
        self.qualities = qualities or [
            90,
            70,
            50,
            30,
            10,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "compression",
            [
                runner.run(
                    dataset,
                    CompressionTest(quality),
                )
                for quality in self.qualities
            ],
        )


class OcclusionSweep:
    def __init__(
        self,
        fractions=None,
    ):
        self.fractions = fractions or [
            0.10,
            0.20,
            0.30,
            0.40,
            0.50,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "occlusion",
            [
                runner.run(
                    dataset,
                    OcclusionTest(fraction),
                )
                for fraction in self.fractions
            ],
        )


class RotationSweep:
    def __init__(
        self,
        degrees=None,
    ):
        self.degrees = degrees or [
            5,
            10,
            20,
            30,
            45,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "rotation",
            [
                runner.run(
                    dataset,
                    RotationTest(degree),
                )
                for degree in self.degrees
            ],
        )


class CropSweep:
    def __init__(
        self,
        fractions=None,
    ):
        self.fractions = fractions or [
            0.90,
            0.80,
            0.70,
            0.60,
            0.50,
        ]

    def run(
        self,
        runner,
        dataset,
    ):
        return SweepResult(
            "crop",
            [
                runner.run(
                    dataset,
                    CenterCropTest(fraction),
                )
                for fraction in self.fractions
            ],
        )


# ============================================================
# FailureLab severity-threshold sweep API
# ============================================================


@dataclass(frozen=True)
class SweepPoint:
    """One severity point in a robustness sweep."""

    severity_value: float
    result: VisionStressResult


@dataclass(frozen=True)
class StressSweepResult:
    """Results across multiple severities for one stress family."""

    name: str
    points: list[SweepPoint]

    @property
    def worst_top1_drop(self) -> float:
        if not self.points:
            return 0.0

        return max(
            point.result.top1_drop
            for point in self.points
        )

    @property
    def failure_threshold(self) -> float | None:
        """
        Return the first severity where top-1 drop reaches 25%.

        None means the tested sweep never crossed the threshold.
        """

        for point in self.points:
            if point.result.top1_drop >= 0.25:
                return point.severity_value

        return None


def run_stress_sweep(
    *,
    name: str,
    severity_values: Iterable[float],
    stress_factory: Callable[[float], object],
    predict_proba_fn,
    dataset,
) -> StressSweepResult:
    """Run one stress type across multiple severity values."""

    runner = VisionStressRunner(
        predict_proba_fn
    )

    points = []

    for severity_value in severity_values:
        stress_test = stress_factory(
            severity_value
        )

        result = runner.run(
            dataset=dataset,
            stress_test=stress_test,
        )

        points.append(
            SweepPoint(
                severity_value=float(
                    severity_value
                ),
                result=result,
            )
        )

    return StressSweepResult(
        name=name,
        points=points,
    )