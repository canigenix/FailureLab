from __future__ import annotations
from dataclasses import dataclass
from .blur import BlurTest
from .compression import CompressionTest
from .crop import CenterCropTest
from .occlusion import OcclusionTest
from .rotation import RotationTest
from .runner import StressTestResult, StressTestRunner
from .stress_tests import BrightnessTest

@dataclass
class SweepResult:
    test_name: str
    results: list[StressTestResult]
    def worst_result(self) -> StressTestResult:
        if not self.results:
            raise ValueError("sweep contains no results.")
        return max(self.results, key=lambda r: r.accuracy_drop)
    def severity(self) -> str:
        return self.worst_result().severity
    def first_failure(self, minimum_drop: float = 0.05):
        if minimum_drop < 0:
            raise ValueError("minimum_drop cannot be negative.")
        for result in self.results:
            if result.accuracy_drop >= minimum_drop:
                return result
        return None

class BrightnessSweep:
    def __init__(self, factors=None): self.factors = factors or [0.90,0.75,0.60,0.45,0.30]
    def run(self, runner, dataset):
        return SweepResult("brightness", [runner.run(dataset, BrightnessTest(f)) for f in self.factors])
class BlurSweep:
    def __init__(self, radii=None): self.radii = radii or [0.5,1.0,2.0,3.0,5.0]
    def run(self, runner, dataset):
        return SweepResult("blur", [runner.run(dataset, BlurTest(r)) for r in self.radii])
class CompressionSweep:
    def __init__(self, qualities=None): self.qualities = qualities or [90,70,50,30,10]
    def run(self, runner, dataset):
        return SweepResult("compression", [runner.run(dataset, CompressionTest(q)) for q in self.qualities])
class OcclusionSweep:
    def __init__(self, fractions=None): self.fractions = fractions or [0.10,0.20,0.30,0.40,0.50]
    def run(self, runner, dataset):
        return SweepResult("occlusion", [runner.run(dataset, OcclusionTest(f)) for f in self.fractions])
class RotationSweep:
    def __init__(self, degrees=None): self.degrees = degrees or [5,10,20,30,45]
    def run(self, runner, dataset):
        return SweepResult("rotation", [runner.run(dataset, RotationTest(d)) for d in self.degrees])
class CropSweep:
    def __init__(self, fractions=None): self.fractions = fractions or [0.90,0.80,0.70,0.60,0.50]
    def run(self, runner, dataset):
        return SweepResult("crop", [runner.run(dataset, CenterCropTest(f)) for f in self.fractions])
