from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_profile_validation import (
    EvaluationProfileValidation,
    validate_evaluation_profile,
)


def test_forecast_requires_input():
    pass


def test_valid_profile_passes():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
    )

    result = validate_evaluation_profile(
        profile
    )

    assert isinstance(
        result,
        EvaluationProfileValidation,
    )

    assert result.passed is True
    assert result.errors == ()


def test_profile_rejects_empty_name():
    profile = EvaluationProfile(
        name="   ",
        suite_config="suite.json",
        run_triage=True,
    )

    result = validate_evaluation_profile(
        profile
    )

    assert result.passed is False
    assert (
        "Evaluation profile name cannot be empty."
        in result.errors
    )


def test_profile_rejects_empty_suite_config():
    profile = EvaluationProfile(
        name="production",
        suite_config="   ",
        run_triage=True,
    )

    result = validate_evaluation_profile(
        profile
    )

    assert result.passed is False
    assert (
        "suite_config cannot be empty."
        in result.errors
    )


def test_profile_requires_enabled_analysis():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
    )

    result = validate_evaluation_profile(
        profile
    )

    assert result.passed is False
    assert (
        "Evaluation profile must enable at least one analysis."
        in result.errors
    )


def test_profile_can_enable_multiple_analyses():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
        run_persistence=True,
        run_resolution=True,
        run_forecast=True,
    )

    result = validate_evaluation_profile(
        profile
    )

    assert result.passed is True