import pytest

from failurelab.failure_correlation import (
    StressCorrelationResult,
)
from failurelab.failure_correlation_policy import (
    FailureCorrelationPolicy,
    evaluate_failure_correlation_policy,
)
from failurelab.failure_correlation_report import (
    FailureCorrelationReport,
)


def build_report():
    return FailureCorrelationReport(
        suite_name="correlation-policy-test",
        correlations=[
            StressCorrelationResult(
                stress_a="blur",
                stress_b="noise",
                shared_failures=8,
                total_failures=10,
                correlation=0.8,
            ),
            StressCorrelationResult(
                stress_a="blur",
                stress_b="brightness",
                shared_failures=2,
                total_failures=10,
                correlation=0.2,
            ),
        ],
    )


def test_correlation_policy_passes():
    evaluation = evaluate_failure_correlation_policy(
        build_report(),
        FailureCorrelationPolicy(
            maximum_correlation=0.8,
            maximum_high_correlation_pairs=1,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "passed"


def test_correlation_policy_fails_maximum():
    evaluation = evaluate_failure_correlation_policy(
        build_report(),
        FailureCorrelationPolicy(
            maximum_correlation=0.7,
        ),
    )

    assert not evaluation.passed
    assert (
        evaluation.violations[0].metric
        == "maximum_correlation"
    )


def test_correlation_policy_fails_pair_count():
    evaluation = evaluate_failure_correlation_policy(
        build_report(),
        FailureCorrelationPolicy(
            maximum_high_correlation_pairs=0,
            high_correlation_threshold=0.75,
        ),
    )

    assert not evaluation.passed
    assert (
        evaluation.violations[0].metric
        == "high_correlation_pairs"
    )


def test_correlation_policy_rejects_invalid_threshold():
    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        evaluate_failure_correlation_policy(
            build_report(),
            FailureCorrelationPolicy(
                maximum_correlation=1.5,
            ),
        )