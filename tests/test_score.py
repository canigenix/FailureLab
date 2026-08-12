import pytest

from failurelab.score import (
    calculate_robustness_score,
)
from failurelab.vision_report import VisionWeakness


def weakness(
    name,
    top1_drop,
    top5_drop=0.0,
    confidence_drop=0.0,
):
    return VisionWeakness(
        name=name,
        severity="medium",
        top1_drop=top1_drop,
        top5_drop=top5_drop,
        confidence_drop=confidence_drop,
    )


def test_perfect_score_when_no_weaknesses():
    result = calculate_robustness_score([])

    assert result.score == 100.0
    assert result.grade == "A"
    assert result.status == "Excellent"
    assert result.average_degradation == 0.0
    assert result.worst_degradation == 0.0


def test_score_combines_average_and_worst_case():
    weaknesses = [
        weakness(
            "blur",
            0.40,
            top5_drop=0.30,
            confidence_drop=0.20,
        ),
        weakness(
            "brightness",
            0.10,
            top5_drop=0.05,
            confidence_drop=0.02,
        ),
    ]

    result = calculate_robustness_score(
        weaknesses
    )

    # Average degradation = 0.25
    # Worst degradation = 0.40
    #
    # Combined:
    # 0.70 * 0.25 + 0.30 * 0.40
    # = 0.295
    #
    # Score = 70.5

    assert result.score == 70.5
    assert result.grade == "C"
    assert result.status == "Needs Improvement"

    assert result.average_degradation == pytest.approx(
        0.25
    )

    assert result.worst_degradation == pytest.approx(
        0.40
    )


def test_catastrophic_failure_penalizes_score():
    weaknesses = [
        weakness("rotation", 0.05),
        weakness("brightness", 0.05),
        weakness("compression", 0.05),
        weakness("occlusion", 0.90),
    ]

    result = calculate_robustness_score(
        weaknesses
    )

    assert result.worst_degradation == pytest.approx(
        0.90
    )

    assert result.score < 70.0


def test_negative_improvement_does_not_penalize_score():
    weaknesses = [
        weakness(
            "brightness",
            -0.05,
            confidence_drop=-0.02,
        ),
    ]

    result = calculate_robustness_score(
        weaknesses
    )

    assert result.score == 100.0
    assert result.grade == "A"


def test_degradation_is_clamped_to_one():
    weaknesses = [
        weakness(
            "blur",
            1.50,
        ),
    ]

    result = calculate_robustness_score(
        weaknesses
    )

    assert result.score == 0.0
    assert result.grade == "F"
    assert result.status == "Critical"