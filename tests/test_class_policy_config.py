import json

from failurelab.class_policy_config import (
    load_class_policy,
)



def test_load_class_policy_reads_minimum_class_coverage(
    tmp_path,
):
    path = tmp_path / "class-policy.json"

    path.write_text(
        json.dumps(
            {
                "minimum_class_coverage": 0.80,
                "default": {
                    "minimum_samples": 25
                },
            }
        ),
        encoding="utf-8",
    )

    loaded = load_class_policy(
        path
    )

    assert loaded.minimum_class_coverage == 0.80

    default_policy, class_policies = loaded

    assert default_policy.minimum_samples == 25
    assert class_policies == {}


def test_load_class_policy_rejects_invalid_class_coverage(
    tmp_path,
):
    path = tmp_path / "class-policy.json"

    path.write_text(
        json.dumps(
            {
                "minimum_class_coverage": 1.25
            }
        ),
        encoding="utf-8",
    )

    try:
        load_class_policy(path)
    except ValueError as exc:
        assert "between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid minimum_class_coverage to fail."
        )