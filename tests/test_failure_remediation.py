import pytest

from failurelab.failure_priority import (
    FailurePriority,
)
from failurelab.failure_remediation import (
    build_failure_remediations,
    identify_primary_driver,
    remediation_for_driver,
)


def make_priority(
    *,
    failure_rate=0.0,
    prediction_flip_rate=0.0,
    affected_fraction=0.0,
):
    return FailurePriority(
        name="test",
        score=0.50,
        level="high",
        failure_rate=failure_rate,
        prediction_flip_rate=prediction_flip_rate,
        affected_fraction=affected_fraction,
    )


def test_identifies_failure_rate_driver():
    priority = make_priority(
        failure_rate=0.80,
        prediction_flip_rate=0.20,
        affected_fraction=0.20,
    )

    assert identify_primary_driver(
        priority
    ) == "failure_rate"


def test_identifies_prediction_instability_driver():
    priority = make_priority(
        failure_rate=0.10,
        prediction_flip_rate=0.80,
        affected_fraction=0.10,
    )

    assert identify_primary_driver(
        priority
    ) == "prediction_instability"


def test_identifies_failure_breadth_driver():
    priority = make_priority(
        failure_rate=0.10,
        prediction_flip_rate=0.10,
        affected_fraction=0.90,
    )

    assert identify_primary_driver(
        priority
    ) == "failure_breadth"


def test_build_failure_remediations_preserves_order():
    priorities = [
        FailurePriority(
            name="blur",
            score=0.80,
            level="critical",
            failure_rate=0.90,
            prediction_flip_rate=0.50,
            affected_fraction=0.60,
        ),
        FailurePriority(
            name="rotation",
            score=0.40,
            level="medium",
            failure_rate=0.20,
            prediction_flip_rate=0.80,
            affected_fraction=0.20,
        ),
    ]

    remediations = build_failure_remediations(
        priorities
    )

    assert len(remediations) == 2
    assert remediations[0].name == "blur"
    assert remediations[1].name == "rotation"

    assert (
        remediations[0].primary_driver
        == "failure_rate"
    )

    assert (
        remediations[1].primary_driver
        == "prediction_instability"
    )


def test_remediation_for_unknown_driver():
    with pytest.raises(
        ValueError,
        match="Unknown remediation driver",
    ):
        remediation_for_driver(
            "unknown"
        )