"""Failure-envelope summaries for robustness sweeps."""

from __future__ import annotations

from dataclasses import dataclass

from failurelab.sweeps import StressSweepResult


@dataclass(frozen=True)
class FailureBoundary:
    """Failure threshold summary for one stress family."""

    stress_name: str
    failure_threshold: float | None
    worst_top1_drop: float

    @property
    def threshold_reached(self) -> bool:
        return self.failure_threshold is not None


@dataclass(frozen=True)
class FailureEnvelope:
    """Collection of model failure boundaries."""

    boundaries: list[FailureBoundary]

    def get(
        self,
        stress_name: str,
    ) -> FailureBoundary:
        """Return one boundary by stress name."""

        normalized = stress_name.strip().lower()

        for boundary in self.boundaries:
            if boundary.stress_name == normalized:
                return boundary

        raise KeyError(
            f"No failure boundary found for: {stress_name}"
        )


def build_failure_envelope(
    sweeps: list[StressSweepResult],
) -> FailureEnvelope:
    """Convert sweep results into a compact failure envelope."""

    boundaries = [
        FailureBoundary(
            stress_name=sweep.name,
            failure_threshold=sweep.failure_threshold,
            worst_top1_drop=sweep.worst_top1_drop,
        )
        for sweep in sweeps
    ]

    return FailureEnvelope(
        boundaries=boundaries
    )