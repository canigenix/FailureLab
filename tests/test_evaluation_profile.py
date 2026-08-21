import json

import pytest

from failurelab.evaluation_profile import (
    EvaluationProfile,
    load_evaluation_profile,
)


def test_load_evaluation_profile(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            {
                "name": "production-evaluation",
                "suite_config": "suite.json",
                "run_progression": True,
                "run_signature": True,
                "run_triage": True,
                "run_persistence": True,
                "run_resolution": True,
                "run_forecast": True,
            }
        ),
        encoding="utf-8",
    )

    profile = load_evaluation_profile(
        path
    )

    assert isinstance(
        profile,
        EvaluationProfile,
    )

    assert (
        profile.name
        == "production-evaluation"
    )

    assert (
        profile.suite_config
        == "suite.json"
    )

    assert profile.run_progression is True
    assert profile.run_signature is True
    assert profile.run_triage is True
    assert profile.run_persistence is True
    assert profile.run_resolution is True
    assert profile.run_forecast is True


def test_evaluation_profile_defaults(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            {
                "name": "basic",
                "suite_config": "suite.json",
            }
        ),
        encoding="utf-8",
    )

    profile = load_evaluation_profile(
        path
    )

    assert profile.run_progression is False
    assert profile.run_signature is False
    assert profile.run_triage is False
    assert profile.run_persistence is False
    assert profile.run_resolution is False
    assert profile.run_forecast is False


def test_profile_rejects_non_object(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            [
                "bad"
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="JSON object",
    ):
        load_evaluation_profile(
            path
        )


def test_profile_requires_name(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            {
                "suite_config": "suite.json",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="'name'",
    ):
        load_evaluation_profile(
            path
        )


def test_profile_requires_suite_config(
    tmp_path,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            {
                "name": "basic",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="'suite_config'",
    ):
        load_evaluation_profile(
            path
        )