from __future__ import annotations

from dataclasses import dataclass

from failurelab.cross_stress_report import (
    CrossStressReport,
)


@dataclass(frozen=True)
class CrossStressPolicy:
    maximum_systemic_classes: int | None = None
    maximum_systemic_fraction: float | None = None


@dataclass(frozen=True)
class CrossStressPolicyViolation:
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class CrossStressPolicyEvaluation:
    violations: list[CrossStressPolicyViolation]

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


def evaluate_cross_stress_policy(
    report: CrossStressReport,
    policy: CrossStressPolicy,
) -> CrossStressPolicyEvaluation:
    if (
        policy.maximum_systemic_classes is not None
        and policy.maximum_systemic_classes < 0
    ):
        raise ValueError(
            "maximum_systemic_classes cannot be negative."
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

    if report.class_count == 0:
        systemic_fraction = 0.0
    else:
        systemic_fraction = (
            report.systemic_count
            / report.class_count
        )

    if (
        policy.maximum_systemic_classes is not None
        and report.systemic_count
        > policy.maximum_systemic_classes
    ):
        violations.append(
            CrossStressPolicyViolation(
                metric="systemic_classes",
                observed=float(
                    report.systemic_count
                ),
                allowed=float(
                    policy.maximum_systemic_classes
                ),
            )
        )

    if (
        policy.maximum_systemic_fraction is not None
        and systemic_fraction
        > policy.maximum_systemic_fraction
    ):
        violations.append(
            CrossStressPolicyViolation(
                metric="systemic_fraction",
                observed=systemic_fraction,
                allowed=(
                    policy.maximum_systemic_fraction
                ),
            )
        )

    return CrossStressPolicyEvaluation(
        violations=violations
    )