import numpy as np
from PIL import Image

from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.robustness_policy import (
    RobustnessPolicy,
    StressPolicy,
    evaluate_policy,
)
from failurelab.suite_runner import ConfiguredSuiteRunner


def predict_proba(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness,
            1.0 - brightness,
        ]
    )


def build_result():
    config = SuiteConfig(
        name="production-vision",
        stresses=[
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.2,
                },
            ),
        ],
    )

    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    runner = ConfiguredSuiteRunner(
        predict_proba
    )

    return runner.run(
        dataset=[(image, 0)],
        config=config,
    )


def test_policy_detects_global_violation():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=0.10,
    )

    evaluation = evaluate_policy(
        result,
        policy,
    )

    assert evaluation.status == "failed"
    assert not evaluation.passed
    assert len(evaluation.violations) >= 1
    assert evaluation.violations[0].metric == "top1_drop"


def test_policy_passes_when_within_limits():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
        maximum_top5_drop=1.0,
        maximum_confidence_drop=1.0,
    )

    evaluation = evaluate_policy(
        result,
        policy,
    )

    assert evaluation.passed
    assert evaluation.status == "passed"
    assert evaluation.violations == []
    assert evaluation.warnings == []


def test_policy_supports_stress_specific_limits():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
        stresses={
            "brightness": StressPolicy(
                maximum_top1_drop=0.10,
            )
        },
    )

    evaluation = evaluate_policy(
        result,
        policy,
    )

    assert not evaluation.passed

    assert any(
        violation.stress_name.startswith(
            "brightness"
        )
        for violation in evaluation.violations
    )


def test_policy_reports_warning_without_failure():
    result = build_result()

    policy = RobustnessPolicy(
        warning_top1_drop=0.10,
        maximum_top1_drop=1.0,
    )

    evaluation = evaluate_policy(
        result,
        policy,
    )

    assert evaluation.passed
    assert evaluation.status == "warning"
    assert evaluation.violations == []
    assert len(evaluation.warnings) >= 1

    assert (
        evaluation.warnings[0].severity
        == "warning"
    )


def test_failure_takes_priority_over_warning():
    result = build_result()

    policy = RobustnessPolicy(
        warning_top1_drop=0.01,
        maximum_top1_drop=0.10,
    )

    evaluation = evaluate_policy(
        result,
        policy,
    )

    assert not evaluation.passed
    assert evaluation.status == "failed"
    assert len(evaluation.violations) >= 1


def test_warning_cannot_exceed_failure_threshold():
    result = build_result()

    policy = RobustnessPolicy(
        warning_top1_drop=0.30,
        maximum_top1_drop=0.20,
    )

    try:
        evaluate_policy(
            result,
            policy,
        )
    except ValueError as exc:
        assert (
            "warning threshold cannot exceed"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected invalid warning threshold to fail."
        )