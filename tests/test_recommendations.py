import pytest

from failurelab.recommendations import (
    build_recommendations,
)
from failurelab.vision_report import VisionWeakness


def make_weakness(
    name,
    severity,
):
    return VisionWeakness(
        name=name,
        severity=severity,
        top1_drop=0.20,
        top5_drop=0.10,
        confidence_drop=0.15,
    )


def test_recommendations_skip_low_severity_by_default():
    weaknesses = [
        make_weakness(
            "brightness",
            "low",
        ),
        make_weakness(
            "blur",
            "critical",
        ),
    ]

    recommendations = build_recommendations(
        weaknesses
    )

    assert len(recommendations) == 1
    assert recommendations[0].weakness_name == "blur"


def test_recommendation_contains_actionable_guidance():
    weaknesses = [
        make_weakness(
            "occlusion",
            "critical",
        )
    ]

    recommendations = build_recommendations(
        weaknesses
    )

    recommendation = recommendations[0]

    assert recommendation.diagnosis
    assert recommendation.likely_cause
    assert recommendation.suggested_action

    assert "occlusion" in (
        recommendation.suggested_action.lower()
    )


def test_rejects_unknown_minimum_severity():
    with pytest.raises(ValueError):
        build_recommendations(
            [],
            minimum_severity="extreme",
        )