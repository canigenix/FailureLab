import pytest

from failurelab.evaluation_plan import (
    EvaluationPlan,
    build_evaluation_plan,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)


def test_build_evaluation_plan():
    profile = EvaluationProfile(
    name="production",
    suite_config="suite.json",
    forecast_input="failures.json",
    run_progression=True,
    run_triage=True,
    run_forecast=True,
)

    plan = build_evaluation_plan(
        profile
    )

    assert isinstance(
        plan,
        EvaluationPlan,
    )

    assert plan.profile_name == "production"
    assert plan.suite_config == "suite.json"

    assert plan.analyses == (
        "progression",
        "triage",
        "forecast",
    )

    assert plan.analysis_count == 3


def test_plan_preserves_analysis_order():
    profile = EvaluationProfile(
    name="full",
    suite_config="suite.json",
    forecast_input="failures.json",
    run_progression=True,
    run_signature=True,
    run_triage=True,
    run_persistence=True,
    run_resolution=True,
    run_forecast=True,
)

    plan = build_evaluation_plan(
        profile
    )

    assert plan.analyses == (
        "progression",
        "signature",
        "triage",
        "persistence",
        "resolution",
        "forecast",
    )


def test_plan_supports_single_analysis():
    profile = EvaluationProfile(
    name="forecast-only",
    suite_config="suite.json",
    forecast_input="failures.json",
    run_forecast=True,
)

    plan = build_evaluation_plan(
        profile
    )

    assert plan.analyses == (
        "forecast",
    )

    assert plan.analysis_count == 1


def test_plan_rejects_invalid_profile():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
    )

    with pytest.raises(
        ValueError,
        match="at least one analysis",
    ):
        build_evaluation_plan(
            profile
        )


def test_plan_rejects_empty_profile_name():
    profile = EvaluationProfile(
        name=" ",
        suite_config="suite.json",
        run_triage=True,
    )

    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        build_evaluation_plan(
            profile
        )