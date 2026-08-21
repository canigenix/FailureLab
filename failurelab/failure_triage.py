from dataclasses import dataclass
from typing import Sequence

from failurelab.failure_priority import (
    FailurePriority,
    FailurePrioritySignal,
    rank_failure_priorities,
)


@dataclass(frozen=True)
class FailureTriageReport:
    """Prioritized summary of detected failure patterns."""

    priorities: tuple[FailurePriority, ...]
    highest_priority: FailurePriority | None
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    @property
    def total_failures(self) -> int:
        return len(self.priorities)

    @property
    def actionable_count(self) -> int:
        return (
            self.critical_count
            + self.high_count
        )


def build_failure_triage_report(
    signals: Sequence[FailurePrioritySignal],
) -> FailureTriageReport:
    """Build a ranked failure-triage report."""

    priorities = tuple(
        rank_failure_priorities(
            signals
        )
    )

    highest_priority = (
        priorities[0]
        if priorities
        else None
    )

    return FailureTriageReport(
        priorities=priorities,
        highest_priority=highest_priority,
        critical_count=sum(
            priority.level == "critical"
            for priority in priorities
        ),
        high_count=sum(
            priority.level == "high"
            for priority in priorities
        ),
        medium_count=sum(
            priority.level == "medium"
            for priority in priorities
        ),
        low_count=sum(
            priority.level == "low"
            for priority in priorities
        ),
    )