from __future__ import annotations

from dataclasses import dataclass

from failurelab.sample_report import (
    SampleFailureReport,
)


@dataclass(frozen=True)
class SampleFailurePolicy:
    maximum_systemic_samples: int | None = None
    maximum_systemic_fraction: float | None = None


@dataclass(frozen=True)
class SampleFailurePolicyViolation:
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class SampleFailurePolicyEvaluation:
    violations: list[SampleFailurePolicyViolation]

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


def evaluate_sample_failure_policy(
    report: SampleFailureReport,
    policy: SampleFailurePolicy,
) -> SampleFailurePolicyEvaluation:
    if (
        policy.maximum_systemic_samples is not None
        and policy.maximum_systemic_samples < 0
    ):
        raise ValueError(
            "maximum_systemic_samples cannot be negative."
        )

    if (
        policy.maximum_systemic_fraction is not None
        and not 0.0
        <= policy.maximum_systemic_fraction
        <= 1.0
    ):
        raise ValueError(
            "maximum_systemic_fraction must be "
            "between 0.0 and 1.0."
        )

    violations = []

    if report.sample_count == 0:
        systemic_fraction = 0.0
    else:
        systemic_fraction = (
            report.systemic_count
            / report.sample_count
        )

    if (
        policy.maximum_systemic_samples is not None
        and report.systemic_count
        > policy.maximum_systemic_samples
    ):
        violations.append(
            SampleFailurePolicyViolation(
                metric="systemic_samples",
                observed=float(
                    report.systemic_count
                ),
                allowed=float(
                    policy.maximum_systemic_samples
                ),
            )
        )

    if (
        policy.maximum_systemic_fraction is not None
        and systemic_fraction
        > policy.maximum_systemic_fraction
    ):
        violations.append(
            SampleFailurePolicyViolation(
                metric="systemic_fraction",
                observed=systemic_fraction,
                allowed=(
                    policy.maximum_systemic_fraction
                ),
            )
        )

    return SampleFailurePolicyEvaluation(
        violations=violations
    )