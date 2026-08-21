from dataclasses import dataclass

from failurelab.failure_triage import (
    FailureTriageReport,
)


@dataclass(frozen=True)
class FailureTriagePolicyResult:
    """Result of evaluating a failure triage report."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_failure_triage_policy(
    report: FailureTriageReport,
    *,
    max_critical: int = 0,
    max_high: int | None = None,
    max_actionable: int | None = None,
    max_priority_score: float | None = None,
) -> FailureTriagePolicyResult:
    """Evaluate failure triage against policy limits."""

    if max_critical < 0:
        raise ValueError(
            "max_critical cannot be negative."
        )

    if max_high is not None and max_high < 0:
        raise ValueError(
            "max_high cannot be negative."
        )

    if (
        max_actionable is not None
        and max_actionable < 0
    ):
        raise ValueError(
            "max_actionable cannot be negative."
        )

    if (
        max_priority_score is not None
        and not 0.0 <= max_priority_score <= 1.0
    ):
        raise ValueError(
            "max_priority_score must be between 0.0 and 1.0."
        )

    violations = []

    if report.critical_count > max_critical:
        violations.append(
            "Critical failures exceeded limit: "
            f"{report.critical_count} > {max_critical}."
        )

    if (
        max_high is not None
        and report.high_count > max_high
    ):
        violations.append(
            "High-priority failures exceeded limit: "
            f"{report.high_count} > {max_high}."
        )

    if (
        max_actionable is not None
        and report.actionable_count > max_actionable
    ):
        violations.append(
            "Actionable failures exceeded limit: "
            f"{report.actionable_count} > {max_actionable}."
        )

    if (
        max_priority_score is not None
        and report.highest_priority is not None
        and report.highest_priority.score
        > max_priority_score
    ):
        violations.append(
            "Highest priority score exceeded limit: "
            f"{report.highest_priority.score:.4f} > "
            f"{max_priority_score:.4f}."
        )

    return FailureTriagePolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )