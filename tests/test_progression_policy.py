import pytest

from failurelab import FailureLab
from failurelab.progression import (
    ProgressionPoint,
    summarize_progression_history,
)
from failurelab.progression_policy import (
    ProgressionPolicyResult,
    evaluate_progression_policy,
)


def test_progression_policy_passes_improving_history():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.30),
            ProgressionPoint("v2", 0.20),
            ProgressionPoint("v3", 0.10),
        ]
    )

    result = evaluate_progression_policy(report)

    assert isinstance(result, ProgressionPolicyResult)
    assert result.passed is True
    assert result.violations == ()


def test_progression_policy_fails_overall_regression():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
        ]
    )

    result = evaluate_progression_policy(
        report,
        max_overall_regression=0.05,
        max_regressed_transitions=1,
    )

    assert result.passed is False
    assert len(result.violations) == 1
    assert "Overall failure-rate regression" in result.violations[0]


def test_progression_policy_limits_regressed_transitions():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
            ProgressionPoint("v3", 0.15),
            ProgressionPoint("v4", 0.25),
        ]
    )

    result = evaluate_progression_policy(
        report,
        max_overall_regression=1.0,
        max_regressed_transitions=1,
    )

    assert result.passed is False
    assert any(
        "Regressed transitions" in violation
        for violation in result.violations
    )


def test_progression_policy_can_reject_volatility():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.20),
            ProgressionPoint("v2", 0.10),
            ProgressionPoint("v3", 0.25),
            ProgressionPoint("v4", 0.12),
        ]
    )

    result = evaluate_progression_policy(
        report,
        max_overall_regression=1.0,
        max_regressed_transitions=10,
        allow_volatile=False,
    )

    assert result.passed is False
    assert (
        "Volatile progression histories are not allowed."
        in result.violations
    )


def test_progression_policy_can_allow_volatility():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.20),
            ProgressionPoint("v2", 0.10),
            ProgressionPoint("v3", 0.25),
            ProgressionPoint("v4", 0.12),
        ]
    )

    result = evaluate_progression_policy(
        report,
        max_overall_regression=1.0,
        max_regressed_transitions=10,
        allow_volatile=True,
    )

    assert result.passed is True


def test_progression_policy_reports_multiple_violations():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
            ProgressionPoint("v3", 0.15),
            ProgressionPoint("v4", 0.30),
        ]
    )

    result = evaluate_progression_policy(
        report,
        max_overall_regression=0.05,
        max_regressed_transitions=1,
        allow_volatile=False,
    )

    assert result.passed is False
    assert len(result.violations) == 3


def test_progression_policy_rejects_negative_regression_limit():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
        ]
    )

    with pytest.raises(
        ValueError,
        match="max_overall_regression",
    ):
        evaluate_progression_policy(
            report,
            max_overall_regression=-0.01,
        )


def test_progression_policy_rejects_negative_transition_limit():
    report = summarize_progression_history(
        [
            ProgressionPoint("v1", 0.10),
            ProgressionPoint("v2", 0.20),
        ]
    )

    with pytest.raises(
        ValueError,
        match="max_regressed_transitions",
    ):
        evaluate_progression_policy(
            report,
            max_regressed_transitions=-1,
        )


def test_failurelab_progression_policy_passes():
    report = FailureLab.progression(
        [
            ("v1", 0.30),
            ("v2", 0.20),
            ("v3", 0.10),
        ]
    )

    result = FailureLab.progression_policy(report)

    assert result.passed is True
    assert result.violations == ()


def test_failurelab_progression_policy_fails():
    report = FailureLab.progression(
        [
            ("v1", 0.10),
            ("v2", 0.20),
            ("v3", 0.15),
            ("v4", 0.30),
        ]
    )

    result = FailureLab.progression_policy(
        report,
        max_overall_regression=0.05,
        max_regressed_transitions=1,
        allow_volatile=False,
    )

    assert result.passed is False
    assert len(result.violations) == 3       