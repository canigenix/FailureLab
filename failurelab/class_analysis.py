from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ClassRobustnessResult:
    class_index: int
    sample_count: int
    baseline_accuracy: float
    stressed_accuracy: float
    accuracy_drop: float
    baseline_confidence: float
    stressed_confidence: float
    confidence_drop: float
    stressed_failure_rate: float
    prediction_flip_rate: float
    top_confusion_class: int | None
    top_confusion_rate: float


def analyze_class_robustness(
    baseline_probabilities,
    stressed_probabilities,
    targets,
):
    bp = np.asarray(baseline_probabilities, dtype=float)
    sp = np.asarray(stressed_probabilities, dtype=float)
    t = np.asarray(targets, dtype=int)

    if bp.shape != sp.shape:
        raise ValueError(
            "baseline and stressed probabilities must have the same shape."
        )

    if len(t) != len(bp):
        raise ValueError(
            "targets must match the number of probability rows."
        )

    results = []

    baseline_predictions = np.argmax(bp, axis=1)
    stressed_predictions = np.argmax(sp, axis=1)

    for class_index in np.unique(t):
        mask = t == class_index

        class_baseline = bp[mask]
        class_stressed = sp[mask]
        class_targets = t[mask]

        class_baseline_predictions = baseline_predictions[mask]
        class_stressed_predictions = stressed_predictions[mask]

        baseline_accuracy = float(
            np.mean(class_baseline_predictions == class_targets)
        )

        stressed_accuracy = float(
            np.mean(class_stressed_predictions == class_targets)
        )

        baseline_confidence = float(
            np.mean(
                class_baseline[
                    np.arange(len(class_targets)),
                    class_targets,
                ]
            )
        )

        stressed_confidence = float(
            np.mean(
                class_stressed[
                    np.arange(len(class_targets)),
                    class_targets,
                ]
            )
        )

        stressed_failure_rate = float(
            np.mean(class_stressed_predictions != class_targets)
        )

        prediction_flip_rate = float(
            np.mean(
                class_baseline_predictions
                != class_stressed_predictions
            )
        )

        wrong_predictions = class_stressed_predictions[
            class_stressed_predictions != class_targets
        ]

        if len(wrong_predictions) > 0:
            confusion_classes, confusion_counts = np.unique(
                wrong_predictions,
                return_counts=True,
            )

            top_index = int(np.argmax(confusion_counts))

            top_confusion_class = int(
                confusion_classes[top_index]
            )

            top_confusion_rate = float(
                confusion_counts[top_index] / len(class_targets)
            )
        else:
            top_confusion_class = None
            top_confusion_rate = 0.0

        results.append(
            ClassRobustnessResult(
                class_index=int(class_index),
                sample_count=len(class_targets),
                baseline_accuracy=baseline_accuracy,
                stressed_accuracy=stressed_accuracy,
                accuracy_drop=baseline_accuracy - stressed_accuracy,
                baseline_confidence=baseline_confidence,
                stressed_confidence=stressed_confidence,
                confidence_drop=baseline_confidence - stressed_confidence,
                stressed_failure_rate=stressed_failure_rate,
                prediction_flip_rate=prediction_flip_rate,
                top_confusion_class=top_confusion_class,
                top_confusion_rate=top_confusion_rate,
            )
        )

    return sorted(
        results,
        key=lambda result: max(
            result.accuracy_drop,
            result.confidence_drop,
        ),
        reverse=True,
    )
def test_class_analysis_tracks_failure_and_prediction_flip_rates():
    baseline = np.array(
        [
            [0.90, 0.10],
            [0.80, 0.20],
            [0.10, 0.90],
            [0.20, 0.80],
        ]
    )

    stressed = np.array(
        [
            [0.40, 0.60],
            [0.70, 0.30],
            [0.60, 0.40],
            [0.25, 0.75],
        ]
    )

    targets = np.array([0, 0, 1, 1])

    results = analyze_class_robustness(
        baseline,
        stressed,
        targets,
    )

    by_class = {
        result.class_index: result
        for result in results
    }

    assert by_class[0].stressed_failure_rate == 0.5
    assert by_class[0].prediction_flip_rate == 0.5

    assert by_class[1].stressed_failure_rate == 0.5
    assert by_class[1].prediction_flip_rate == 0.5