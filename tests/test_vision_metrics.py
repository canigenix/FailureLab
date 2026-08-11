import pytest

from failurelab.vision_metrics import calculate_vision_metrics


def test_calculates_top1_top5_and_confidence():
    probabilities = [
        [0.80, 0.10, 0.05, 0.03, 0.02],
        [0.40, 0.35, 0.15, 0.05, 0.05],
    ]

    targets = [
        0,
        1,
    ]

    metrics = calculate_vision_metrics(
        probabilities,
        targets,
    )

    assert metrics.top1_accuracy == 0.5
    assert metrics.top5_accuracy == 1.0

    assert metrics.mean_target_confidence == pytest.approx(
        0.575
    )


def test_rejects_empty_input():
    with pytest.raises(ValueError):
        calculate_vision_metrics(
            probabilities=[],
            targets=[],
        )