from failurelab.failure_persistence_report import (
    FailurePersistenceReport,
    build_failure_persistence_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def test_build_failure_persistence_report():
    report = build_failure_persistence_report(
        [
            FailureOccurrence("v1", "blur", 0.80),
            FailureOccurrence("v2", "blur", 0.70),
            FailureOccurrence("v3", "blur", 0.60),

            FailureOccurrence("v1", "rotation", 0.40),
            FailureOccurrence("v2", "rotation", 0.35),

            FailureOccurrence("v1", "crop", 0.20),
        ]
    )

    assert isinstance(
        report,
        FailurePersistenceReport,
    )

    assert report.total_failures == 3
    assert report.persistent_count == 1
    assert report.recurring_count == 1
    assert report.isolated_count == 1
    assert report.unresolved_count == 2


def test_persistence_report_highest_failure():
    report = build_failure_persistence_report(
        [
            FailureOccurrence("v1", "blur", 0.80),
            FailureOccurrence("v2", "blur", 0.70),
            FailureOccurrence("v3", "blur", 0.60),

            FailureOccurrence("v1", "rotation", 0.90),
        ]
    )

    assert report.highest_persistence is not None
    assert (
        report.highest_persistence.failure_name
        == "blur"
    )


def test_persistence_report_empty():
    report = build_failure_persistence_report(
        []
    )

    assert report.total_failures == 0
    assert report.persistent_count == 0
    assert report.recurring_count == 0
    assert report.isolated_count == 0
    assert report.unresolved_count == 0
    assert report.highest_persistence is None