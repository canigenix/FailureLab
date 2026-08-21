from dataclasses import dataclass

from failurelab.failure_persistence_report import (
    FailurePersistenceReport,
)


@dataclass(frozen=True)
class FailurePersistencePolicyResult:
    """Result of evaluating failure persistence policy."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_failure_persistence_policy(
    report: FailurePersistenceReport,
    *,
    max_persistent: int | None = None,
    max_recurring: int | None = None,
    max_unresolved: int | None = None,
    max_recurrence_rate: float | None = None,
) -> FailurePersistencePolicyResult:
    """Evaluate persistent failures against policy limits."""

    for name, value in (
        ("max_persistent", max_persistent),
        ("max_recurring", max_recurring),
        ("max_unresolved", max_unresolved),
    ):
        if value is not None and value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    if (
        max_recurrence_rate is not None
        and not 0.0 <= max_recurrence_rate <= 1.0
    ):
        raise ValueError(
            "max_recurrence_rate must be between 0.0 and 1.0."
        )

    violations = []

    if (
        max_persistent is not None
        and report.persistent_count > max_persistent
    ):
        violations.append(
            "Persistent failures exceeded limit: "
            f"{report.persistent_count} > {max_persistent}."
        )

    if (
        max_recurring is not None
        and report.recurring_count > max_recurring
    ):
        violations.append(
            "Recurring failures exceeded limit: "
            f"{report.recurring_count} > {max_recurring}."
        )

    if (
        max_unresolved is not None
        and report.unresolved_count > max_unresolved
    ):
        violations.append(
            "Unresolved failures exceeded limit: "
            f"{report.unresolved_count} > {max_unresolved}."
        )

    if (
        max_recurrence_rate is not None
        and report.highest_persistence is not None
        and report.highest_persistence.recurrence_rate
        > max_recurrence_rate
    ):
        violations.append(
            "Highest recurrence rate exceeded limit: "
            f"{report.highest_persistence.recurrence_rate:.4f} > "
            f"{max_recurrence_rate:.4f}."
        )

    return FailurePersistencePolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )