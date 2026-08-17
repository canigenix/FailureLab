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
        dataset=[
            (image, 0),
        ],
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
    assert len(
        report.evaluation.violations
    ) >= 1


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


def test_policy_report_tracks_skipped_classes():
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
            minimum_samples=2,
        ),
    )

    assert report.class_evaluation.evaluated_classes == 0
    assert report.class_evaluation.skipped_classes == 1
    assert report.class_policy_status == "passed"


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

    report.save_json(
        path
    )

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

    assert "evaluated_classes" in data
    assert "skipped_classes" in data

    assert (
        data["class_violations"][0]["sample_count"]
        == 1
    )


def test_policy_report_preserves_warning_status():
    result = build_result()

    policy = RobustnessPolicy(
        warning_top1_drop=0.10,
        maximum_top1_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
    )

    assert report.passed
    assert report.has_warnings
    assert report.status == "warning"
    assert report.policy_status == "warning"

    data = report.to_dict()

    assert data["status"] == "warning"
    assert data["warning_count"] >= 1
    assert data["violation_count"] == 0
    assert data["warnings"][0]["severity"] == "warning"


def test_policy_report_enforces_class_coverage():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            maximum_failure_rate=1.0,
            minimum_samples=2,
        ),
        minimum_class_coverage=0.80,
    )

    assert not report.passed
    assert report.status == "failed"
    assert report.class_policy_status == "failed"

    assert report.class_evaluation.class_coverage == 0.0
    assert not report.class_evaluation.coverage_passed


def test_policy_report_exports_class_coverage():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            maximum_failure_rate=1.0,
            minimum_samples=1,
        ),
        minimum_class_coverage=0.80,
    )

    data = report.to_dict()

    assert data["total_classes"] == 1
    assert data["class_coverage"] == 1.0
    assert data["minimum_class_coverage"] == 0.80
    assert data["coverage_passed"]


def test_policy_report_preserves_class_warning_status():
    result = build_result()

    policy = RobustnessPolicy(
        maximum_top1_drop=1.0,
    )

    report = build_policy_report(
        result,
        policy,
        default_class_policy=ClassPolicy(
            warning_failure_rate=0.01,
            maximum_failure_rate=1.0,
        ),
    )

    assert report.passed
    assert report.has_warnings
    assert report.status == "warning"
    assert report.class_policy_status == "warning"

    data = report.to_dict()

    assert data["class_warning_count"] >= 1
    assert len(data["class_warnings"]) >= 1
    assert data["class_warnings"][0]["severity"] == "warning"