from __future__ import annotations
from dataclasses import dataclass
from PIL import Image

@dataclass
class StressTestResult:
    name: str
    baseline_accuracy: float
    stressed_accuracy: float
    @property
    def accuracy_drop(self) -> float:
        return self.baseline_accuracy - self.stressed_accuracy
    @property
    def severity(self) -> str:
        drop = self.accuracy_drop
        if drop >= 0.25: return "critical"
        if drop >= 0.15: return "high"
        if drop >= 0.05: return "medium"
        return "low"

class StressTestRunner:
    def __init__(self, predict_fn):
        self.predict_fn = predict_fn
    def run(self, dataset, stress_test) -> StressTestResult:
        baseline_correct = stressed_correct = total = 0
        for image, target in dataset:
            if not isinstance(image, Image.Image):
                raise TypeError("StressTestRunner currently expects PIL images.")
            baseline_prediction = self.predict_fn(image)
            stressed_prediction = self.predict_fn(stress_test.apply(image))
            baseline_correct += int(baseline_prediction == target)
            stressed_correct += int(stressed_prediction == target)
            total += 1
        if total == 0:
            raise ValueError("dataset must contain at least one sample.")
        return StressTestResult(stress_test.name, baseline_correct / total, stressed_correct / total)
