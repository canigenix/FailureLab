"""Core model failure analysis for FailureLab."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class FailureCase:
    index: Any
    actual: Any
    predicted: Any
    confidence: float | None = None

class FailureAnalyzer:
    def __init__(self, y_true, y_pred, probabilities=None):
        self.y_true = np.asarray(y_true)
        self.y_pred = np.asarray(y_pred)
        self.probabilities = None if probabilities is None else np.asarray(probabilities)
        self._validate_inputs()

    def _validate_inputs(self):
        if len(self.y_true) != len(self.y_pred):
            raise ValueError("y_true and y_pred must contain the same number of samples.")
        if self.probabilities is not None and len(self.probabilities) != len(self.y_true):
            raise ValueError("probabilities must match the number of predictions.")

    def failure_mask(self) -> np.ndarray:
        return self.y_true != self.y_pred

    def failure_indices(self) -> np.ndarray:
        return np.flatnonzero(self.failure_mask())

    def failure_rate(self) -> float:
        if len(self.y_true) == 0:
            return 0.0
        return float(np.mean(self.failure_mask()))

    def accuracy(self) -> float:
        if len(self.y_true) == 0:
            return 0.0
        return float(np.mean(self.y_true == self.y_pred))

    def _prediction_confidence(self, index: int) -> float:
        probabilities = self.probabilities[index]
        if np.ndim(probabilities) == 0:
            return float(probabilities)
        predicted = self.y_pred[index]
        if isinstance(predicted, (np.integer, int)) and 0 <= int(predicted) < len(probabilities):
            return float(probabilities[int(predicted)])
        return float(np.max(probabilities))

    def failures(self) -> list[FailureCase]:
        cases = []
        for index in self.failure_indices():
            confidence = None if self.probabilities is None else self._prediction_confidence(index)
            cases.append(FailureCase(int(index), self.y_true[index], self.y_pred[index], confidence))
        return cases

    def high_confidence_failures(self, threshold: float = 0.90) -> list[FailureCase]:
        if self.probabilities is None:
            raise ValueError("probabilities are required for high-confidence failure analysis.")
        return [case for case in self.failures() if case.confidence is not None and case.confidence >= threshold]
