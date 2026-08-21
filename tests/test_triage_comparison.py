import pytest

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.triage_comparison import (
    FailureTriageComparison,
    compare_failure_triage,
)


def make_report(*rows):
    return build_failure_triage_report(
        [
            FailurePrioritySignal(
                name=name,
                failure_rate=failure_rate,
                prediction_flip_rate=flip_rate,
                affected_fraction=affected_fraction,
            )
            for (
                name,
                failure_rate,
                flip_rate,
                affected_fraction,
            ) in rows
        ]
    )


def test_triage_comparison_improved():
    baseline = make_report(
        ("blur", 1.0, 1.0, 1.0),
        ("rotation", 0.60, 0.50, 0.50),
    )

    candidate = make_report(
        ("blur", 0.30, 0.20, 0.20),
        ("rotation", 0.10, 0.05, 0.10),
    )

    comparison = compare_failure_triage(
        baseline,
        candidate,
    )

    assert isinstance(
        comparison,
        FailureTriageComparison,
    )

    assert comparison.status == "improved"
    assert comparison.actionable_delta < 0
    assert comparison.critical_delta < 0
    assert comparison.highest_score_delta < 0


def test_triage_comparison_regressed():
    baseline = make_report(
        ("blur", 0.20, 0.10, 0.20),
    )

    candidate = make_report(
        ("blur", 1.0, 1.0, 1.0),
    )

    comparison = compare_failure_triage(
        baseline,
        candidate,
    )

    assert comparison.status == "regressed"
    assert comparison.actionable_delta > 0
    assert comparison.critical_delta > 0
    assert comparison.highest_score_delta > 0


def test_triage_comparison_stable():
    baseline = make_report(
        ("blur", 0.30, 0.20, 0.20),
    )

    candidate = make_report(
        ("blur", 0.30, 0.20, 0.20),
    )

    comparison = compare_failure_triage(
        baseline,
        candidate,
    )

    assert comparison.status == "stable"
    assert comparison.actionable_delta == 0
    assert comparison.critical_delta == 0
    assert comparison.highest_score_delta == pytest.approx(
        0.0
    )


def test_triage_comparison_respects_score_tolerance():
    baseline = make_report(
        ("blur", 0.30, 0.20, 0.20),
    )

    candidate = make_report(
        ("blur", 0.305, 0.20, 0.20),
    )

    comparison = compare_failure_triage(
        baseline,
        candidate,
        score_tolerance=0.01,
    )

    assert comparison.status == "stable"


def test_triage_comparison_rejects_negative_tolerance():
    report = make_report(
        ("blur", 0.30, 0.20, 0.20),
    )

    with pytest.raises(
        ValueError,
        match="score_tolerance",
    ):
        compare_failure_triage(
            report,
            report,
            score_tolerance=-0.01,
        )