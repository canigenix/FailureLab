import json

import pytest

from failurelab.evaluation_gate_config import (
    EvaluationGateConfig,
    load_evaluation_gate_config,
)


def write_config(
    tmp_path,
    data,
):
    path = tmp_path / "gate.json"

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def test_load_default_gate_config(
    tmp_path,
):
    config = load_evaluation_gate_config(
        write_config(
            tmp_path,
            {},
        )
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
    config = load_evaluation_gate_config(
        write_config(
            tmp_path,
            {
                "maximum_failed_analyses": 1,
                "allowed_health_statuses": [
                    "healthy",
                    "watch",
                ],
            },
        )
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
    path = write_config(
        tmp_path,
        {
            "maximum_failed_analyses": -1,
        },
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_non_integer_maximum(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "maximum_failed_analyses": "1",
        },
    )

    with pytest.raises(
        ValueError,
        match="must be an integer",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_boolean_maximum(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "maximum_failed_analyses": True,
        },
    )

    with pytest.raises(
        ValueError,
        match="must be an integer",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_empty_health_statuses(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "allowed_health_statuses": [],
        },
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_non_list_health_statuses(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "allowed_health_statuses": "healthy",
        },
    )

    with pytest.raises(
        ValueError,
        match="must be a JSON list",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_non_string_status(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "allowed_health_statuses": [
                "healthy",
                1,
            ],
        },
    )

    with pytest.raises(
        ValueError,
        match="contain only strings",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_invalid_health_status(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "allowed_health_statuses": [
                "healthy",
                "unknown",
            ],
        },
    )

    with pytest.raises(
        ValueError,
        match="Invalid health status",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_duplicate_health_status(
    tmp_path,
):
    path = write_config(
        tmp_path,
        {
            "allowed_health_statuses": [
                "healthy",
                "healthy",
            ],
        },
    )

    with pytest.raises(
        ValueError,
        match="cannot contain duplicates",
    ):
        load_evaluation_gate_config(
            path
        )


def test_gate_config_rejects_non_object(
    tmp_path,
):
    path = write_config(
        tmp_path,
        [
            "bad"
        ],
    )

    with pytest.raises(
        ValueError,
        match="JSON object",
    ):
        load_evaluation_gate_config(
            path
        )