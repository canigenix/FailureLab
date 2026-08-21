import pytest
from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution_report import (
    FailureResolutionReport,
    build_failure_resolution_report,
)


def test_build_failure_resolution_report():
    report = build_failure_resolution_report(
        [
            FailureOccurrence("v1", "blur", 0.80),
            FailureOccurrence("v2", "blur", 0.50),

            FailureOccurrence("v1", "rotation", 0.30),
            FailureOccurrence("v2", "rotation", 0.60),

            FailureOccurrence("v1", "crop", 0.40),
            FailureOccurrence("v2", "crop", 0.40),

            FailureOccurrence("v1", "compression", 0.20),
        ]
    )

    assert isinstance(
        report,
        FailureResolutionReport,
    )

    assert report.total_failures == 4
    assert report.improving_count == 1
    assert report.worsening_count == 1
    assert report.unchanged_count == 1
    assert report.insufficient_history_count == 1
    assert report.unresolved_count == 2


def test_resolution_report_tracks_worst_regression():
    report = build_failure_resolution_report(
        [
            FailureOccurrence("v1", "blur", 0.30),
            FailureOccurrence("v2", "blur", 0.50),

            FailureOccurrence("v1", "rotation", 0.20),
            FailureOccurrence("v2", "rotation", 0.70),
        ]
    )

    assert report.worst_resolution is not None

    assert (
        report.worst_resolution.failure_name
        == "rotation"
    )

    assert report.worst_resolution.score_delta == pytest.approx(
    0.50
)


def test_resolution_report_respects_tolerance():
    report = build_failure_resolution_report(
        [
            FailureOccurrence("v1", "blur", 0.50),
            FailureOccurrence("v2", "blur", 0.505),
        ],
        tolerance=0.01,
    )

    assert report.unchanged_count == 1
    assert report.worsening_count == 0


def test_resolution_report_empty():
    report = build_failure_resolution_report(
        []
    )

    assert report.total_failures == 0
    assert report.improving_count == 0
    assert report.unchanged_count == 0
    assert report.worsening_count == 0
    assert report.insufficient_history_count == 0
    assert report.unresolved_count == 0
    assert report.worst_resolution is None