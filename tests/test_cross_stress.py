from failurelab.class_analysis import (
    ClassRobustnessResult,
)
from failurelab.cross_stress import (
    analyze_cross_stress_classes,
)
from failurelab.suite_runner import (
    SavedStressResult,
    SuiteResult,
)
from failurelab.cross_stress import (
    CrossStressClassResult,
    analyze_cross_stress_classes,
    classify_cross_stress_severity,
)


def class_result(
    class_index,
    accuracy_drop,
    failure_rate,
    confidence_drop=0.0,
    flip_rate=0.0,
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
        stressed_confidence=(
            0.9 - confidence_drop
        ),
        confidence_drop=confidence_drop,
        stressed_failure_rate=failure_rate,
        prediction_flip_rate=flip_rate,
        top_confusion_class=None,
        top_confusion_rate=0.0,
    )


def test_cross_stress_identifies_repeated_failure():
    suite = SuiteResult(
        name="cross-stress-test",
        results=[
            SavedStressResult(
                name="blur",
                top1_drop=0.2,
                top5_drop=0.0,
                target_confidence_drop=0.1,
                class_results=[
                    class_result(
                        0,
                        accuracy_drop=0.5,
                        failure_rate=0.5,
                    ),
                    class_result(
                        1,
                        accuracy_drop=0.0,
                        failure_rate=0.0,
                    ),
                ],
            ),
            SavedStressResult(
                name="brightness",
                top1_drop=0.3,
                top5_drop=0.0,
                target_confidence_drop=0.2,
                class_results=[
                    class_result(
                        0,
                        accuracy_drop=0.4,
                        failure_rate=0.4,
                    ),
                    class_result(
                        1,
                        accuracy_drop=0.1,
                        failure_rate=0.1,
                    ),
                ],
            ),
        ],
    )

    results = analyze_cross_stress_classes(
        suite
    )

    by_class = {
        row.class_index: row
        for row in results
    }

    assert by_class[0].stress_count == 2
    assert (
        by_class[0].failure_stress_count
        == 2
    )
    assert (
        by_class[0].failure_frequency
        == 1.0
    )

    assert (
        by_class[0].mean_accuracy_drop
        == 0.45
    )

    assert (
        by_class[0].worst_stress
        == "blur"
    )
    assert by_class[0].severity == "systemic"
    assert results[0].class_index == 0


def test_cross_stress_ranks_systemic_vulnerability_first():
    suite = SuiteResult(
        name="ranking-test",
        results=[
            SavedStressResult(
                name="blur",
                top1_drop=0.5,
                top5_drop=0.0,
                target_confidence_drop=0.2,
                class_results=[
                    class_result(
                        0,
                        accuracy_drop=0.6,
                        failure_rate=0.6,
                    ),
                    class_result(
                        1,
                        accuracy_drop=0.8,
                        failure_rate=0.8,
                    ),
                ],
            ),
            SavedStressResult(
                name="noise",
                top1_drop=0.4,
                top5_drop=0.0,
                target_confidence_drop=0.2,
                class_results=[
                    class_result(
                        0,
                        accuracy_drop=0.5,
                        failure_rate=0.5,
                    ),
                    class_result(
                        1,
                        accuracy_drop=0.0,
                        failure_rate=0.0,
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
                        accuracy_drop=0.4,
                        failure_rate=0.4,
                    ),
                    class_result(
                        1,
                        accuracy_drop=0.0,
                        failure_rate=0.0,
                    ),
                ],
            ),
        ],
    )

    results = analyze_cross_stress_classes(
        suite
    )

    assert results[0].class_index == 0
    assert results[0].failure_stress_count == 3
    assert results[0].failure_frequency == 1.0

    assert results[1].class_index == 1
    assert results[1].failure_stress_count == 1
    assert results[0].severity == "systemic"


def test_cross_stress_severity_stable():
    result = CrossStressClassResult(
        class_index=0,
        stress_count=3,
        failure_stress_count=0,
        failure_frequency=0.0,
        mean_accuracy_drop=0.0,
        mean_confidence_drop=0.0,
        mean_failure_rate=0.0,
        mean_flip_rate=0.0,
        worst_stress="blur",
        worst_accuracy_drop=0.0,
    )

    assert (
        classify_cross_stress_severity(result)
        == "stable"
    )


def test_cross_stress_severity_localized():
    result = CrossStressClassResult(
        class_index=0,
        stress_count=3,
        failure_stress_count=1,
        failure_frequency=1 / 3,
        mean_accuracy_drop=0.2,
        mean_confidence_drop=0.1,
        mean_failure_rate=0.2,
        mean_flip_rate=0.1,
        worst_stress="blur",
        worst_accuracy_drop=0.5,
    )

    assert (
        classify_cross_stress_severity(result)
        == "localized"
    )


def test_cross_stress_severity_systemic():
    result = CrossStressClassResult(
        class_index=0,
        stress_count=3,
        failure_stress_count=3,
        failure_frequency=1.0,
        mean_accuracy_drop=0.4,
        mean_confidence_drop=0.3,
        mean_failure_rate=0.5,
        mean_flip_rate=0.4,
        worst_stress="brightness",
        worst_accuracy_drop=0.7,
    )

    assert (
        classify_cross_stress_severity(result)
        == "systemic"
    )

    