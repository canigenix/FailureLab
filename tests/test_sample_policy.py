import pytest

from failurelab.sample_analysis import (
    SampleFailureResult,
)
from failurelab.sample_policy import (
    SampleFailurePolicy,
    evaluate_sample_failure_policy,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


def sample(
    sample_index,
    severity,
):
    systemic = severity == "systemic"

    return SampleFailureResult(
        sample_index=sample_index,
        target=0,
        stress_count=3,
        failure_stress_count=(
            3 if systemic else 0
        ),
        failure_frequency=(
            1.0 if systemic else 0.0
        ),
        flip_stress_count=(
            3 if systemic else 0
        ),
        flip_frequency=(
            1.0 if systemic else 0.0
        ),
        failed_stresses=(
            ["blur", "noise", "brightness"]
            if systemic
            else []
        ),
        flipped_stresses=(
            ["blur", "noise", "brightness"]
            if systemic
            else []
        ),
        severity=severity,
    )


def build_report():
    return SampleFailureReport(
        suite_name="sample-policy-test",
        samples=[
            sample(0, "systemic"),
            sample(1, "stable"),
            sample(2, "stable"),
            sample(3, "stable"),
        ],
    )


def test_sample_policy_passes():
    evaluation = evaluate_sample_failure_policy(
        build_report(),
        SampleFailurePolicy(
            maximum_systemic_samples=1,
            maximum_systemic_fraction=0.25,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "passed"
    assert evaluation.violations == []


def test_sample_policy_fails_systemic_count():
    evaluation = evaluate_sample_failure_policy(
        build_report(),
        SampleFailurePolicy(
            maximum_systemic_samples=0,
        ),
    )

    assert not evaluation.passed

    assert (
        evaluation.violations[0].metric
        == "systemic_samples"
    )


def test_sample_policy_fails_systemic_fraction():
    evaluation = evaluate_sample_failure_policy(
        build_report(),
        SampleFailurePolicy(
            maximum_systemic_fraction=0.20,
        ),
    )

    assert not evaluation.passed

    assert (
        evaluation.violations[0].metric
        == "systemic_fraction"
    )


def test_sample_policy_rejects_invalid_fraction():
    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        evaluate_sample_failure_policy(
            build_report(),
            SampleFailurePolicy(
                maximum_systemic_fraction=1.5,
            ),
        )