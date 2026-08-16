import json

import numpy as np
from PIL import Image

from failurelab.class_policy import ClassPolicy
from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.policy_report import (
    build_policy_report,
)
from failurelab.robustness_policy import (
    RobustnessPolicy,
)
from failurelab.suite_runner import (
    ConfiguredSuiteRunner,
)


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
        maximum_drop=1.0,
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


def test_policy_report_passes():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
        maximum_top5_drop=1.0,
        maximum_confidence_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            maximum_accuracy_drop=1.0,
            maximum_confidence_drop=1.0,
            maximum_failure_rate=1.0,
            maximum_flip_rate=1.0,
        ),
    )

    assert report.passed
    assert report.status == "passed"
    assert report.policy_status == "passed"
    assert report.class_policy_status == "passed"


def test_policy_report_detects_global_failure():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=0.01,
    )

    report = build_policy_report(
        result,
        policy,
    )

    assert not report.passed
    assert report.status == "failed"
    assert report.policy_status == "failed"
    assert len(report.evaluation.violations) >= 1


def test_policy_report_detects_class_failure():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
        maximum_top5_drop=1.0,
        maximum_confidence_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            maximum_failure_rate=0.01,
        ),
    )

    assert not report.passed
    assert report.status == "failed"
    assert report.class_policy_status == "failed"
    assert (
        len(
            report.class_evaluation.violations
        )
        >= 1
    )


def test_policy_report_saves_json(tmp_path):
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=0.01,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            maximum_failure_rate=0.01,
        ),
    )

    path = tmp_path / "policy-report.json"

    report.save_json(path)

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "production-vision"
    assert data["status"] == "failed"
    assert data["policy_status"] == "failed"
    assert data["class_policy_status"] == "failed"
    assert data["violation_count"] >= 1
    assert data["class_violation_count"] >= 1