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