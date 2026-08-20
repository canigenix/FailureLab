import pytest

from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_comparison import (
    compare_failure_signatures,
)
from failurelab.signature_policy import (
    SignaturePolicyResult,
    evaluate_signature_policy,
)


def build_comparison(
    baseline_signals,
    candidate_signals,
):
    baseline = build_failure_signature(
        baseline_signals
    )

    candidate = build_failure_signature(
        candidate_signals
    )

    return compare_failure_signatures(
        baseline,
        candidate,
    )


def test_signature_policy_passes_improvement():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.30, 0.10),
            StressFailureSignal("rotation", 0.20, 0.08),
        ],
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
        ],
    )

    result = evaluate_signature_policy(
        comparison
    )

    assert isinstance(
        result,
        SignaturePolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_signature_policy_rejects_failure_rate_increase():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
        ],
        [
            StressFailureSignal("blur", 0.30, 0.03),
            StressFailureSignal("rotation", 0.15, 0.02),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=0.05,
        max_flip_rate_increase=1.0,
        max_affected_stress_increase=10,
        allow_severity_regression=True,
    )

    assert result.passed is False
    assert any(
        "Mean failure-rate increase" in violation
        for violation in result.violations
    )


def test_signature_policy_rejects_flip_rate_increase():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.10, 0.02),
            StressFailureSignal("rotation", 0.05, 0.01),
        ],
        [
            StressFailureSignal("blur", 0.10, 0.20),
            StressFailureSignal("rotation", 0.05, 0.15),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=1.0,
        max_flip_rate_increase=0.05,
        max_affected_stress_increase=10,
        allow_severity_regression=True,
    )

    assert result.passed is False
    assert any(
        "prediction-flip-rate" in violation
        for violation in result.violations
    )


def test_signature_policy_rejects_affected_stress_increase():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.20, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
            StressFailureSignal("crop", 0.03, 0.01),
        ],
        [
            StressFailureSignal("blur", 0.20, 0.03),
            StressFailureSignal("rotation", 0.15, 0.02),
            StressFailureSignal("crop", 0.12, 0.01),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=1.0,
        max_flip_rate_increase=1.0,
        max_affected_stress_increase=1,
        allow_severity_regression=True,
    )

    assert result.passed is False
    assert any(
        "Affected-stress increase" in violation
        for violation in result.violations
    )


def test_signature_policy_can_reject_dominant_stress_change():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.30, 0.03),
            StressFailureSignal("rotation", 0.10, 0.02),
        ],
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.35, 0.02),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=1.0,
        max_flip_rate_increase=1.0,
        max_affected_stress_increase=10,
        allow_dominant_stress_change=False,
        allow_severity_regression=True,
    )

    assert result.passed is False
    assert any(
        "Dominant failure stress changed" in violation
        for violation in result.violations
    )


def test_signature_policy_reports_multiple_violations():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.10, 0.02),
            StressFailureSignal("rotation", 0.05, 0.01),
        ],
        [
            StressFailureSignal("blur", 0.20, 0.20),
            StressFailureSignal("rotation", 0.30, 0.15),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=0.01,
        max_flip_rate_increase=0.01,
        max_affected_stress_increase=0,
        allow_dominant_stress_change=False,
        allow_severity_regression=True,
    )

    assert result.passed is False
    assert len(result.violations) == 4


def test_signature_policy_rejects_negative_limits():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.10, 0.02),
        ],
        [
            StressFailureSignal("blur", 0.20, 0.03),
        ],
    )

    with pytest.raises(
        ValueError,
        match="max_failure_rate_increase",
    ):
        evaluate_signature_policy(
            comparison,
            max_failure_rate_increase=-0.01,
        )

    with pytest.raises(
        ValueError,
        match="max_flip_rate_increase",
    ):
        evaluate_signature_policy(
            comparison,
            max_flip_rate_increase=-0.01,
        )

    with pytest.raises(
        ValueError,
        match="max_affected_stress_increase",
    ):
        evaluate_signature_policy(
            comparison,
            max_affected_stress_increase=-1,
        )


def test_signature_policy_rejects_severity_regression():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.04, 0.02),
            StressFailureSignal("rotation", 0.03, 0.01),
        ],
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.18, 0.04),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=1.0,
        max_flip_rate_increase=1.0,
        max_affected_stress_increase=10,
    )

    assert result.passed is False
    assert any(
        "Failure signature severity regressed" in violation
        for violation in result.violations
    )


def test_signature_policy_can_allow_severity_regression():
    comparison = build_comparison(
        [
            StressFailureSignal("blur", 0.04, 0.02),
            StressFailureSignal("rotation", 0.03, 0.01),
        ],
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.18, 0.04),
        ],
    )

    result = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=1.0,
        max_flip_rate_increase=1.0,
        max_affected_stress_increase=10,
        allow_severity_regression=True,
    )

    assert result.passed is True