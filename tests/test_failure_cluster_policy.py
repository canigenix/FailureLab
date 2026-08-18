import pytest

from failurelab.failure_cluster_policy import (
    FailureClusterPolicy,
    evaluate_failure_cluster_policy,
)
from failurelab.failure_cluster_report import (
    FailureClusterReport,
)
from failurelab.failure_clusters import (
    FailureCluster,
)


def build_report():
    return FailureClusterReport(
        suite_name="cluster-policy-test",
        minimum_correlation=0.75,
        clusters=[
            FailureCluster(
                stresses=[
                    "blur",
                    "noise",
                    "compression",
                ],
                pair_count=2,
                mean_correlation=0.85,
            ),
            FailureCluster(
                stresses=[
                    "brightness",
                    "rotation",
                ],
                pair_count=1,
                mean_correlation=0.80,
            ),
        ],
    )


def test_cluster_policy_passes():
    evaluation = evaluate_failure_cluster_policy(
        build_report(),
        FailureClusterPolicy(
            maximum_clusters=2,
            maximum_cluster_size=3,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "passed"


def test_cluster_policy_fails_cluster_count():
    evaluation = evaluate_failure_cluster_policy(
        build_report(),
        FailureClusterPolicy(
            maximum_clusters=1,
        ),
    )

    assert not evaluation.passed

    assert (
        evaluation.violations[0].metric
        == "cluster_count"
    )


def test_cluster_policy_fails_largest_cluster():
    evaluation = evaluate_failure_cluster_policy(
        build_report(),
        FailureClusterPolicy(
            maximum_cluster_size=2,
        ),
    )

    assert not evaluation.passed

    assert (
        evaluation.violations[0].metric
        == "largest_cluster_size"
    )


def test_cluster_policy_rejects_negative_limit():
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        evaluate_failure_cluster_policy(
            build_report(),
            FailureClusterPolicy(
                maximum_cluster_size=-1,
            ),
        )