from __future__ import annotations

from dataclasses import dataclass

from failurelab.failure_cluster_report import (
    FailureClusterReport,
)


@dataclass(frozen=True)
class FailureClusterPolicy:
    maximum_clusters: int | None = None
    maximum_cluster_size: int | None = None


@dataclass(frozen=True)
class FailureClusterPolicyViolation:
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class FailureClusterPolicyEvaluation:
    violations: list[FailureClusterPolicyViolation]

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def status(self) -> str:
        return (
            "passed"
            if self.passed
            else "failed"
        )


def evaluate_failure_cluster_policy(
    report: FailureClusterReport,
    policy: FailureClusterPolicy,
) -> FailureClusterPolicyEvaluation:
    if (
        policy.maximum_clusters is not None
        and policy.maximum_clusters < 0
    ):
        raise ValueError(
            "maximum_clusters cannot be negative."
        )

    if (
        policy.maximum_cluster_size is not None
        and policy.maximum_cluster_size < 0
    ):
        raise ValueError(
            "maximum_cluster_size cannot be negative."
        )

    violations = []

    if (
        policy.maximum_clusters is not None
        and report.cluster_count
        > policy.maximum_clusters
    ):
        violations.append(
            FailureClusterPolicyViolation(
                metric="cluster_count",
                observed=float(
                    report.cluster_count
                ),
                allowed=float(
                    policy.maximum_clusters
                ),
            )
        )

    largest = report.largest_cluster

    largest_size = (
        0
        if largest is None
        else len(largest.stresses)
    )

    if (
        policy.maximum_cluster_size is not None
        and largest_size
        > policy.maximum_cluster_size
    ):
        violations.append(
            FailureClusterPolicyViolation(
                metric="largest_cluster_size",
                observed=float(
                    largest_size
                ),
                allowed=float(
                    policy.maximum_cluster_size
                ),
            )
        )

    return FailureClusterPolicyEvaluation(
        violations=violations
    )