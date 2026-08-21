import pytest

from failurelab.failure_priority import (
    FailurePrioritySignal,
)
from failurelab.failure_triage import (
    build_failure_triage_report,
)
from failurelab.triage_comparison import (
    compare_failure_triage,
)
from failurelab.triage_comparison_policy import (
    TriageComparisonPolicyResult,
    evaluate_triage_comparison_policy,
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


def make_regression():
    baseline = make_report(
        ("blur", 0.20, 0.10, 0.20),
    )

    candidate = make_report(
        ("blur", 1.0, 1.0, 1.0),
    )

    return compare_failure_triage(
        baseline,
        candidate,
    )


def test_comparison_policy_result_type():
    report = make_report(
        ("blur", 0.20, 0.10, 0.20),
    )

    comparison = compare_failure_triage(
        report,
        report,
    )

    result = evaluate_triage_comparison_policy(
        comparison
    )

    assert isinstance(
        result,
        TriageComparisonPolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_comparison_policy_rejects_regression():
    result = evaluate_triage_comparison_policy(
        make_regression()
    )

    assert result.passed is False
    assert "Failure triage regressed." in (
        result.violations
    )


def test_comparison_policy_can_allow_regression():
    result = evaluate_triage_comparison_policy(
        make_regression(),
        allow_regression=True,
    )

    assert result.passed is True


def test_comparison_policy_limits_actionable_increase():
    result = evaluate_triage_comparison_policy(
        make_regression(),
        allow_regression=True,
        max_actionable_increase=0,
    )

    assert result.passed is False

    assert any(
        "Actionable failure increase exceeded limit"
        in violation
        for violation in result.violations
    )


def test_comparison_policy_limits_critical_increase():
    result = evaluate_triage_comparison_policy(
        make_regression(),
        allow_regression=True,
        max_critical_increase=0,
    )

    assert result.passed is False

    assert any(
        "Critical failure increase exceeded limit"
        in violation
        for violation in result.violations
    )


def test_comparison_policy_limits_score_increase():
    result = evaluate_triage_comparison_policy(
        make_regression(),
        allow_regression=True,
        max_score_increase=0.10,
    )

    assert result.passed is False

    assert any(
        "Priority score increase exceeded limit"
        in violation
        for violation in result.violations
    )


def test_comparison_policy_rejects_invalid_limits():
    comparison = make_regression()

    with pytest.raises(
        ValueError,
        match="max_actionable_increase",
    ):
        evaluate_triage_comparison_policy(
            comparison,
            max_actionable_increase=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_critical_increase",
    ):
        evaluate_triage_comparison_policy(
            comparison,
            max_critical_increase=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_score_increase",
    ):
        evaluate_triage_comparison_policy(
            comparison,
            max_score_increase=-0.01,
        )