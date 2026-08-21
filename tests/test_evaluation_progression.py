import json

import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_progression import (
    run_profile_progression,
)


def test_run_profile_progression(
    tmp_path,
):
    input_path = tmp_path / "progression.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "label": "v1",
                    "failure_rate": 0.50,
                },
                {
                    "label": "v2",
                    "failure_rate": 0.40,
                },
                {
                    "label": "v3",
                    "failure_rate": 0.30,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_progression=True,
    )

    result = run_profile_progression(
        profile,
        input_path="progression.json",
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "progression"
    assert result.passed is True
    assert "3 checkpoints analyzed" in result.message
    assert "2 improved" in result.message


def test_progression_requires_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_progression=True,
    )

    with pytest.raises(
        ValueError,
        match="progression input",
    ):
        run_profile_progression(
            profile
        )


def test_progression_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_progression(
            profile,
            input_path="progression.json",
        )


def test_progression_rejects_invalid_json_shape(
    tmp_path,
):
    input_path = tmp_path / "progression.json"

    input_path.write_text(
        json.dumps(
            {
                "label": "v1"
            }
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_progression=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_progression(
            profile,
            input_path="progression.json",
            base_path=tmp_path,
        )