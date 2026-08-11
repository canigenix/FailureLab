import numpy as np
import pytest

from failurelab.analyzer import FailureAnalyzer


def test_accuracy_and_failure_rate():
    y_true = [0, 1, 1, 0]
    y_pred = [0, 1, 0, 0]

    analyzer = FailureAnalyzer(
        y_true,
        y_pred,
    )

    assert analyzer.accuracy() == 0.75
    assert analyzer.failure_rate() == 0.25


def test_failure_indices():
    y_true = [0, 1, 1, 0]
    y_pred = [0, 0, 1, 1]

    analyzer = FailureAnalyzer(
        y_true,
        y_pred,
    )

    np.testing.assert_array_equal(
        analyzer.failure_indices(),
        np.array([1, 3]),
    )


def test_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        FailureAnalyzer(
            y_true=[0, 1, 1],
            y_pred=[0, 1],
        )


def test_failures_returns_structured_cases():
    analyzer = FailureAnalyzer(
        y_true=[0, 1, 2],
        y_pred=[0, 2, 1],
    )

    failures = analyzer.failures()

    assert len(failures) == 2

    assert failures[0].index == 1
    assert failures[0].actual == 1
    assert failures[0].predicted == 2

    assert failures[1].index == 2
    assert failures[1].actual == 2
    assert failures[1].predicted == 1


def test_failure_confidence_uses_predicted_probability():
    analyzer = FailureAnalyzer(
        y_true=[0, 1],
        y_pred=[0, 0],
        probabilities=[
            [0.90, 0.10],
            [0.80, 0.20],
        ],
    )

    failures = analyzer.failures()

    assert len(failures) == 1
    assert failures[0].confidence == pytest.approx(
        0.80
    )


def test_high_confidence_failures():
    analyzer = FailureAnalyzer(
        y_true=[0, 1, 2, 1],
        y_pred=[0, 2, 1, 0],
        probabilities=[
            [0.96, 0.03, 0.01],
            [0.02, 0.03, 0.95],
            [0.05, 0.88, 0.07],
            [0.91, 0.08, 0.01],
        ],
    )

    failures = analyzer.high_confidence_failures(
        threshold=0.90
    )

    assert len(failures) == 2

    assert failures[0].index == 1
    assert failures[0].confidence == pytest.approx(
        0.95
    )

    assert failures[1].index == 3
    assert failures[1].confidence == pytest.approx(
        0.91
    )


def test_high_confidence_failures_requires_probabilities():
    analyzer = FailureAnalyzer(
        y_true=[0, 1],
        y_pred=[0, 0],
    )

    with pytest.raises(ValueError):
        analyzer.high_confidence_failures()