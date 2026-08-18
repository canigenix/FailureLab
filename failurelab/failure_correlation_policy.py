from __future__ import annotations

from dataclasses import dataclass

from failurelab.failure_correlation_report import (
    FailureCorrelationReport,
)


@dataclass(frozen=True)
class FailureCorrelationPolicy:
    maximum_correlation: float | None = None
    maximum_high_correlation_pairs: int | None = None
    high_correlation_threshold: float = 0.75


@dataclass(frozen=True)
class FailureCorrelationPolicyViolation:
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class FailureCorrelationPolicyEvaluation:
    violations: list[FailureCorrelationPolicyViolation]

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


def evaluate_failure_correlation_policy(
    report: FailureCorrelationReport,
    policy: FailureCorrelationPolicy,
) -> FailureCorrelationPolicyEvaluation:
    if (
        policy.maximum_correlation is not None
        and not 0.0
        <= policy.maximum_correlation
        <= 1.0
    ):
        raise ValueError(
            "maximum_correlation must be "
            "between 0.0 and 1.0."
        )

    if (
        policy.high_correlation_threshold < 0.0
        or policy.high_correlation_threshold > 1.0
    ):
        raise ValueError(
            "high_correlation_threshold must be "
            "between 0.0 and 1.0."
        )

    if (
        policy.maximum_high_correlation_pairs is not None
        and policy.maximum_high_correlation_pairs < 0
    ):
        raise ValueError(
            "maximum_high_correlation_pairs "
            "cannot be negative."
        )

    violations = []

    strongest = report.strongest_pair

    if (
        policy.maximum_correlation is not None
        and strongest is not None
        and strongest.correlation
        > policy.maximum_correlation
    ):
        violations.append(
            FailureCorrelationPolicyViolation(
                metric="maximum_correlation",
                observed=strongest.correlation,
                allowed=policy.maximum_correlation,
            )
        )

    high_pair_count = sum(
        row.correlation
        >= policy.high_correlation_threshold
        for row in report.correlations
    )

    if (
        policy.maximum_high_correlation_pairs is not None
        and high_pair_count
        > policy.maximum_high_correlation_pairs
    ):
        violations.append(
            FailureCorrelationPolicyViolation(
                metric="high_correlation_pairs",
                observed=float(high_pair_count),
                allowed=float(
                    policy.maximum_high_correlation_pairs
                ),
            )
        )

    return FailureCorrelationPolicyEvaluation(
        violations=violations
    )