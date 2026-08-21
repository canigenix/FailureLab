import json

import pytest

from failurelab.evaluation_gate_config import (
    EvaluationGateConfig,
    load_evaluation_gate_config,
)


def test_load_default_gate_config(
    tmp_path,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps({}),
        encoding="utf-8",
    )

    config = load_evaluation_gate_config(
        path
    )

    assert isinstance(
        config,
        EvaluationGateConfig,
    )

    assert (
        config.maximum_failed_analyses
        == 0
    )

    assert (
        config.allowed_health_statuses
        == (
            "healthy",
        )
    )


def test_load_custom_gate_config(
    tmp_path,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 1,
                "allowed_health_statuses": [
                    "healthy",
                    "watch",
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_evaluation_gate_config(
        path
    )

    assert (
        config.maximum_failed_analyses
        == 1
    )

    assert (
        config.allowed_health_statuses
        == (
            "healthy",
            "watch",
        )
    )


def test_gate_config_rejects_negative_maximum(
    tmp_path,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": -1,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_empty_health_statuses(
    tmp_path,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps(
            {
                "allowed_health_statuses": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_invalid_health_status(
    tmp_path,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps(
            {
                "allowed_health_statuses": [
                    "healthy",
                    "unknown",
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Invalid health status",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_non_object(
    tmp_path,
):
    path = tmp_path / "gate.json"

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
        load_evaluation_gate_config(
            path
        )