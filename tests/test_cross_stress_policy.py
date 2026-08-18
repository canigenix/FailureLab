import pytest

from failurelab.cross_stress import (
    CrossStressClassResult,
)
from failurelab.cross_stress_policy import (
    CrossStressPolicy,
    evaluate_cross_stress_policy,
)
from failurelab.cross_stress_report import (
    CrossStressReport,
)


def result(
    class_index,
    severity,
):
    return CrossStressClassResult(
        class_index=class_index,
        stress_count=3,
        failure_stress_count=(
            3 if severity == "systemic" else 0
        ),
        failure_frequency=(
            1.0 if severity == "systemic" else 0.0
        ),
        mean_accuracy_drop=0.0,
        mean_confidence_drop=0.0,
        mean_failure_rate=0.0,
        mean_flip_rate=0.0,
        worst_stress="blur",
        worst_accuracy_drop=0.0,
        severity=severity,
    )


def build_report():
    return CrossStressReport(
        suite_name="production-vision",
        classes=[
            result(
                0,
                "systemic",
            ),
            result(
                1,
                "stable",
            ),
            result(
                2,
                "stable",
            ),
            result(
                3,
                "stable",
            ),
        ],
    )


def test_cross_stress_policy_passes():
    evaluation = evaluate_cross_stress_policy(
        build_report(),
        CrossStressPolicy(
            maximum_systemic_classes=1,
            maximum_systemic_fraction=0.25,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "passed"
    assert evaluation.violations == []


def test_cross_stress_policy_fails_systemic_count():
    evaluation = evaluate_cross_stress_policy(
        build_report(),
        CrossStressPolicy(
            maximum_systemic_classes=0,
        ),
    )

    assert not evaluation.passed
    assert evaluation.status == "failed"

    assert (
        evaluation.violations[0].metric
        == "systemic_classes"
    )


def test_cross_stress_policy_fails_systemic_fraction():
    evaluation = evaluate_cross_stress_policy(
        build_report(),
        CrossStressPolicy(
            maximum_systemic_fraction=0.20,
        ),
    )

    assert not evaluation.passed

    assert (
        evaluation.violations[0].metric
        == "systemic_fraction"
    )


def test_cross_stress_policy_rejects_invalid_fraction():
    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        evaluate_cross_stress_policy(
            build_report(),
            CrossStressPolicy(
                maximum_systemic_fraction=1.5,
            ),
        )