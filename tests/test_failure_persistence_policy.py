import pytest

from failurelab.failure_persistence_policy import (
    FailurePersistencePolicyResult,
    evaluate_failure_persistence_policy,
)
from failurelab.failure_persistence_report import (
    build_failure_persistence_report,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def make_report():
    return build_failure_persistence_report(
        [
            FailureOccurrence("v1", "blur", 0.80),
            FailureOccurrence("v2", "blur", 0.70),
            FailureOccurrence("v3", "blur", 0.60),

            FailureOccurrence("v1", "rotation", 0.40),
            FailureOccurrence("v2", "rotation", 0.35),

            FailureOccurrence("v1", "crop", 0.20),
        ]
    )


def test_persistence_policy_result_type():
    report = build_failure_persistence_report(
        []
    )

    result = evaluate_failure_persistence_policy(
        report
    )

    assert isinstance(
        result,
        FailurePersistencePolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_persistence_policy_limits_persistent():
    result = evaluate_failure_persistence_policy(
        make_report(),
        max_persistent=0,
    )

    assert result.passed is False

    assert any(
        "Persistent failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_persistence_policy_limits_recurring():
    result = evaluate_failure_persistence_policy(
        make_report(),
        max_recurring=0,
    )

    assert result.passed is False

    assert any(
        "Recurring failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_persistence_policy_limits_unresolved():
    result = evaluate_failure_persistence_policy(
        make_report(),
        max_unresolved=1,
    )

    assert result.passed is False

    assert any(
        "Unresolved failures exceeded limit"
        in violation
        for violation in result.violations
    )


def test_persistence_policy_limits_recurrence_rate():
    result = evaluate_failure_persistence_policy(
        make_report(),
        max_recurrence_rate=0.90,
    )

    assert result.passed is False

    assert any(
        "Highest recurrence rate exceeded limit"
        in violation
        for violation in result.violations
    )


def test_persistence_policy_can_pass():
    result = evaluate_failure_persistence_policy(
        make_report(),
        max_persistent=1,
        max_recurring=1,
        max_unresolved=2,
        max_recurrence_rate=1.0,
    )

    assert result.passed is True
    assert result.violations == ()


def test_persistence_policy_rejects_invalid_limits():
    report = make_report()

    with pytest.raises(
        ValueError,
        match="max_persistent",
    ):
        evaluate_failure_persistence_policy(
            report,
            max_persistent=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_recurring",
    ):
        evaluate_failure_persistence_policy(
            report,
            max_recurring=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_unresolved",
    ):
        evaluate_failure_persistence_policy(
            report,
            max_unresolved=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_recurrence_rate",
    ):
        evaluate_failure_persistence_policy(
            report,
            max_recurrence_rate=1.1,
        )