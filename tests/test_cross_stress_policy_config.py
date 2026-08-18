import json

from failurelab.cross_stress_policy_config import (
    load_cross_stress_policy,
)


def test_load_cross_stress_policy(tmp_path):
    path = tmp_path / "cross-stress-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_systemic_classes": 2,
                "maximum_systemic_fraction": 0.25,
            }
        ),
        encoding="utf-8",
    )

    policy = load_cross_stress_policy(
        path
    )

    assert policy.maximum_systemic_classes == 2
    assert policy.maximum_systemic_fraction == 0.25


def test_load_cross_stress_policy_rejects_negative_count(
    tmp_path,
):
    path = tmp_path / "cross-stress-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_systemic_classes": -1
            }
        ),
        encoding="utf-8",
    )

    try:
        load_cross_stress_policy(path)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError(
            "Expected negative systemic count to fail."
        )


def test_load_cross_stress_policy_rejects_invalid_fraction(
    tmp_path,
):
    path = tmp_path / "cross-stress-policy.json"

    path.write_text(
        json.dumps(
            {
                "maximum_systemic_fraction": 1.25
            }
        ),
        encoding="utf-8",
    )

    try:
        load_cross_stress_policy(path)
    except ValueError as exc:
        assert "between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid systemic fraction to fail."
        )