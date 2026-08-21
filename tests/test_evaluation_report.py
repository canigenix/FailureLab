import pytest

from failurelab.evaluation_plan import (
    EvaluationPlan,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
    build_evaluation_report,
)


def test_build_evaluation_report():
    plan = EvaluationPlan(
        profile_name="production",
        suite_config="suite.json",
        analyses=(
            "triage",
            "forecast",
        ),
    )

    report = build_evaluation_report(
        plan,
        [
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ],
    )

    assert isinstance(
        report,
        EvaluationReport,
    )

    assert report.profile_name == "production"
    assert report.passed is True
    assert report.passed_count == 2
    assert report.failed_count == 0


def test_evaluation_report_detects_failure():
    plan = EvaluationPlan(
        profile_name="production",
        suite_config="suite.json",
        analyses=(
            "triage",
            "forecast",
        ),
    )

    report = build_evaluation_report(
        plan,
        [
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=False,
                message="Projected risk exceeded limit.",
            ),
        ],
    )

    assert report.passed is False
    assert report.passed_count == 1
    assert report.failed_count == 1


def test_report_preserves_messages():
    plan = EvaluationPlan(
        profile_name="production",
        suite_config="suite.json",
        analyses=(
            "forecast",
        ),
    )

    report = build_evaluation_report(
        plan,
        [
            EvaluationStepResult(
                analysis="forecast",
                passed=False,
                message="Forecast policy failed.",
            ),
        ],
    )

    assert (
        report.steps[0].message
        == "Forecast policy failed."
    )


def test_report_rejects_wrong_analysis_order():
    plan = EvaluationPlan(
        profile_name="production",
        suite_config="suite.json",
        analyses=(
            "triage",
            "forecast",
        ),
    )

    with pytest.raises(
        ValueError,
        match="match the evaluation plan",
    ):
        build_evaluation_report(
            plan,
            [
                EvaluationStepResult(
                    analysis="forecast",
                    passed=True,
                ),
                EvaluationStepResult(
                    analysis="triage",
                    passed=True,
                ),
            ],
        )


def test_report_rejects_missing_result():
    plan = EvaluationPlan(
        profile_name="production",
        suite_config="suite.json",
        analyses=(
            "triage",
            "forecast",
        ),
    )

    with pytest.raises(
        ValueError,
        match="match the evaluation plan",
    ):
        build_evaluation_report(
            plan,
            [
                EvaluationStepResult(
                    analysis="triage",
                    passed=True,
                ),
            ],
        )