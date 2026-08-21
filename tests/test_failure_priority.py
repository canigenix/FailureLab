import pytest

from failurelab.failure_priority import (
    FailurePrioritySignal,
    calculate_priority_score,
    classify_priority_level,
    rank_failure_priorities,
)


def test_calculate_priority_score():
    signal = FailurePrioritySignal(
        name="blur",
        failure_rate=0.60,
        prediction_flip_rate=0.40,
        affected_fraction=0.50,
    )

    score = calculate_priority_score(
        signal
    )

    assert score == pytest.approx(
        0.515
    )


def test_priority_score_respects_severity_weight():
    signal = FailurePrioritySignal(
        name="blur",
        failure_rate=0.40,
        prediction_flip_rate=0.20,
        affected_fraction=0.30,
        severity_weight=1.5,
    )

    score = calculate_priority_score(
        signal
    )

    assert score > 0.30


def test_priority_score_is_clamped():
    signal = FailurePrioritySignal(
        name="blur",
        failure_rate=1.0,
        prediction_flip_rate=1.0,
        affected_fraction=1.0,
        severity_weight=2.0,
    )

    assert calculate_priority_score(
        signal
    ) == pytest.approx(1.0)


def test_classify_priority_levels():
    assert classify_priority_level(
        0.10
    ) == "low"

    assert classify_priority_level(
        0.30
    ) == "medium"

    assert classify_priority_level(
        0.60
    ) == "high"

    assert classify_priority_level(
        0.80
    ) == "critical"


def test_rank_failure_priorities():
    signals = [
        FailurePrioritySignal(
            "rotation",
            failure_rate=0.10,
            prediction_flip_rate=0.05,
            affected_fraction=0.10,
        ),
        FailurePrioritySignal(
            "blur",
            failure_rate=0.70,
            prediction_flip_rate=0.50,
            affected_fraction=0.60,
        ),
        FailurePrioritySignal(
            "compression",
            failure_rate=0.30,
            prediction_flip_rate=0.15,
            affected_fraction=0.20,
        ),
    ]

    priorities = rank_failure_priorities(
        signals
    )

    assert len(priorities) == 3
    assert priorities[0].name == "blur"
    assert priorities[1].name == "compression"
    assert priorities[2].name == "rotation"

    assert priorities[0].score > priorities[1].score
    assert priorities[1].score > priorities[2].score


def test_priority_signal_rejects_invalid_values():
    with pytest.raises(
        ValueError,
        match="failure_rate",
    ):
        FailurePrioritySignal(
            name="blur",
            failure_rate=1.1,
            prediction_flip_rate=0.20,
            affected_fraction=0.30,
        )

    with pytest.raises(
        ValueError,
        match="prediction_flip_rate",
    ):
        FailurePrioritySignal(
            name="blur",
            failure_rate=0.20,
            prediction_flip_rate=-0.1,
            affected_fraction=0.30,
        )

    with pytest.raises(
        ValueError,
        match="affected_fraction",
    ):
        FailurePrioritySignal(
            name="blur",
            failure_rate=0.20,
            prediction_flip_rate=0.10,
            affected_fraction=1.1,
        )

    with pytest.raises(
        ValueError,
        match="severity_weight",
    ):
        FailurePrioritySignal(
            name="blur",
            failure_rate=0.20,
            prediction_flip_rate=0.10,
            affected_fraction=0.30,
            severity_weight=-1.0,
        )