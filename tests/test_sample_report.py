import json

import numpy as np

from failurelab.sample_report import (
    build_sample_failure_report,
)
from failurelab.suite_runner import SuiteResult
from failurelab.vision_metrics import VisionMetrics
from failurelab.vision_runner import VisionStressResult


def stress_result(
    name,
    baseline,
    stressed,
    targets,
):
    return VisionStressResult(
        name=name,
        baseline=VisionMetrics(
            top1_accuracy=1.0,
            top5_accuracy=1.0,
            mean_target_confidence=0.9,
        ),
        stressed=VisionMetrics(
            top1_accuracy=0.5,
            top5_accuracy=1.0,
            mean_target_confidence=0.6,
        ),
        baseline_probabilities=np.asarray(
            baseline,
            dtype=float,
        ),
        stressed_probabilities=np.asarray(
            stressed,
            dtype=float,
        ),
        targets=np.asarray(
            targets,
            dtype=int,
        ),
    )


def build_suite():
    return SuiteResult(
        name="sample-report-test",
        results=[
            stress_result(
                "blur",
                baseline=[
                    [0.9, 0.1],
                    [0.1, 0.9],
                ],
                stressed=[
                    [0.2, 0.8],
                    [0.1, 0.9],
                ],
                targets=[0, 1],
            ),
            stress_result(
                "brightness",
                baseline=[
                    [0.9, 0.1],
                    [0.1, 0.9],
                ],
                stressed=[
                    [0.3, 0.7],
                    [0.8, 0.2],
                ],
                targets=[0, 1],
            ),
        ],
    )


def test_sample_report_summarizes_failures():
    report = build_sample_failure_report(
        build_suite()
    )

    assert report.suite_name == "sample-report-test"
    assert report.sample_count == 2
    assert report.systemic_count == 1
    assert report.localized_count == 1
    assert report.stable_count == 0


def test_sample_report_saves_json(
    tmp_path,
):
    report = build_sample_failure_report(
        build_suite()
    )

    path = tmp_path / "sample-report.json"

    report.save_json(
        path
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "sample-report-test"
    assert data["sample_count"] == 2
    assert data["systemic_count"] == 1
    assert data["samples"][0]["severity"] == "systemic"