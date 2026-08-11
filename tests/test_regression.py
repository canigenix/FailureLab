import numpy as np
import pytest

from failurelab.regression import (
    RobustnessThreshold,
    evaluate_regression,
    evaluate_regression_suite,
)
from failurelab.vision_metrics import VisionMetrics
from failurelab.vision_runner import VisionStressResult


def make_result(
    name="blur_3.00",
    baseline_top1=0.80,
    stressed_top1=0.60,
    baseline_top5=0.95,
    stressed_top5=0.85,
    baseline_confidence=0.70,
    stressed_confidence=0.50,
):
    return VisionStressResult(
        name=name,
        baseline=VisionMetrics(
            top1_accuracy=baseline_top1,
            top5_accuracy=baseline_top5,
            mean_target_confidence=baseline_confidence,
        ),
        stressed=VisionMetrics(
            top1_accuracy=stressed_top1,
            top5_accuracy=stressed_top5,
            mean_target_confidence=stressed_confidence,
        ),
        baseline_probabilities=np.array(
            [
                [0.8, 0.2],
                [0.3, 0.7],
            ]
        ),
        stressed_probabilities=np.array(
            [
                [0.6, 0.4],
                [0.5, 0.5],
            ]
        ),
        targets=np.array(
            [
                0,
                1,
            ]
        ),
    )


def test_regression_passes_when_requirements_are_met():
    result = make_result()

    threshold = RobustnessThreshold(
        stress_name="blur_3.00",
        minimum_top1_accuracy=0.55,
        maximum_top1_drop=0.25,
        maximum_confidence_drop=0.25,
    )

    check = evaluate_regression(
        result,
        threshold,
    )

    assert check.passed is True
    assert check.failures == ()


def test_regression_fails_when_accuracy_is_too_low():
    result = make_result()

    threshold = RobustnessThreshold(
        stress_name="blur_3.00",
        minimum_top1_accuracy=0.70,
    )

    check = evaluate_regression(
        result,
        threshold,
    )

    assert check.passed is False
    assert len(check.failures) == 1
    assert "top-1 accuracy" in check.failures[0]


def test_regression_can_detect_multiple_failures():
    result = make_result()

    threshold = RobustnessThreshold(
        stress_name="blur_3.00",
        minimum_top1_accuracy=0.70,
        maximum_top1_drop=0.10,
        maximum_confidence_drop=0.10,
    )

    check = evaluate_regression(
        result,
        threshold,
    )

    assert check.passed is False
    assert len(check.failures) == 3


def test_regression_rejects_invalid_threshold():
    result = make_result()

    threshold = RobustnessThreshold(
        stress_name="blur_3.00",
        minimum_top1_accuracy=1.5,
    )

    with pytest.raises(ValueError):
        evaluate_regression(
            result,
            threshold,
        )


def test_regression_suite_marks_missing_test_as_failure():
    result = make_result()

    thresholds = [
        RobustnessThreshold(
            stress_name="blur_3.00",
            minimum_top1_accuracy=0.50,
        ),
        RobustnessThreshold(
            stress_name="occlusion_0.40",
            minimum_top1_accuracy=0.50,
        ),
    ]

    checks = evaluate_regression_suite(
        results=[result],
        thresholds=thresholds,
    )

    assert checks[0].passed is True

    assert checks[1].passed is False
    assert checks[1].failures == (
        "stress test result is missing",
    )