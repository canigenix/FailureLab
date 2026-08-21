from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    FailureTriageReport,
    build_failure_triage_report,
)


def test_build_failure_triage_report():
    report = build_failure_triage_report(
        [
            FailurePrioritySignal(
                "blur",
                failure_rate=0.80,
                prediction_flip_rate=0.70,
                affected_fraction=0.80,
            ),
            FailurePrioritySignal(
                "compression",
                failure_rate=0.55,
                prediction_flip_rate=0.40,
                affected_fraction=0.50,
            ),
            FailurePrioritySignal(
                "rotation",
                failure_rate=0.20,
                prediction_flip_rate=0.10,
                affected_fraction=0.20,
            ),
        ]
    )

    assert isinstance(
        report,
        FailureTriageReport,
    )

    assert report.total_failures == 3
    assert report.highest_priority is not None
    assert report.highest_priority.name == "blur"

    assert (
        report.priorities[0].score
        >= report.priorities[1].score
        >= report.priorities[2].score
    )


def test_failure_triage_counts_levels():
    report = build_failure_triage_report(
        [
            FailurePrioritySignal(
                "critical",
                failure_rate=1.0,
                prediction_flip_rate=1.0,
                affected_fraction=1.0,
            ),
            FailurePrioritySignal(
                "high",
                failure_rate=0.60,
                prediction_flip_rate=0.50,
                affected_fraction=0.50,
            ),
            FailurePrioritySignal(
    "medium",
    failure_rate=0.35,
    prediction_flip_rate=0.20,
    affected_fraction=0.20,
),
            
            FailurePrioritySignal(
                "low",
                failure_rate=0.10,
                prediction_flip_rate=0.05,
                affected_fraction=0.10,
            ),
        ]
    )

    assert report.critical_count == 1
    assert report.high_count == 1
    assert report.medium_count == 1
    assert report.low_count == 1


def test_failure_triage_actionable_count():
    report = build_failure_triage_report(
        [
            FailurePrioritySignal(
                "critical",
                failure_rate=1.0,
                prediction_flip_rate=1.0,
                affected_fraction=1.0,
            ),
            FailurePrioritySignal(
                "high",
                failure_rate=0.60,
                prediction_flip_rate=0.50,
                affected_fraction=0.50,
            ),
            FailurePrioritySignal(
                "low",
                failure_rate=0.05,
                prediction_flip_rate=0.02,
                affected_fraction=0.05,
            ),
        ]
    )

    assert report.actionable_count == 2


def test_failure_triage_empty_input():
    report = build_failure_triage_report(
        []
    )

    assert report.total_failures == 0
    assert report.highest_priority is None
    assert report.priorities == ()
    assert report.critical_count == 0
    assert report.high_count == 0
    assert report.medium_count == 0
    assert report.low_count == 0
    assert report.actionable_count == 0


def test_failure_triage_preserves_priority_order():
    report = build_failure_triage_report(
        [
            FailurePrioritySignal(
                "low",
                failure_rate=0.10,
                prediction_flip_rate=0.05,
                affected_fraction=0.10,
            ),
            FailurePrioritySignal(
                "critical",
                failure_rate=1.0,
                prediction_flip_rate=1.0,
                affected_fraction=1.0,
            ),
            FailurePrioritySignal(
                "medium",
                failure_rate=0.30,
                prediction_flip_rate=0.20,
                affected_fraction=0.20,
            ),
        ]
    )

    assert [
        priority.name
        for priority in report.priorities
    ] == [
        "critical",
        "medium",
        "low",
    ]