import json

import pytest

from failurelab.failure_cluster_policy_config import (
    load_failure_cluster_policy,
)


def test_load_cluster_policy(
    tmp_path,
):
    path = tmp_path / "cluster-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_clusters": 3,
                "maximum_cluster_size": 4,
            }
        ),
        encoding="utf-8",
    )

    policy = load_failure_cluster_policy(
        path
    )

    assert policy.maximum_clusters == 3
    assert policy.maximum_cluster_size == 4


def test_load_cluster_policy_allows_empty_policy(
    tmp_path,
):
    path = tmp_path / "cluster-policy.json"

    path.write_text(
        "{}",
        encoding="utf-8",
    )

    policy = load_failure_cluster_policy(
        path
    )

    assert policy.maximum_clusters is None
    assert policy.maximum_cluster_size is None


def test_load_cluster_policy_rejects_negative_limit(
    tmp_path,
):
    path = tmp_path / "cluster-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_cluster_size": -1,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        load_failure_cluster_policy(
            path
        )


def test_load_cluster_policy_rejects_non_integer(
    tmp_path,
):
    path = tmp_path / "cluster-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_clusters": 1.5,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="must be an integer",
    ):
        load_failure_cluster_policy(
            path
        )