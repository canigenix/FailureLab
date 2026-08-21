import json

import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_triage import (
    run_profile_triage,
)


def test_run_profile_triage(
    tmp_path,
):
    input_path = tmp_path / "triage.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "name": "blur",
                    "failure_rate": 0.80,
                    "prediction_flip_rate": 0.60,
                    "affected_fraction": 0.70,
                    "severity_weight": 1.0,
                },
                {
                    "name": "rotation",
                    "failure_rate": 0.20,
                    "prediction_flip_rate": 0.10,
                    "affected_fraction": 0.20,
                    "severity_weight": 1.0,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
    )

    result = run_profile_triage(
        profile,
        input_path="triage.json",
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "triage"
    assert result.passed is True
    assert "2 failures analyzed" in result.message


def test_triage_requires_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
    )

    with pytest.raises(
        ValueError,
        match="triage input",
    ):
        run_profile_triage(
            profile
        )


def test_triage_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_triage(
            profile,
            input_path="triage.json",
        )


def test_triage_rejects_invalid_json_shape(
    tmp_path,
):
    input_path = tmp_path / "triage.json"

    input_path.write_text(
        json.dumps(
            {
                "name": "blur"
            }
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_triage=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_triage(
            profile,
            input_path="triage.json",
            base_path=tmp_path,
        )