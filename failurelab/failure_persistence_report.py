from dataclasses import dataclass
from typing import Sequence

from failurelab.failure_persistence import (
    FailurePersistence,
    analyze_failure_persistence,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
    analyze_failure_recurrence,
)


@dataclass(frozen=True)
class FailurePersistenceReport:
    """Summary of recurring and persistent failures."""

    failures: tuple[FailurePersistence, ...]
    total_failures: int
    persistent_count: int
    recurring_count: int
    isolated_count: int
    highest_persistence: FailurePersistence | None

    @property
    def unresolved_count(self) -> int:
        return (
            self.persistent_count
            + self.recurring_count
        )


def build_failure_persistence_report(
    occurrences: Sequence[FailureOccurrence],
) -> FailurePersistenceReport:
    """Build a persistence report from failure occurrences."""

    recurrences = analyze_failure_recurrence(
        occurrences
    )

    failures = tuple(
        analyze_failure_persistence(
            recurrences
        )
    )

    highest_persistence = (
        failures[0]
        if failures
        else None
    )

    return FailurePersistenceReport(
        failures=failures,
        total_failures=len(failures),
        persistent_count=sum(
            failure.level == "persistent"
            for failure in failures
        ),
        recurring_count=sum(
            failure.level == "recurring"
            for failure in failures
        ),
        isolated_count=sum(
            failure.level == "isolated"
            for failure in failures
        ),
        highest_persistence=highest_persistence,
    )