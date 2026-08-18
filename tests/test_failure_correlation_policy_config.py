import json

import pytest

from failurelab.failure_correlation_policy_config import (
    load_failure_correlation_policy,
)


def test_load_correlation_policy(
    tmp_path,
):
    path = tmp_path / "correlation-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_correlation": 0.80,
                "maximum_high_correlation_pairs": 2,
                "high_correlation_threshold": 0.70,
            }
        ),
        encoding="utf-8",
    )

    policy = load_failure_correlation_policy(
        path
    )

    assert policy.maximum_correlation == 0.80
    assert policy.maximum_high_correlation_pairs == 2
    assert policy.high_correlation_threshold == 0.70


def test_load_correlation_policy_defaults_threshold(
    tmp_path,
):
    path = tmp_path / "correlation-policy.json"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    policy = load_failure_correlation_policy(
        path
    )

    assert policy.high_correlation_threshold == 0.75


def test_load_correlation_policy_rejects_invalid_correlation(
    tmp_path,
):
    path = tmp_path / "correlation-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_correlation": 1.5,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="between 0.0 and 1.0",
    ):
        load_failure_correlation_policy(
            path
        )


def test_load_correlation_policy_rejects_negative_pair_count(
    tmp_path,
):
    path = tmp_path / "correlation-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_high_correlation_pairs": -1,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        load_failure_correlation_policy(
            path
        )