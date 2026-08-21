from collections.abc import Callable, Mapping

from failurelab.evaluation_plan import (
    build_evaluation_plan,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
    build_evaluation_report,
)


EvaluationHandler = Callable[
    [],
    EvaluationStepResult,
]


def run_evaluation(
    profile: EvaluationProfile,
    handlers: Mapping[
        str,
        EvaluationHandler,
    ],
) -> EvaluationReport:
    """Execute an evaluation profile."""

    plan = build_evaluation_plan(
        profile
    )

    results = []

    for analysis in plan.analyses:
        if analysis not in handlers:
            raise ValueError(
                "No evaluation handler registered "
                f"for '{analysis}'."
            )

        result = handlers[analysis]()

        if not isinstance(
            result,
            EvaluationStepResult,
        ):
            raise TypeError(
                "Evaluation handlers must return "
                "EvaluationStepResult."
            )

        if result.analysis != analysis:
            raise ValueError(
                "Evaluation handler returned a result "
                f"for '{result.analysis}' while running "
                f"'{analysis}'."
            )

        results.append(
            result
        )

    return build_evaluation_report(
        plan,
        results,
    )