import numpy as np

from failurelab.class_report import top_vulnerable_classes
from failurelab.vision_metrics import VisionMetrics
from failurelab.vision_runner import VisionStressResult


def test_top_vulnerable_classes_returns_names():
    result = VisionStressResult(
        name="blur_3.00",
        baseline=VisionMetrics(
            top1_accuracy=1.0,
            top5_accuracy=1.0,
            mean_target_confidence=0.85,
        ),
        stressed=VisionMetrics(
            top1_accuracy=0.5,
            top5_accuracy=1.0,
            mean_target_confidence=0.55,
        ),
        baseline_probabilities=np.array(
            [
                [0.90, 0.10],
                [0.20, 0.80],
            ]
        ),
        stressed_probabilities=np.array(
            [
                [0.40, 0.60],
                [0.30, 0.70],
            ]
        ),
        targets=np.array(
            [
                0,
                1,
            ]
        ),
    )

    categories = [
        "class zero",
        "class one",
    ]

    vulnerable = top_vulnerable_classes(
        result=result,
        categories=categories,
        limit=2,
    )

    assert vulnerable[0]["class_name"] == "class zero"
    assert vulnerable[0]["accuracy_drop"] == 1.0


def test_top_vulnerable_classes_includes_new_metrics():
    result = VisionStressResult(
        name="blur_3.00",
        baseline=VisionMetrics(
            top1_accuracy=1.0,
            top5_accuracy=1.0,
            mean_target_confidence=0.85,
        ),
        stressed=VisionMetrics(
            top1_accuracy=0.5,
            top5_accuracy=1.0,
            mean_target_confidence=0.55,
        ),
        baseline_probabilities=np.array(
            [
                [0.90, 0.10],
                [0.20, 0.80],
            ]
        ),
        stressed_probabilities=np.array(
            [
                [0.40, 0.60],
                [0.30, 0.70],
            ]
        ),
        targets=np.array(
            [
                0,
                1,
            ]
        ),
    )

    categories = [
        "class zero",
        "class one",
    ]

    vulnerable = top_vulnerable_classes(
        result=result,
        categories=categories,
        limit=2,
    )

    first = vulnerable[0]

    assert "stressed_failure_rate" in first
    assert "prediction_flip_rate" in first
    assert first["stressed_failure_rate"] == 1.0
    assert first["prediction_flip_rate"] == 1.0


def test_top_vulnerable_classes_includes_confusion_target():
    result = VisionStressResult(
        name="blur_3.00",
        baseline=VisionMetrics(
            top1_accuracy=1.0,
            top5_accuracy=1.0,
            mean_target_confidence=0.85,
        ),
        stressed=VisionMetrics(
            top1_accuracy=0.5,
            top5_accuracy=1.0,
            mean_target_confidence=0.55,
        ),
        baseline_probabilities=np.array(
            [
                [0.90, 0.05, 0.05],
                [0.80, 0.10, 0.10],
                [0.10, 0.80, 0.10],
            ]
        ),
        stressed_probabilities=np.array(
            [
                [0.20, 0.70, 0.10],
                [0.30, 0.60, 0.10],
                [0.10, 0.70, 0.20],
            ]
        ),
        targets=np.array(
            [
                0,
                0,
                1,
            ]
        ),
    )

    categories = [
        "class zero",
        "class one",
        "class two",
    ]

    vulnerable = top_vulnerable_classes(
        result=result,
        categories=categories,
        limit=3,
    )

    by_name = {
        row["class_name"]: row
        for row in vulnerable
    }

    assert by_name["class zero"]["top_confusion_class"] == "class one"
    assert by_name["class zero"]["top_confusion_rate"] == 1.0