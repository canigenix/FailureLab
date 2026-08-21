from dataclasses import dataclass

from failurelab.evaluation_plan import (
    EvaluationPlan,
)


@dataclass(frozen=True)
class EvaluationStepResult:
    """Result for one evaluation workflow."""

    analysis: str
    passed: bool
    message: str = ""


@dataclass(frozen=True)
class EvaluationReport:
    """Combined result for an evaluation plan."""

    profile_name: str
    suite_config: str
    steps: tuple[EvaluationStepResult, ...]

    @property
    def passed(self) -> bool:
        return all(
            step.passed
            for step in self.steps
        )

    @property
    def failed_count(self) -> int:
        return sum(
            not step.passed
            for step in self.steps
        )

    @property
    def passed_count(self) -> int:
        return sum(
            step.passed
            for step in self.steps
        )


def build_evaluation_report(
    plan: EvaluationPlan,
    step_results,
) -> EvaluationReport:
    """Build an evaluation report from step results."""

    results = tuple(step_results)

    expected = plan.analyses
    actual = tuple(
        result.analysis
        for result in results
    )

    if actual != expected:
        raise ValueError(
            "Evaluation results must match the evaluation plan."
        )

    return EvaluationReport(
        profile_name=plan.profile_name,
        suite_config=plan.suite_config,
        steps=results,
    )