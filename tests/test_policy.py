from failurelab.policy import (
    load_policy,
    save_policy,
)
from failurelab.regression import RobustnessThreshold


def test_policy_round_trip(tmp_path):
    thresholds = [
        RobustnessThreshold(
            stress_name="blur_3.00",
            maximum_top1_drop=0.25,
            maximum_confidence_drop=0.20,
        ),
        RobustnessThreshold(
            stress_name="occlusion_0.40",
            minimum_top1_accuracy=0.50,
        ),
    ]

    path = (
        tmp_path
        / "failurelab_policy.json"
    )

    save_policy(
        thresholds,
        path,
    )

    loaded = load_policy(
        path
    )

    assert loaded == thresholds


def test_policy_file_is_created(tmp_path):
    path = (
        tmp_path
        / "policy.json"
    )

    save_policy(
        [
            RobustnessThreshold(
                stress_name="blur_3.00",
                maximum_top1_drop=0.25,
            )
        ],
        path,
    )

    assert path.exists()