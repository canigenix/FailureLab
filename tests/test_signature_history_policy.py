import pytest

from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_history import (
    SignatureCheckpoint,
    analyze_signature_history,
)
from failurelab.signature_history_policy import (
    SignatureHistoryPolicyResult,
    evaluate_signature_history_policy,
)


def make_signature(*rows):
    return build_failure_signature(
        [
            StressFailureSignal(
                stress_name=name,
                failure_rate=failure_rate,
                prediction_flip_rate=flip_rate,
            )
            for name, failure_rate, flip_rate in rows
        ]
    )


def make_improving_report():
    return analyze_signature_history(
        [
            SignatureCheckpoint(
                "v1",
                make_signature(
                    ("blur", 0.30, 0.10),
                    ("rotation", 0.20, 0.08),
                ),
            ),
            SignatureCheckpoint(
                "v2",
                make_signature(
                    ("blur", 0.10, 0.03),
                    ("rotation", 0.05, 0.02),
                ),
            ),
        ]
    )


def make_degrading_report():
    return analyze_signature_history(
        [
            SignatureCheckpoint(
                "v1",
                make_signature(
                    ("blur", 0.03, 0.01),
                    ("rotation", 0.02, 0.01),
                ),
            ),
            SignatureCheckpoint(
                "v2",
                make_signature(
                    ("blur", 0.20, 0.05),
                    ("rotation", 0.18, 0.04),
                ),
            ),
        ]
    )


def test_signature_history_policy_passes_improvement():
    report = make_improving_report()

    result = evaluate_signature_history_policy(
        report
    )

    assert isinstance(
        result,
        SignatureHistoryPolicyResult,
    )
    assert result.passed is True
    assert result.violations == ()


def test_signature_history_policy_rejects_regressions():
    report = make_degrading_report()

    result = evaluate_signature_history_policy(
        report
    )

    assert result.passed is False

    assert any(
        "Regressed signature transitions" in violation
        for violation in result.violations
    )


def test_signature_history_policy_rejects_severity_regression():
    report = make_degrading_report()

    result = evaluate_signature_history_policy(
        report,
        max_regressed_transitions=10,
    )

    assert result.passed is False

    assert any(
        "Signature severity regressions" in violation
        for violation in result.violations
    )


def test_signature_history_policy_limits_dominant_changes():
    report = analyze_signature_history(
        [
            SignatureCheckpoint(
                "v1",
                make_signature(
                    ("blur", 0.30, 0.05),
                    ("rotation", 0.05, 0.02),
                ),
            ),
            SignatureCheckpoint(
                "v2",
                make_signature(
                    ("blur", 0.05, 0.02),
                    ("rotation", 0.30, 0.05),
                ),
            ),
        ]
    )

    result = evaluate_signature_history_policy(
        report,
        max_regressed_transitions=10,
        max_severity_regressions=10,
        max_dominant_stress_changes=0,
    )

    assert result.passed is False

    assert any(
        "Dominant stress changes" in violation
        for violation in result.violations
    )


def test_signature_history_policy_rejects_volatile():
    report = analyze_signature_history(
        [
            SignatureCheckpoint(
                "v1",
                make_signature(
                    ("blur", 0.20, 0.05),
                    ("rotation", 0.10, 0.03),
                ),
            ),
            SignatureCheckpoint(
                "v2",
                make_signature(
                    ("blur", 0.10, 0.03),
                    ("rotation", 0.05, 0.02),
                ),
            ),
            SignatureCheckpoint(
                "v3",
                make_signature(
                    ("blur", 0.25, 0.08),
                    ("rotation", 0.15, 0.05),
                ),
            ),
        ]
    )

    result = evaluate_signature_history_policy(
        report,
        max_regressed_transitions=10,
        max_severity_regressions=10,
    )

    assert result.passed is False
    assert "Signature history trend is volatile." in (
        result.violations
    )


def test_signature_history_policy_can_allow_volatile():
    report = analyze_signature_history(
        [
            SignatureCheckpoint(
                "v1",
                make_signature(
                    ("blur", 0.20, 0.05),
                    ("rotation", 0.10, 0.03),
                ),
            ),
            SignatureCheckpoint(
                "v2",
                make_signature(
                    ("blur", 0.10, 0.03),
                    ("rotation", 0.05, 0.02),
                ),
            ),
            SignatureCheckpoint(
                "v3",
                make_signature(
                    ("blur", 0.25, 0.08),
                    ("rotation", 0.15, 0.05),
                ),
            ),
        ]
    )

    result = evaluate_signature_history_policy(
        report,
        max_regressed_transitions=10,
        max_severity_regressions=10,
        allow_volatile=True,
    )

    assert result.passed is True


def test_signature_history_policy_rejects_negative_limits():
    report = make_improving_report()

    with pytest.raises(
        ValueError,
        match="max_regressed_transitions",
    ):
        evaluate_signature_history_policy(
            report,
            max_regressed_transitions=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_severity_regressions",
    ):
        evaluate_signature_history_policy(
            report,
            max_severity_regressions=-1,
        )

    with pytest.raises(
        ValueError,
        match="max_dominant_stress_changes",
    ):
        evaluate_signature_history_policy(
            report,
            max_dominant_stress_changes=-1,
        )