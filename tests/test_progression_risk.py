import pytest

from failurelab.progression import ProgressionPoint
from failurelab.progression_risk import (
    CheckpointRisk,
    highest_risk_checkpoint,
    score_checkpoint_risk,
)


def test_score_checkpoint_risk():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.20),
        ProgressionPoint("v3", 0.15),
    ]

    risks = score_checkpoint_risk(points)

    assert len(risks) == 3

    assert risks[0] == CheckpointRisk(
        label="v1",
        failure_rate=0.10,
        regression_from_previous=None,
        risk_score=0.10,
    )

    assert risks[1].regression_from_previous == pytest.approx(0.10)
    assert risks[1].risk_score == pytest.approx(0.30)

    assert risks[2].regression_from_previous == pytest.approx(0.0)
    assert risks[2].risk_score == pytest.approx(0.15)


def test_highest_risk_checkpoint():
    points = [
        ProgressionPoint("v1", 0.10),
        ProgressionPoint("v2", 0.20),
        ProgressionPoint("v3", 0.18),
        ProgressionPoint("v4", 0.30),
    ]

    risk = highest_risk_checkpoint(points)

    assert risk.label == "v4"
    assert risk.failure_rate == pytest.approx(0.30)
    assert risk.regression_from_previous == pytest.approx(0.12)
    assert risk.risk_score == pytest.approx(0.42)


def test_improvement_does_not_add_regression_risk():
    points = [
        ProgressionPoint("v1", 0.30),
        ProgressionPoint("v2", 0.20),
    ]

    risks = score_checkpoint_risk(points)

    assert risks[1].regression_from_previous == pytest.approx(0.0)
    assert risks[1].risk_score == pytest.approx(0.20)


def test_highest_risk_checkpoint_requires_points():
    with pytest.raises(
        ValueError,
        match="At least one progression point",
    ):
        highest_risk_checkpoint([])