import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)
from failurelab.evaluator import (
    run_evaluation,
)


def test_run_evaluation():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
        run_forecast=True,
    )

    report = run_evaluation(
        profile,
        {
            "triage": lambda: EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            "forecast": lambda: EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        },
    )

    assert isinstance(
        report,
        EvaluationReport,
    )

    assert report.passed is True
    assert report.passed_count == 2
    assert report.failed_count == 0


def test_evaluator_preserves_order():
    calls = []

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_progression=True,
        run_triage=True,
        run_forecast=True,
    )

    def make_handler(
        analysis,
    ):
        def handler():
            calls.append(
                analysis
            )

            return EvaluationStepResult(
                analysis=analysis,
                passed=True,
            )

        return handler

    run_evaluation(
        profile,
        {
            "progression": make_handler(
                "progression"
            ),
            "triage": make_handler(
                "triage"
            ),
            "forecast": make_handler(
                "forecast"
            ),
        },
    )

    assert calls == [
        "progression",
        "triage",
        "forecast",
    ]


def test_evaluator_tracks_failure():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
        run_forecast=True,
    )

    report = run_evaluation(
        profile,
        {
            "triage": lambda: EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            "forecast": lambda: EvaluationStepResult(
                analysis="forecast",
                passed=False,
                message="Projected risk exceeded.",
            ),
        },
    )

    assert report.passed is False
    assert report.failed_count == 1

    assert (
        report.steps[1].message
        == "Projected risk exceeded."
    )


def test_evaluator_requires_handler():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_forecast=True,
    )

    with pytest.raises(
        ValueError,
        match="No evaluation handler",
    ):
        run_evaluation(
            profile,
            {},
        )


def test_evaluator_requires_step_result():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_forecast=True,
    )

    with pytest.raises(
        TypeError,
        match="EvaluationStepResult",
    ):
        run_evaluation(
            profile,
            {
                "forecast": lambda: True,
            },
        )


def test_evaluator_rejects_wrong_analysis():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_forecast=True,
    )

    with pytest.raises(
        ValueError,
        match="while running",
    ):
        run_evaluation(
            profile,
            {
                "forecast": lambda: EvaluationStepResult(
                    analysis="triage",
                    passed=True,
                ),
            },
        )