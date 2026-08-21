import json

import pytest

from failurelab.evaluation_persistence import (
    run_profile_persistence,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)


def test_run_profile_persistence(
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
                    "checkpoint": "v3",
                    "failure_name": "blur",
                    "priority_score": 0.40,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        run_persistence=True,
    )

    result = run_profile_persistence(
        profile,
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "persistence"
    assert result.passed is True
    assert "1 failures analyzed" in result.message


def test_persistence_requires_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_persistence=True,
    )

    with pytest.raises(
        ValueError,
        match="occurrence input",
    ):
        run_profile_persistence(
            profile
        )


def test_persistence_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_persistence(
            profile
        )


def test_persistence_rejects_invalid_json_shape(
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
        run_persistence=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_persistence(
            profile,
            base_path=tmp_path,
        )