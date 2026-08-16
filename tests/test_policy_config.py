import json

from failurelab.policy_config import (
    load_robustness_policy,
)


def test_load_robustness_policy(tmp_path):
    path = tmp_path / "policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_top1_drop": 0.20,
                "maximum_top5_drop": 0.15,
                "maximum_confidence_drop": 0.25,
                "stresses": {
                    "brightness": {
                        "maximum_top1_drop": 0.10
                    },
                    "blur": {
                        "maximum_confidence_drop": 0.12
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    policy = load_robustness_policy(
        path
    )

    assert policy.maximum_top1_drop == 0.20
    assert policy.maximum_top5_drop == 0.15
    assert policy.maximum_confidence_drop == 0.25

    assert (
        policy.stresses[
            "brightness"
        ].maximum_top1_drop
        == 0.10
    )

    assert (
        policy.stresses[
            "blur"
        ].maximum_confidence_drop
        == 0.12
    )


def test_load_robustness_policy_rejects_negative_limit(
    tmp_path,
):
    path = tmp_path / "policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_top1_drop": -0.10
            }
        ),
        encoding="utf-8",
    )

    try:
        load_robustness_policy(path)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError(
            "Expected negative policy limit to fail."
        )


def test_load_robustness_policy_rejects_invalid_stresses(
    tmp_path,
):
    path = tmp_path / "policy.json"

    path.write_text(
        json.dumps(
            {
                "stresses": []
            }
        ),
        encoding="utf-8",
    )

    try:
        load_robustness_policy(path)
    except ValueError as exc:
        assert "'stresses' must be an object" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid stresses configuration to fail."
        )