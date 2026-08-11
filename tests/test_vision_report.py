import numpy as np

from failurelab.vision_metrics import VisionMetrics
from failurelab.vision_report import (
    VisionDiagnosticReport,
    classify_vision_severity,
    rank_vision_results,
)
from failurelab.vision_runner import VisionStressResult


def make_result(
    name,
    baseline_metrics,
    stressed_metrics,
):
    baseline_probabilities = np.array(
        [
            [0.70, 0.30],
            [0.20, 0.80],
        ]
    )

    stressed_probabilities = np.array(
        [
            [0.60, 0.40],
            [0.35, 0.65],
        ]
    )

    targets = np.array(
        [
            0,
            1,
        ]
    )

    return VisionStressResult(
        name=name,
        baseline=baseline_metrics,
        stressed=stressed_metrics,
        baseline_probabilities=baseline_probabilities,
        stressed_probabilities=stressed_probabilities,
        targets=targets,
    )


def test_classify_vision_severity():
    assert classify_vision_severity(
        0.30,
        0.10,
        0.05,
    ) == "critical"

    assert classify_vision_severity(
        0.10,
        0.18,
        0.04,
    ) == "high"

    assert classify_vision_severity(
        0.02,
        0.03,
        0.07,
    ) == "medium"

    assert classify_vision_severity(
        0.01,
        0.01,
        0.02,
    ) == "low"


def test_rank_vision_results_orders_worst_first():
    baseline = VisionMetrics(
        top1_accuracy=0.70,
        top5_accuracy=0.93,
        mean_target_confidence=0.49,
    )

    blur = make_result(
        name="blur_3.00",
        baseline_metrics=baseline,
        stressed_metrics=VisionMetrics(
            top1_accuracy=0.36,
            top5_accuracy=0.61,
            mean_target_confidence=0.24,
        ),
    )

    compression = make_result(
        name="jpeg_20",
        baseline_metrics=baseline,
        stressed_metrics=VisionMetrics(
            top1_accuracy=0.63,
            top5_accuracy=0.90,
            mean_target_confidence=0.46,
        ),
    )

    ranked = rank_vision_results(
        [
            compression,
            blur,
        ]
    )

    assert ranked[0].name == "blur"
    assert ranked[0].severity == "critical"
    assert ranked[1].name == "compression"


def test_vision_report_includes_diagnosis():
    baseline = VisionMetrics(
        top1_accuracy=0.70,
        top5_accuracy=0.93,
        mean_target_confidence=0.49,
    )

    blur = make_result(
        name="blur_3.00",
        baseline_metrics=baseline,
        stressed_metrics=VisionMetrics(
            top1_accuracy=0.36,
            top5_accuracy=0.61,
            mean_target_confidence=0.24,
        ),
    )

    weaknesses = rank_vision_results(
        [
            blur,
        ]
    )

    report = VisionDiagnosticReport(
        weaknesses
    ).to_text()

    assert "Blur" in report
    assert "Severity: critical" in report
    assert "Diagnosis:" in report