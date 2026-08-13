import numpy as np

from failurelab.class_analysis import analyze_class_robustness


def test_class_analysis_ranks_most_affected_class_first():
    baseline = np.array(
        [
            [0.90, 0.10],
            [0.80, 0.20],
            [0.10, 0.90],
            [0.20, 0.80],
        ]
    )

    stressed = np.array(
        [
            [0.55, 0.45],
            [0.40, 0.60],
            [0.15, 0.85],
            [0.25, 0.75],
        ]
    )

    targets = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    results = analyze_class_robustness(
        baseline,
        stressed,
        targets,
    )

    assert results[0].class_index == 0
    assert results[0].sample_count == 2
    assert results[0].accuracy_drop == 0.5
    assert results[0].confidence_drop > 0.0

    assert results[1].class_index == 1


def test_class_analysis_identifies_top_confusion_class():
    baseline = np.array(
        [
            [0.90, 0.05, 0.05],
            [0.80, 0.10, 0.10],
            [0.10, 0.80, 0.10],
            [0.10, 0.75, 0.15],
        ]
    )

    stressed = np.array(
        [
            [0.20, 0.70, 0.10],
            [0.30, 0.60, 0.10],
            [0.10, 0.70, 0.20],
            [0.10, 0.65, 0.25],
        ]
    )

    targets = np.array([0, 0, 1, 1])

    results = analyze_class_robustness(
        baseline,
        stressed,
        targets,
    )

    by_class = {
        result.class_index: result
        for result in results
    }

    assert by_class[0].top_confusion_class == 1
    assert by_class[0].top_confusion_rate == 1.0

    assert by_class[1].top_confusion_class is None
    assert by_class[1].top_confusion_rate == 0.0