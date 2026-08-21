import pytest

from failurelab.failure_recurrence import (
    FailureOccurrence,
)
from failurelab.failure_resolution import (
    analyze_failure_resolution,
    classify_resolution_status,
)


def test_classify_resolution_status():
    assert classify_resolution_status(
        0.80,
        0.50,
    ) == "improving"

    assert classify_resolution_status(
        0.50,
        0.80,
    ) == "worsening"

    assert classify_resolution_status(
        0.50,
        0.50,
    ) == "unchanged"


def test_resolution_respects_tolerance():
    assert classify_resolution_status(
        0.50,
        0.505,
        tolerance=0.01,
    ) == "unchanged"


def test_analyze_failure_resolution():
    results = analyze_failure_resolution(
        [
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
                0.50,
            ),
        ]
    )

    assert len(results) == 1

    result = results[0]

    assert result.failure_name == "blur"
    assert result.first_score == pytest.approx(
        0.80
    )
    assert result.latest_score == pytest.approx(
        0.50
    )
    assert result.score_delta == pytest.approx(
        -0.30
    )
    assert result.occurrence_count == 3
    assert result.status == "improving"


def test_resolution_detects_worsening_failure():
    result = analyze_failure_resolution(
        [
            FailureOccurrence(
                "v1",
                "rotation",
                0.30,
            ),
            FailureOccurrence(
                "v2",
                "rotation",
                0.60,
            ),
        ]
    )[0]

    assert result.status == "worsening"
    assert result.score_delta > 0


def test_resolution_handles_single_occurrence():
    result = analyze_failure_resolution(
        [
            FailureOccurrence(
                "v1",
                "crop",
                0.40,
            ),
        ]
    )[0]

    assert result.status == "insufficient_history"
    assert result.occurrence_count == 1


def test_resolution_rejects_negative_tolerance():
    with pytest.raises(
        ValueError,
        match="tolerance",
    ):
        classify_resolution_status(
            0.50,
            0.50,
            tolerance=-0.01,
        )