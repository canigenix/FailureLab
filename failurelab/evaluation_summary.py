from dataclasses import dataclass
from typing import Sequence

from failurelab.evaluation_report import (
    EvaluationStepResult,
)


@dataclass(frozen=True)
class EvaluationSummary:
    """High-level interpretation of an evaluation."""

    total_analyses: int
    passed_analyses: int
    failed_analyses: int
    failed_analysis_names: tuple[str, ...]
    status: str


def build_evaluation_summary(
    steps: Sequence[EvaluationStepResult],
) -> EvaluationSummary:
    """Summarize the outcome of multiple evaluation analyses."""

    if not steps:
        raise ValueError(
            "At least one evaluation step is required."
        )

    failed_analysis_names = tuple(
        step.analysis
        for step in steps
        if not step.passed
    )

    failed_analyses = len(
        failed_analysis_names
    )

    passed_analyses = (
        len(steps)
        - failed_analyses
    )

    status = (
        "passed"
        if failed_analyses == 0
        else "failed"
    )

    return EvaluationSummary(
        total_analyses=len(steps),
        passed_analyses=passed_analyses,
        failed_analyses=failed_analyses,
        failed_analysis_names=failed_analysis_names,
        status=status,
    )