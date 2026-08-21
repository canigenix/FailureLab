from dataclasses import dataclass
from typing import Literal

from failurelab.evaluation_summary import (
    EvaluationSummary,
)


EvaluationHealthStatus = Literal[
    "healthy",
    "watch",
    "at-risk",
    "critical",
]


@dataclass(frozen=True)
class EvaluationHealth:
    """High-level health classification for an evaluation."""

    status: EvaluationHealthStatus
    failure_ratio: float
    failed_analyses: int
    message: str


def classify_evaluation_health(
    summary: EvaluationSummary,
) -> EvaluationHealth:
    """Classify overall evaluation health."""

    failure_ratio = (
        summary.failed_analyses
        / summary.total_analyses
    )

    if summary.failed_analyses == 0:
        status = "healthy"
        message = (
            "All enabled analyses passed."
        )

    elif failure_ratio <= 0.25:
        status = "watch"
        message = (
            "A limited number of analyses failed."
        )

    elif failure_ratio <= 0.50:
        status = "at-risk"
        message = (
            "Multiple evaluation areas require attention."
        )

    else:
        status = "critical"
        message = (
            "Most enabled analyses failed."
        )

    return EvaluationHealth(
        status=status,
        failure_ratio=failure_ratio,
        failed_analyses=summary.failed_analyses,
        message=message,
    )