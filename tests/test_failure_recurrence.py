import pytest

from failurelab.failure_recurrence import (
    FailureOccurrence,
    analyze_failure_recurrence,
)


def test_failure_recurrence_analysis():
    occurrences = [
        FailureOccurrence(
            "v1",
            "blur",
            0.80,
        ),
        FailureOccurrence(
            "v2",
            "blur",
            0.70,
        ),
        FailureOccurrence(
            "v3",
            "blur",
            0.60,
        ),
        FailureOccurrence(
            "v1",
            "rotation",
            0.40,
        ),
    ]

    results = analyze_failure_recurrence(
        occurrences
    )

    assert len(results) == 2

    blur = results[0]

    assert blur.failure_name == "blur"
    assert blur.occurrence_count == 3
    assert blur.checkpoint_count == 3
    assert blur.recurrence_rate == pytest.approx(
        1.0
    )
    assert blur.mean_priority_score == pytest.approx(
        0.70
    )
    assert blur.max_priority_score == pytest.approx(
        0.80
    )
    assert blur.checkpoints == (
        "v1",
        "v2",
        "v3",
    )


def test_failure_recurrence_ranks_persistent_failures_first():
    occurrences = [
        FailureOccurrence(
            "v1",
            "blur",
            0.50,
        ),
        FailureOccurrence(
            "v2",
            "blur",
            0.50,
        ),
        FailureOccurrence(
            "v3",
            "blur",
            0.50,
        ),
        FailureOccurrence(
            "v1",
            "compression",
            0.90,
        ),
    ]

    results = analyze_failure_recurrence(
        occurrences
    )

    assert results[0].failure_name == "blur"
    assert results[1].failure_name == "compression"


def test_failure_recurrence_empty_input():
    assert analyze_failure_recurrence(
        []
    ) == []


def test_failure_occurrence_rejects_invalid_score():
    with pytest.raises(
        ValueError,
        match="priority_score",
    ):
        FailureOccurrence(
            "v1",
            "blur",
            1.1,
        )

    with pytest.raises(
        ValueError,
        match="priority_score",
    ):
        FailureOccurrence(
            "v1",
            "blur",
            -0.1,
        )