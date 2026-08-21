from dataclasses import dataclass
from typing import Sequence

from failurelab.evaluation_health import (
    EvaluationHealth,
    classify_evaluation_health,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_summary import (
    EvaluationSummary,
    build_evaluation_summary,
)


@dataclass(frozen=True)
class EvaluationIntelligence:
    """High-level interpretation of a complete evaluation."""

    summary: EvaluationSummary
    health: EvaluationHealth


def build_evaluation_intelligence(
    steps: Sequence[EvaluationStepResult],
) -> EvaluationIntelligence:
    """Build high-level intelligence from evaluation results."""

    summary = build_evaluation_summary(
        steps
    )

    health = classify_evaluation_health(
        summary
    )

    return EvaluationIntelligence(
        summary=summary,
        health=health,
    )