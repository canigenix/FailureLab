import pytest

from failurelab.failure_forecast import (
    classify_forecast_status,
    forecast_failure_trajectory,
)
from failurelab.failure_recurrence import (
    FailureOccurrence,
)


def test_classify_forecast_status():
    assert classify_forecast_status(
        -0.10
    ) == "improving"

    assert classify_forecast_status(
        0.0
    ) == "stable"

    assert classify_forecast_status(
        0.10
    ) == "worsening"


def test_forecast_improving_failure():
    result = forecast_failure_trajectory(
        [
            FailureOccurrence(
                "v1",
                "blur",
                0.80,
            ),
            FailureOccurrence(
                "v2",
                "blur",
                0.60,
            ),
            FailureOccurrence(
                "v3",
                "blur",
                0.40,
            ),
        ]
    )[0]

    assert result.failure_name == "blur"
    assert result.observation_count == 3
    assert result.latest_score == pytest.approx(
        0.40
    )
    assert result.average_change == pytest.approx(
        -0.20
    )
    assert result.projected_score == pytest.approx(
        0.20
    )
    assert result.status == "improving"


def test_forecast_worsening_failure():
    result = forecast_failure_trajectory(
        [
            FailureOccurrence(
                "v1",
                "rotation",
                0.20,
            ),
            FailureOccurrence(
                "v2",
                "rotation",
                0.40,
            ),
            FailureOccurrence(
                "v3",
                "rotation",
                0.60,
            ),
        ]
    )[0]

    assert result.average_change == pytest.approx(
        0.20
    )
    assert result.projected_score == pytest.approx(
        0.80
    )
    assert result.status == "worsening"


def test_forecast_respects_tolerance():
    result = forecast_failure_trajectory(
        [
            FailureOccurrence(
                "v1",
                "blur",
                0.50,
            ),
            FailureOccurrence(
                "v2",
                "blur",
                0.505,
            ),
        ],
        tolerance=0.01,
    )[0]

    assert result.status == "stable"


def test_forecast_clamps_projected_score():
    result = forecast_failure_trajectory(
        [
            FailureOccurrence(
                "v1",
                "blur",
                0.80,
            ),
            FailureOccurrence(
                "v2",
                "blur",
                1.00,
            ),
        ]
    )[0]

    assert result.projected_score == pytest.approx(
        1.0
    )


def test_forecast_single_occurrence():
    result = forecast_failure_trajectory(
        [
            FailureOccurrence(
                "v1",
                "crop",
                0.30,
            ),
        ]
    )[0]

    assert (
        result.status
        == "insufficient_history"
    )
    assert result.projected_score == pytest.approx(
        0.30
    )


def test_forecast_rejects_negative_tolerance():
    with pytest.raises(
        ValueError,
        match="tolerance",
    ):
        classify_forecast_status(
            0.0,
            tolerance=-0.01,
        )