import json

from failurelab.evaluation_handlers import (
    build_profile_handlers,
)
from failurelab.evaluation_profile import (
    EvaluationProfile,
)


def write_occurrences(
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

    return input_path


def write_triage_input(
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

    return input_path


def write_progression_input(
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

    return input_path


def write_signature_input(
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

    return input_path


def test_build_profile_handlers_forecast(
    tmp_path,
):
    write_occurrences(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        run_forecast=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "forecast" in handlers

    result = handlers["forecast"]()

    assert result.analysis == "forecast"
    assert result.passed is True


def test_build_profile_handlers_persistence(
    tmp_path,
):
    write_occurrences(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        run_persistence=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "persistence" in handlers

    result = handlers["persistence"]()

    assert result.analysis == "persistence"
    assert result.passed is True


def test_build_profile_handlers_resolution(
    tmp_path,
):
    write_occurrences(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        run_resolution=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "resolution" in handlers

    result = handlers["resolution"]()

    assert result.analysis == "resolution"
    assert result.passed is True


def test_build_profile_handlers_triage(
    tmp_path,
):
    write_triage_input(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        triage_input="triage.json",
        run_triage=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "triage" in handlers

    result = handlers["triage"]()

    assert result.analysis == "triage"
    assert result.passed is True


def test_build_profile_handlers_progression(
    tmp_path,
):
    write_progression_input(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        progression_input="progression.json",
        run_progression=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "progression" in handlers

    result = handlers["progression"]()

    assert result.analysis == "progression"
    assert result.passed is True


def test_build_profile_handlers_signature(
    tmp_path,
):
    write_signature_input(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        signature_input="signature.json",
        run_signature=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert "signature" in handlers

    result = handlers["signature"]()

    assert result.analysis == "signature"
    assert result.passed is True


def test_handlers_build_all_real_steps(
    tmp_path,
):
    write_occurrences(
        tmp_path
    )

    write_triage_input(
        tmp_path
    )

    write_progression_input(
        tmp_path
    )

    write_signature_input(
        tmp_path
    )

    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        forecast_input="failures.json",
        triage_input="triage.json",
        progression_input="progression.json",
        signature_input="signature.json",
        run_progression=True,
        run_signature=True,
        run_triage=True,
        run_persistence=True,
        run_resolution=True,
        run_forecast=True,
    )

    handlers = build_profile_handlers(
        profile,
        base_path=tmp_path,
    )

    assert set(
        handlers
    ) == {
        "progression",
        "signature",
        "triage",
        "persistence",
        "resolution",
        "forecast",
    }


def test_handlers_ignore_disabled_steps():
    profile = EvaluationProfile(
        name="production",
        suite_config="suite.json",
        run_progression=False,
        run_signature=False,
        run_triage=False,
        run_persistence=False,
        run_resolution=False,
        run_forecast=False,
    )

    handlers = build_profile_handlers(
        profile
    )

    assert handlers == {}