import numpy as np

from failurelab.sample_analysis import (
    SampleFailureResult,
    analyze_sample_failures,
    classify_sample_failure_severity,
)
from failurelab.suite_runner import (
    SuiteResult,
)
from failurelab.vision_metrics import (
    VisionMetrics,
)
from failurelab.vision_runner import (
    VisionStressResult,
)


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


def test_sample_analysis_tracks_repeated_failures():
    suite = SuiteResult(
        name="sample-test",
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
                targets=[
                    0,
                    1,
                ],
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
                targets=[
                    0,
                    1,
                ],
            ),
        ],
    )

    results = analyze_sample_failures(
        suite
    )

    by_index = {
        row.sample_index: row
        for row in results
    }

    assert (
        by_index[0].failure_stress_count
        == 2
    )

    assert (
        by_index[0].failure_frequency
        == 1.0
    )

    assert by_index[0].failed_stresses == [
        "blur",
        "brightness",
    ]

    assert (
        by_index[1].failure_stress_count
        == 1
    )

    assert (
        by_index[1].failure_frequency
        == 0.5
    )

    assert results[0].sample_index == 0
    assert by_index[0].severity == "systemic"
    assert by_index[1].severity == "localized"


def test_sample_analysis_tracks_prediction_flips():
    suite = SuiteResult(
        name="flip-test",
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
                targets=[
                    0,
                    1,
                ],
            ),
        ],
    )

    results = analyze_sample_failures(
        suite
    )

    by_index = {
        row.sample_index: row
        for row in results
    }

    assert by_index[0].flip_stress_count == 1
    assert by_index[0].flip_frequency == 1.0
    assert by_index[0].flipped_stresses == [
        "blur"
    ]

    assert by_index[1].flip_stress_count == 0


def test_sample_failure_severity():
    stable = SampleFailureResult(
        sample_index=0,
        target=0,
        stress_count=3,
        failure_stress_count=0,
        failure_frequency=0.0,
        flip_stress_count=0,
        flip_frequency=0.0,
        failed_stresses=[],
        flipped_stresses=[],
    )

    localized = SampleFailureResult(
        sample_index=1,
        target=0,
        stress_count=3,
        failure_stress_count=1,
        failure_frequency=1 / 3,
        flip_stress_count=1,
        flip_frequency=1 / 3,
        failed_stresses=["blur"],
        flipped_stresses=["blur"],
    )

    systemic = SampleFailureResult(
        sample_index=2,
        target=0,
        stress_count=3,
        failure_stress_count=3,
        failure_frequency=1.0,
        flip_stress_count=3,
        flip_frequency=1.0,
        failed_stresses=[
            "blur",
            "noise",
            "brightness",
        ],
        flipped_stresses=[
            "blur",
            "noise",
            "brightness",
        ],
    )

    assert classify_sample_failure_severity(stable) == "stable"
    assert classify_sample_failure_severity(localized) == "localized"
    assert classify_sample_failure_severity(systemic) == "systemic"