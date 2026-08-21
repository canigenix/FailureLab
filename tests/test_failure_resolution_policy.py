import pytest

from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution_policy import (
    FailureResolutionPolicyResult,
    evaluate_failure_resolution_policy,
)
from failurelab.failure_resolution_report import (
    build_failure_resolution_report,
)


def make_report():
    return build_failure_resolution_report(
        [
            FailureOccurrence("v1", "blur", 0.80),
            FailureOccurrence("v2", "blur", 0.50),

            FailureOccurrence("v1", "rotation", 0.30),
            FailureOccurrence("v2", "rotation", 0.60),

            FailureOccurrence("v1", "crop", 0.40),
            FailureOccurrence("v2", "crop", 0.40),
        ]
    )


def test_resolution_policy_result_type():
    result = evaluate_failure_resolution_policy(
        make_report()
    )

    assert isinstance(
        result,
        FailureResolutionPolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_resolution_policy_limits_worsening():
    result = evaluate_failure_resolution_policy(
        make_report(),
        max_worsening=0,
    )

    assert result.passed is False

    assert any(
        "Worsening failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_resolution_policy_limits_unchanged():
    result = evaluate_failure_resolution_policy(
        make_report(),
        max_unchanged=0,
    )

    assert result.passed is False

    assert any(
        "Unchanged failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_resolution_policy_limits_unresolved():
    result = evaluate_failure_resolution_policy(
        make_report(),
        max_unresolved=1,
    )

    assert result.passed is False

    assert any(
        "Unresolved failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_resolution_policy_limits_score_regression():
    result = evaluate_failure_resolution_policy(
        make_report(),
        max_score_regression=0.20,
    )

    assert result.passed is False

    assert any(
        "Failure score regression exceeded limit"
        in violation
        for violation in result.violations
    )


def test_resolution_policy_can_pass():
    result = evaluate_failure_resolution_policy(
        make_report(),
        max_worsening=1,
        max_unchanged=1,
        max_unresolved=2,
        max_score_regression=0.30,
    )

    assert result.passed is True
    assert result.violations == ()


def test_resolution_policy_rejects_invalid_limits():
    report = make_report()

    with pytest.raises(
        ValueError,
        match="max_worsening",
    ):
        evaluate_failure_resolution_policy(
            report,
            max_worsening=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_unchanged",
    ):
        evaluate_failure_resolution_policy(
            report,
            max_unchanged=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_unresolved",
    ):
        evaluate_failure_resolution_policy(
            report,
            max_unresolved=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_score_regression",
    ):
        evaluate_failure_resolution_policy(
            report,
            max_score_regression=-0.01,
        )