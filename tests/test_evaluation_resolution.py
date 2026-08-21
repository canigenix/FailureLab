import json

import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_resolution import (
    run_profile_resolution,
)


def test_run_profile_resolution(
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
        forecast_input="failures.json",
        run_resolution=True,
    )

    result = run_profile_resolution(
        profile,
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "resolution"
    assert result.passed is True

    assert (
        result.message
        == (
            "2 failures analyzed; "
            "1 improving; "
            "1 worsening."
        )
    )


def test_resolution_requires_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_resolution=True,
    )

    with pytest.raises(
        ValueError,
        match="occurrence input",
    ):
        run_profile_resolution(
            profile
        )


def test_resolution_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_resolution(
            profile
        )


def test_resolution_rejects_invalid_json_shape(
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
        forecast_input="failures.json",
        run_resolution=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_resolution(
            profile,
            base_path=tmp_path,
        )