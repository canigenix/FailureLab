import pytest

from failurelab.api import FailureLab
from failurelab.progression import (
    ProgressionHistoryReport,
    ProgressionPoint,
)


def test_failurelab_progression_accepts_tuples():
    report = FailureLab.progression(
        [
            ("v1", 0.20),
            ("v2", 0.15),
            ("v3", 0.10),
        ]
    )

    assert isinstance(report, ProgressionHistoryReport)
    assert report.overall_status == "improved"
    assert report.trend == "improving"
    assert report.overall_delta == pytest.approx(-0.10)


def test_failurelab_progression_accepts_progression_points():
    report = FailureLab.progression(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
            ProgressionPoint("v3", 0.30),
        ]
    )

    assert isinstance(report, ProgressionHistoryReport)
    assert report.overall_status == "regressed"
    assert report.trend == "degrading"
    assert report.regressed_count == 2


def test_failurelab_progression_detects_volatility():
    report = FailureLab.progression(
        [
            ("v1", 0.20),
            ("v2", 0.10),
            ("v3", 0.25),
            ("v4", 0.12),
        ]
    )

    assert report.overall_status == "improved"
    assert report.trend == "volatile"
    assert report.improved_count == 2
    assert report.regressed_count == 1


def test_failurelab_progression_respects_tolerance():
    report = FailureLab.progression(
        [
            ("v1", 0.10),
            ("v2", 0.105),
        ],
        tolerance=0.01,
    )

    assert report.overall_status == "stable"
    assert report.trend == "stable"
    assert report.stable_count == 1


def test_failurelab_progression_requires_two_points():
    with pytest.raises(
        ValueError,
        match="At least two progression points",
    ):
        FailureLab.progression(
            [
                ("v1", 0.10),
            ]
        )


def test_failurelab_progression_risk_scores_checkpoints():
    risks = FailureLab.progression_risk(
        [
            ("v1", 0.10),
            ("v2", 0.20),
            ("v3", 0.15),
        ]
    )

    assert len(risks) == 3
    assert risks[0].label == "v1"
    assert risks[1].risk_score == pytest.approx(0.30)
    assert risks[2].risk_score == pytest.approx(0.15)


def test_failurelab_highest_progression_risk():
    risk = FailureLab.highest_progression_risk(
        [
            ("v1", 0.10),
            ("v2", 0.20),
            ("v3", 0.18),
            ("v4", 0.30),
        ]
    )

    assert risk.label == "v4"
    assert risk.failure_rate == pytest.approx(0.30)
    assert risk.regression_from_previous == pytest.approx(0.12)
    assert risk.risk_score == pytest.approx(0.42)


def test_failurelab_save_progression_json(tmp_path):
    report = FailureLab.progression(
        [
            ("v1", 0.20),
            ("v2", 0.10),
            ("v3", 0.25),
            ("v4", 0.12),
        ]
    )

    policy = FailureLab.progression_policy(
        report,
        max_overall_regression=1.0,
        max_regressed_transitions=10,
        allow_volatile=True,
    )

    risks = FailureLab.progression_risk(
        [
            ("v1", 0.20),
            ("v2", 0.10),
            ("v3", 0.25),
            ("v4", 0.12),
        ]
    )

    path = tmp_path / "progression.json"

    result = FailureLab.save_progression_json(
        report,
        path,
        policy=policy,
        risks=risks,
    )

    assert result == path
    assert path.exists()