from dataclasses import dataclass
from typing import Literal

from failurelab.evaluation_intelligence import (
    EvaluationIntelligence,
)


EvaluationGateStatus = Literal[
    "passed",
    "failed",
]


@dataclass(frozen=True)
class EvaluationGateResult:
    """Result of applying a release gate to evaluation intelligence."""

    status: EvaluationGateStatus
    passed: bool
    violations: tuple[str, ...]


def evaluate_intelligence_gate(
    intelligence: EvaluationIntelligence,
    *,
    maximum_failed_analyses: int = 0,
    allowed_health_statuses: tuple[str, ...] = (
        "healthy",
    ),
) -> EvaluationGateResult:
    """Evaluate combined model health against release-gate limits."""

    if maximum_failed_analyses < 0:
        raise ValueError(
            "maximum_failed_analyses cannot be negative."
        )

    if not allowed_health_statuses:
        raise ValueError(
            "allowed_health_statuses cannot be empty."
        )

    violations = []

    failed_analyses = (
        intelligence.summary.failed_analyses
    )

    health_status = (
        intelligence.health.status
    )

    if (
        failed_analyses
        > maximum_failed_analyses
    ):
        violations.append(
            "Failed analyses "
            f"{failed_analyses} exceed maximum "
            f"{maximum_failed_analyses}."
        )

    if (
        health_status
        not in allowed_health_statuses
    ):
        violations.append(
            f"Health status '{health_status}' "
            "is not allowed."
        )

    passed = not violations

    return EvaluationGateResult(
        status=(
            "passed"
            if passed
            else "failed"
        ),
        passed=passed,
        violations=tuple(
            violations
        ),
    )