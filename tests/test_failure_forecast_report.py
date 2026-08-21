import pytest

from failurelab.failure_forecast_report import (
    FailureForecastReport,
    build_failure_forecast_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def test_build_failure_forecast_report():
    report = build_failure_forecast_report(
        [
            FailureOccurrence(
                "v1", "blur", 0.80
            ),
            FailureOccurrence(
                "v2", "blur", 0.60
            ),
            FailureOccurrence(
                "v3", "blur", 0.40
            ),

            FailureOccurrence(
                "v1", "rotation", 0.20
            ),
            FailureOccurrence(
                "v2", "rotation", 0.40
            ),
            FailureOccurrence(
                "v3", "rotation", 0.60
            ),

            FailureOccurrence(
                "v1", "crop", 0.40
            ),
            FailureOccurrence(
                "v2", "crop", 0.40
            ),

            FailureOccurrence(
                "v1", "compression", 0.30
            ),
        ]
    )

    assert isinstance(
        report,
        FailureForecastReport,
    )

    assert report.total_failures == 4
    assert report.improving_count == 1
    assert report.stable_count == 1
    assert report.worsening_count == 1
    assert (
        report.insufficient_history_count
        == 1
    )


def test_report_tracks_highest_projected_risk():
    report = build_failure_forecast_report(
        [
            FailureOccurrence(
                "v1", "blur", 0.80
            ),
            FailureOccurrence(
                "v2", "blur", 0.60
            ),

            FailureOccurrence(
                "v1", "rotation", 0.20
            ),
            FailureOccurrence(
                "v2", "rotation", 0.60
            ),
        ]
    )

    assert (
        report.highest_projected_risk
        is not None
    )

    assert (
        report.highest_projected_risk.failure_name
        == "rotation"
    )

    assert (
        report.highest_projected_risk.projected_score
        == pytest.approx(1.0)
    )


def test_report_counts_projected_risk():
    report = build_failure_forecast_report(
        [
            FailureOccurrence(
                "v1", "blur", 0.80
            ),
            FailureOccurrence(
                "v2", "blur", 0.60
            ),

            FailureOccurrence(
                "v1", "rotation", 0.20
            ),
            FailureOccurrence(
                "v2", "rotation", 0.60
            ),

            FailureOccurrence(
                "v1", "crop", 0.50
            ),
            FailureOccurrence(
                "v2", "crop", 0.50
            ),
        ]
    )

    assert report.projected_risk_count == 2


def test_report_respects_tolerance():
    report = build_failure_forecast_report(
        [
            FailureOccurrence(
                "v1", "blur", 0.50
            ),
            FailureOccurrence(
                "v2", "blur", 0.505
            ),
        ],
        tolerance=0.01,
    )

    assert report.stable_count == 1
    assert report.worsening_count == 0


def test_empty_forecast_report():
    report = build_failure_forecast_report(
        []
    )

    assert report.total_failures == 0
    assert report.improving_count == 0
    assert report.stable_count == 0
    assert report.worsening_count == 0
    assert (
        report.insufficient_history_count
        == 0
    )
    assert report.projected_risk_count == 0
    assert report.highest_projected_risk is None