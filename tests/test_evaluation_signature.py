import json

import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)
from failurelab.evaluation_signature import (
    run_profile_signature,
)


def test_run_profile_signature(
    tmp_path,
):
    input_path = tmp_path / "signature.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "stress_name": "blur",
                    "failure_rate": 0.60,
                    "prediction_flip_rate": 0.10,
                },
                {
                    "stress_name": "rotation",
                    "failure_rate": 0.20,
                    "prediction_flip_rate": 0.05,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_signature=True,
    )

    result = run_profile_signature(
        profile,
        input_path="signature.json",
        base_path=tmp_path,
    )

    assert isinstance(
        result,
        EvaluationStepResult,
    )

    assert result.analysis == "signature"
    assert result.passed is True
    assert "dominant stress blur" in result.message


def test_signature_requires_input():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_signature=True,
    )

    with pytest.raises(
        ValueError,
        match="signature input",
    ):
        run_profile_signature(
            profile
        )


def test_signature_must_be_enabled():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
    )

    with pytest.raises(
        ValueError,
        match="not enabled",
    ):
        run_profile_signature(
            profile,
            input_path="signature.json",
        )


def test_signature_rejects_invalid_json_shape(
    tmp_path,
):
    input_path = tmp_path / "signature.json"

    input_path.write_text(
        json.dumps(
            {
                "stress_name": "blur"
            }
        ),
        encoding="utf-8",
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_signature=True,
    )

    with pytest.raises(
        ValueError,
        match="JSON list",
    ):
        run_profile_signature(
            profile,
            input_path="signature.json",
            base_path=tmp_path,
        )