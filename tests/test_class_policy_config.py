import json

from failurelab.class_policy_config import (
    load_class_policy,
)


def test_load_class_policy(tmp_path):
    path = tmp_path / "class-policy.json"

    path.write_text(
        json.dumps(
            {
                "default": {
                    "maximum_failure_rate": 0.40,
                    "maximum_flip_rate": 0.30,
                },
                "classes": {
                    "0": {
                        "maximum_accuracy_drop": 0.10
                    },
                    "1": {
                        "maximum_confidence_drop": 0.15
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    default_policy, class_policies = (
        load_class_policy(
            path
        )
    )

    assert (
        default_policy.maximum_failure_rate
        == 0.40
    )

    assert (
        default_policy.maximum_flip_rate
        == 0.30
    )

    assert (
        class_policies[
            0
        ].maximum_accuracy_drop
        == 0.10
    )

    assert (
        class_policies[
            1
        ].maximum_confidence_drop
        == 0.15
    )


def test_load_class_policy_rejects_invalid_class_index(
    tmp_path,
):
    path = tmp_path / "class-policy.json"

    path.write_text(
        json.dumps(
            {
                "classes": {
                    "dog": {
                        "maximum_failure_rate": 0.2
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    try:
        load_class_policy(path)
    except ValueError as exc:
        assert "integer class index" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid class index to fail."
        )


def test_load_class_policy_rejects_negative_limit(
    tmp_path,
):
    path = tmp_path / "class-policy.json"

    path.write_text(
        json.dumps(
            {
                "default": {
                    "maximum_flip_rate": -0.1
                }
            }
        ),
        encoding="utf-8",
    )

    try:
        load_class_policy(path)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError(
            "Expected negative class policy limit to fail."
        )