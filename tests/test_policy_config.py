import json
from failurelab.policy_config import load_robustness_policy


def test_load_robustness_policy_reads_warning_thresholds(
    tmp_path,
):
    path = tmp_path / "policy.json"

    path.write_text(
        json.dumps(
            {
                "warning_top1_drop": 0.10,
                "maximum_top1_drop": 0.20,
                "stresses": {
                    "brightness": {
                        "warning_confidence_drop": 0.08,
                        "maximum_confidence_drop": 0.15,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    policy = load_robustness_policy(
        path
    )

    assert policy.warning_top1_drop == 0.10
    assert policy.maximum_top1_drop == 0.20

    assert (
        policy.stresses[
            "brightness"
        ].warning_confidence_drop
        == 0.08
    )

    assert (
        policy.stresses[
            "brightness"
        ].maximum_confidence_drop
        == 0.15
    )


def test_load_robustness_policy_rejects_negative_warning(
    tmp_path,
):
    path = tmp_path / "policy.json"

    path.write_text(
        json.dumps(
            {
                "warning_top1_drop": -0.10
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
            "Expected negative warning threshold to fail."
        )