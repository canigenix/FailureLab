import pytest

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.failure_triage_policy import (
    FailureTriagePolicyResult,
    evaluate_failure_triage_policy,
)


def make_report():
    return build_failure_triage_report(
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
                failure_rate=0.10,
                prediction_flip_rate=0.05,
                affected_fraction=0.10,
            ),
        ]
    )


def test_triage_policy_result_type():
    report = build_failure_triage_report(
        []
    )

    result = evaluate_failure_triage_policy(
        report
    )

    assert isinstance(
        result,
        FailureTriagePolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_triage_policy_rejects_critical_failures():
    result = evaluate_failure_triage_policy(
        make_report()
    )

    assert result.passed is False

    assert any(
        "Critical failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_triage_policy_limits_high_failures():
    result = evaluate_failure_triage_policy(
        make_report(),
        max_critical=10,
        max_high=0,
    )

    assert result.passed is False

    assert any(
        "High-priority failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_triage_policy_limits_actionable_failures():
    result = evaluate_failure_triage_policy(
        make_report(),
        max_critical=10,
        max_actionable=1,
    )

    assert result.passed is False

    assert any(
        "Actionable failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_triage_policy_limits_priority_score():
    result = evaluate_failure_triage_policy(
        make_report(),
        max_critical=10,
        max_priority_score=0.90,
    )

    assert result.passed is False

    assert any(
        "Highest priority score exceeded limit"
        in violation
        for violation in result.violations
    )


def test_triage_policy_can_pass_configured_limits():
    result = evaluate_failure_triage_policy(
        make_report(),
        max_critical=1,
        max_high=1,
        max_actionable=2,
        max_priority_score=1.0,
    )

    assert result.passed is True
    assert result.violations == ()


def test_triage_policy_rejects_invalid_limits():
    report = build_failure_triage_report(
        []
    )

    with pytest.raises(
        ValueError,
        match="max_critical",
    ):
        evaluate_failure_triage_policy(
            report,
            max_critical=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_high",
    ):
        evaluate_failure_triage_policy(
            report,
            max_high=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_actionable",
    ):
        evaluate_failure_triage_policy(
            report,
            max_actionable=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_priority_score",
    ):
        evaluate_failure_triage_policy(
            report,
            max_priority_score=1.1,
        )