import pytest

from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_summary import (
    EvaluationSummary,
    build_evaluation_summary,
)


def test_summary_for_passing_evaluation():
    steps = [
        EvaluationStepResult(
            analysis="progression",
            passed=True,
            message="Progression passed.",
        ),
        EvaluationStepResult(
            analysis="signature",
            passed=True,
            message="Signature passed.",
        ),
        EvaluationStepResult(
            analysis="triage",
            passed=True,
            message="Triage passed.",
        ),
    ]

    summary = build_evaluation_summary(
        steps
    )

    assert isinstance(
        summary,
        EvaluationSummary,
    )

    assert summary.total_analyses == 3
    assert summary.passed_analyses == 3
    assert summary.failed_analyses == 0
    assert summary.failed_analysis_names == ()
    assert summary.status == "passed"


def test_summary_tracks_failed_analyses():
    steps = [
        EvaluationStepResult(
            analysis="progression",
            passed=False,
            message="Regression detected.",
        ),
        EvaluationStepResult(
            analysis="signature",
            passed=True,
            message="Signature passed.",
        ),
        EvaluationStepResult(
            analysis="forecast",
            passed=False,
            message="Projected risk detected.",
        ),
    ]

    summary = build_evaluation_summary(
        steps
    )

    assert summary.total_analyses == 3
    assert summary.passed_analyses == 1
    assert summary.failed_analyses == 2

    assert (
        summary.failed_analysis_names
        == (
            "progression",
            "forecast",
        )
    )

    assert summary.status == "failed"


def test_summary_preserves_failure_order():
    steps = [
        EvaluationStepResult(
            analysis="triage",
            passed=False,
            message="Triage failed.",
        ),
        EvaluationStepResult(
            analysis="resolution",
            passed=False,
            message="Resolution failed.",
        ),
        EvaluationStepResult(
            analysis="forecast",
            passed=False,
            message="Forecast failed.",
        ),
    ]

    summary = build_evaluation_summary(
        steps
    )

    assert summary.failed_analysis_names == (
        "triage",
        "resolution",
        "forecast",
    )


def test_summary_rejects_empty_steps():
    with pytest.raises(
        ValueError,
        match="At least one evaluation step",
    ):
        build_evaluation_summary(
            []
        )