from failurelab.failure_envelope import (
    FailureBoundary,
    FailureEnvelope,
)


def test_failure_boundary_tracks_threshold():
    boundary = FailureBoundary(
        stress_name="blur",
        failure_threshold=3.0,
        worst_top1_drop=0.538,
    )

    assert boundary.threshold_reached is True
    assert boundary.failure_threshold == 3.0


def test_failure_boundary_can_remain_unreached():
    boundary = FailureBoundary(
        stress_name="rotation",
        failure_threshold=None,
        worst_top1_drop=0.156,
    )

    assert boundary.threshold_reached is False


def test_failure_envelope_gets_boundary():
    envelope = FailureEnvelope(
        boundaries=[
            FailureBoundary(
                stress_name="blur",
                failure_threshold=3.0,
                worst_top1_drop=0.538,
            ),
            FailureBoundary(
                stress_name="occlusion",
                failure_threshold=0.30,
                worst_top1_drop=0.702,
            ),
        ]
    )

    boundary = envelope.get(
        "Occlusion"
    )

    assert boundary.failure_threshold == 0.30