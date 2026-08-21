import json

import pytest

from failurelab.evaluation_forecast import (
    run_profile_forecast,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)


def test_run_profile_forecast_with_occurrence_input(
    tmp_path,
):
    input_path = tmp_path / "failures.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.80,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.60,
                },
                {
                    "checkpoint": "v1",
                    "failure_name": "rotation",
                    "priority_score": 0.20,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "rotation",
                    "priority_score": 0.60,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        occurrence_input="failures.json",
        run_forecast=True,
    )

    result = run_profile_forecast(
        profile,
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "forecast"
    assert result.passed is True

    assert (
        result.message
        == (
            "2 failures analyzed; "
            "1 worsening; "
            "1 projected risk."
        )
    )


def test_forecast_keeps_legacy_forecast_input(
    tmp_path,
):
    input_path = tmp_path / "failures.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.80,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.60,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        run_forecast=True,
    )

    result = run_profile_forecast(
        profile,
        base_path=tmp_path,
    )

    assert result.analysis == "forecast"
    assert result.passed is True


def test_occurrence_input_takes_priority(
    tmp_path,
):
    new_input = tmp_path / "new.json"

    new_input.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.20,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.60,
                },
            ]
        ),
        encoding="utf-8",
    )

    legacy_input = tmp_path / "legacy.json"

    legacy_input.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.80,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.60,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        occurrence_input="new.json",
        forecast_input="legacy.json",
        run_forecast=True,
    )

    result = run_profile_forecast(
        profile,
        base_path=tmp_path,
    )

    assert "1 worsening" in result.message


def test_forecast_requires_occurrence_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_forecast=True,
    )

    with pytest.raises(
        ValueError,
        match="occurrence input",
    ):
        run_profile_forecast(
            profile
        )


def test_forecast_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        occurrence_input="failures.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_forecast(
            profile
        )


def test_forecast_rejects_invalid_json_shape(
    tmp_path,
):
    input_path = tmp_path / "failures.json"

    input_path.write_text(
        json.dumps(
            {
                "checkpoint": "v1"
            }
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        occurrence_input="failures.json",
        run_forecast=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_forecast(
            profile,
            base_path=tmp_path,
        )