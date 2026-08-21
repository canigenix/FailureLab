import json

from failurelab.api import FailureLab
from failurelab.evaluation_plan import EvaluationPlan
from failurelab.evaluation_profile import EvaluationProfile
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)


def test_failurelab_loads_evaluation_profile(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            {
                "name": "production",
                "suite_config": "suite.json",
                "run_triage": True,
                "run_forecast": True,
            }
        ),
        encoding="utf-8",
    )

    profile = FailureLab.load_evaluation_profile(
        path
    )

    assert isinstance(
        profile,
        EvaluationProfile,
    )

    assert profile.name == "production"
    assert profile.run_triage is True
    assert profile.run_forecast is True


def test_failurelab_validates_evaluation_profile():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_forecast=True,
    )

    result = FailureLab.validate_evaluation_profile(
        profile
    )

    assert result.passed is True
    assert result.errors == ()


def test_failurelab_builds_evaluation_plan():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
        run_forecast=True,
    )

    plan = FailureLab.evaluation_plan(
        profile
    )

    assert isinstance(
        plan,
        EvaluationPlan,
    )

    assert plan.analyses == (
        "triage",
        "forecast",
    )


def test_failurelab_evaluates_profile():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
        run_forecast=True,
    )

    report = FailureLab.evaluate_profile(
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


def test_failurelab_saves_evaluation_json(
    tmp_path,
):
    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
                message="Forecast passed.",
            ),
        ),
    )

    path = tmp_path / "evaluation.json"

    result = FailureLab.save_evaluation_json(
        report,
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["profile_name"] == "production"
    assert data["passed"] is True
    assert data["passed_count"] == 1