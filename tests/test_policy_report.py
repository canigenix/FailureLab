import json

import numpy as np
from PIL import Image

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
    )

    assert report.passed
    assert report.status == "passed"
    assert report.policy_status == "passed"
    assert report.suite_name == "production-vision"
    assert report.evaluation.violations == []


def test_policy_report_detects_failure():
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


def test_policy_report_saves_json(tmp_path):
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=0.01,
    )

    report = build_policy_report(
        result,
        policy,
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
    assert data["violation_count"] >= 1

    violation = data["violations"][0]

    assert violation["stress_name"].startswith(
        "brightness"
    )

    assert violation["metric"] == "top1_drop"
    assert violation["observed"] > violation["allowed"]