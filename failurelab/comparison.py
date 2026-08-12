"""Compare robustness results between model versions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from failurelab.api import FailureLabReport


class RobustnessRegressionError(RuntimeError):
    """Raised when a candidate model fails a robustness comparison gate."""


@dataclass(frozen=True)
class BoundaryComparison:
    """Comparison of one stress family between two model versions."""

    stress_name: str
    baseline_threshold: float | None
    candidate_threshold: float | None
    baseline_worst_drop: float
    candidate_worst_drop: float
    worst_drop_delta: float
    threshold_status: str
    regression: bool
    regression_reason: str


@dataclass(frozen=True)
class ModelComparison:
    """Overall robustness comparison between two model versions."""

    baseline_score: float
    candidate_score: float
    score_delta: float
    boundaries: list[BoundaryComparison]

    @property
    def improved(self) -> bool:
        return self.score_delta > 0.0

    @property
    def regressions(self) -> list[BoundaryComparison]:
        return [
            boundary
            for boundary in self.boundaries
            if boundary.regression
        ]

    @property
    def passed(self) -> bool:
        return not self.regressions

    def summary(self) -> str:
        direction = (
            "improved"
            if self.score_delta > 0
            else "declined"
            if self.score_delta < 0
            else "unchanged"
        )

        return (
            f"Robustness score {direction}: "
            f"{self.baseline_score:.1f} → "
            f"{self.candidate_score:.1f} "
            f"({self.score_delta:+.1f}). "
            f"Regressions detected: {len(self.regressions)}."
        )

    def require_pass(self) -> None:
        """
        Enforce this comparison as a CI robustness gate.

        Returns normally when no regressions exist.

        Raises RobustnessRegressionError when one or more
        robustness regressions are detected.
        """

        if self.passed:
            return

        regression_names = ", ".join(
            boundary.stress_name
            for boundary in self.regressions
        )

        raise RobustnessRegressionError(
            "FailureLab robustness gate failed. "
            f"Detected {len(self.regressions)} regression(s): "
            f"{regression_names}."
        )

    def save_json(
        self,
        path,
    ) -> Path:
        from failurelab.comparison_export import (
            export_comparison_json,
        )

        return export_comparison_json(
            self,
            path,
        )

    def save_html(
        self,
        path,
    ) -> Path:
        from failurelab.comparison_export import (
            export_comparison_html,
        )

        return export_comparison_html(
            self,
            path,
        )


_HIGHER_THRESHOLD_IS_BETTER = {
    "blur",
    "occlusion",
    "rotation",
}

_LOWER_THRESHOLD_IS_BETTER = {
    "brightness",
    "compression",
    "crop",
}


def _compare_thresholds(
    stress_name: str,
    baseline: float | None,
    candidate: float | None,
) -> str:
    if baseline is None and candidate is None:
        return "unchanged"

    if baseline is not None and candidate is None:
        return "improved"

    if baseline is None and candidate is not None:
        return "regressed"

    if stress_name in _HIGHER_THRESHOLD_IS_BETTER:
        if candidate > baseline:
            return "improved"

        if candidate < baseline:
            return "regressed"

        return "unchanged"

    if stress_name in _LOWER_THRESHOLD_IS_BETTER:
        if candidate < baseline:
            return "improved"

        if candidate > baseline:
            return "regressed"

        return "unchanged"

    return "unchanged"


def _regression_reason(
    *,
    threshold_regressed: bool,
    drop_regressed: bool,
) -> str:
    if threshold_regressed and drop_regressed:
        return "both"

    if threshold_regressed:
        return "threshold"

    if drop_regressed:
        return "worst_drop"

    return "none"


def compare_reports(
    baseline: FailureLabReport,
    candidate: FailureLabReport,
    *,
    regression_tolerance: float = 0.02,
) -> ModelComparison:
    """Compare two FailureLab reports."""

    if regression_tolerance < 0:
        raise ValueError(
            "regression_tolerance cannot be negative."
        )

    if baseline.failure_envelope is None:
        raise ValueError(
            "Baseline report does not contain a failure envelope."
        )

    if candidate.failure_envelope is None:
        raise ValueError(
            "Candidate report does not contain a failure envelope."
        )

    baseline_boundaries = {
        boundary.stress_name: boundary
        for boundary in baseline.failure_envelope.boundaries
    }

    candidate_boundaries = {
        boundary.stress_name: boundary
        for boundary in candidate.failure_envelope.boundaries
    }

    common_names = [
        name
        for name in baseline_boundaries
        if name in candidate_boundaries
    ]

    comparisons = []

    for name in common_names:
        baseline_boundary = baseline_boundaries[name]
        candidate_boundary = candidate_boundaries[name]

        threshold_status = _compare_thresholds(
            stress_name=name,
            baseline=baseline_boundary.failure_threshold,
            candidate=candidate_boundary.failure_threshold,
        )

        worst_drop_delta = (
            candidate_boundary.worst_top1_drop
            - baseline_boundary.worst_top1_drop
        )

        drop_regressed = (
            worst_drop_delta
            > regression_tolerance
        )

        threshold_regressed = (
            threshold_status == "regressed"
        )

        reason = _regression_reason(
            threshold_regressed=threshold_regressed,
            drop_regressed=drop_regressed,
        )

        comparisons.append(
            BoundaryComparison(
                stress_name=name,
                baseline_threshold=(
                    baseline_boundary.failure_threshold
                ),
                candidate_threshold=(
                    candidate_boundary.failure_threshold
                ),
                baseline_worst_drop=(
                    baseline_boundary.worst_top1_drop
                ),
                candidate_worst_drop=(
                    candidate_boundary.worst_top1_drop
                ),
                worst_drop_delta=worst_drop_delta,
                threshold_status=threshold_status,
                regression=(
                    drop_regressed
                    or threshold_regressed
                ),
                regression_reason=reason,
            )
        )

    baseline_score = baseline.robustness_score.score
    candidate_score = candidate.robustness_score.score

    return ModelComparison(
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        score_delta=(
            candidate_score
            - baseline_score
        ),
        boundaries=comparisons,
    )