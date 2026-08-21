from dataclasses import dataclass
from typing import Sequence

from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution import (
    FailureResolution,
    analyze_failure_resolution,
)


@dataclass(frozen=True)
class FailureResolutionReport:
    """Summary of failure resolution trends."""

    failures: tuple[FailureResolution, ...]
    total_failures: int
    improving_count: int
    unchanged_count: int
    worsening_count: int
    insufficient_history_count: int
    worst_resolution: FailureResolution | None

    @property
    def unresolved_count(self) -> int:
        return (
            self.unchanged_count
            + self.worsening_count
        )


def build_failure_resolution_report(
    occurrences: Sequence[FailureOccurrence],
    *,
    tolerance: float = 0.0,
) -> FailureResolutionReport:
    """Build a report of failure resolution trends."""

    failures = tuple(
        analyze_failure_resolution(
            occurrences,
            tolerance=tolerance,
        )
    )

    worsening = [
        failure
        for failure in failures
        if failure.status == "worsening"
    ]

    worst_resolution = (
        max(
            worsening,
            key=lambda failure: failure.score_delta,
        )
        if worsening
        else None
    )

    return FailureResolutionReport(
        failures=failures,
        total_failures=len(failures),
        improving_count=sum(
            failure.status == "improving"
            for failure in failures
        ),
        unchanged_count=sum(
            failure.status == "unchanged"
            for failure in failures
        ),
        worsening_count=sum(
            failure.status == "worsening"
            for failure in failures
        ),
        insufficient_history_count=sum(
            failure.status == "insufficient_history"
            for failure in failures
        ),
        worst_resolution=worst_resolution,
    )