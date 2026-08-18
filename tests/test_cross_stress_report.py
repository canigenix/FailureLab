import json

from failurelab.class_analysis import (
    ClassRobustnessResult,
)
from failurelab.cross_stress_report import (
    build_cross_stress_report,
)
from failurelab.suite_runner import (
    SavedStressResult,
    SuiteResult,
)


def class_result(
    class_index,
    accuracy_drop,
    failure_rate,
):
    return ClassRobustnessResult(
        class_index=class_index,
        sample_count=10,
        baseline_accuracy=1.0,
        stressed_accuracy=(
            1.0 - accuracy_drop
        ),
        accuracy_drop=accuracy_drop,
        baseline_confidence=0.9,
        stressed_confidence=0.8,
        confidence_drop=0.1,
        stressed_failure_rate=failure_rate,
        prediction_flip_rate=failure_rate,
        top_confusion_class=None,
        top_confusion_rate=0.0,
    )


def build_suite():
    return SuiteResult(
        name="production-vision",
        results=[
            SavedStressResult(
                name="blur",
                top1_drop=0.4,
                top5_drop=0.0,
                target_confidence_drop=0.1,
                class_results=[
                    class_result(
                        0,
                        0.5,
                        0.5,
                    ),
                    class_result(
                        1,
                        0.0,
                        0.0,
                    ),
                ],
            ),
            SavedStressResult(
                name="brightness",
                top1_drop=0.3,
                top5_drop=0.0,
                target_confidence_drop=0.1,
                class_results=[
                    class_result(
                        0,
                        0.4,
                        0.4,
                    ),
                    class_result(
                        1,
                        0.0,
                        0.0,
                    ),
                ],
            ),
        ],
    )


def test_cross_stress_report_summarizes_classes():
    report = build_cross_stress_report(
        build_suite()
    )

    assert report.suite_name == "production-vision"
    assert report.class_count == 2
    assert report.systemic_count == 1
    assert report.stable_count == 1


def test_cross_stress_report_saves_json(
    tmp_path,
):
    report = build_cross_stress_report(
        build_suite()
    )

    path = tmp_path / "cross-stress.json"

    report.save_json(
        path
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "production-vision"
    assert data["class_count"] == 2
    assert data["systemic_count"] == 1

    assert (
        data["classes"][0]["severity"]
        == "systemic"
    )