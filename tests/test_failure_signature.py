import pytest

from failurelab.failure_signature import (
    FailureSignature,
    StressFailureSignal,
    build_failure_signature,
    classify_failure_signature,
)


def test_build_failure_signature():
    signals = [
        StressFailureSignal(
            "blur",
            failure_rate=0.30,
            prediction_flip_rate=0.10,
        ),
        StressFailureSignal(
            "compression",
            failure_rate=0.10,
            prediction_flip_rate=0.05,
        ),
        StressFailureSignal(
            "rotation",
            failure_rate=0.05,
            prediction_flip_rate=0.02,
        ),
    ]

    signature = build_failure_signature(signals)

    assert isinstance(signature, FailureSignature)
    assert signature.dominant_stress == "blur"
    assert signature.dominant_failure_rate == pytest.approx(0.30)
    assert signature.mean_failure_rate == pytest.approx(0.15)
    assert signature.affected_stresses == (
        "blur",
        "compression",
    )
    assert signature.signature_type == "systemic"


def test_classify_failure_signature_localized():
    signals = [
        StressFailureSignal("blur", 0.25, 0.05),
        StressFailureSignal("rotation", 0.02, 0.01),
        StressFailureSignal("crop", 0.01, 0.01),
    ]

    assert (
        classify_failure_signature(signals)
        == "localized"
    )


def test_classify_failure_signature_systemic():
    signals = [
        StressFailureSignal("blur", 0.20, 0.05),
        StressFailureSignal("compression", 0.18, 0.04),
        StressFailureSignal("rotation", 0.15, 0.03),
    ]

    assert (
        classify_failure_signature(signals)
        == "systemic"
    )


def test_classify_failure_signature_unstable():
    signals = [
        StressFailureSignal("blur", 0.05, 0.30),
        StressFailureSignal("rotation", 0.04, 0.25),
    ]

    assert (
        classify_failure_signature(signals)
        == "unstable"
    )


def test_classify_failure_signature_low_risk():
    signals = [
        StressFailureSignal("blur", 0.04, 0.02),
        StressFailureSignal("rotation", 0.03, 0.01),
    ]

    assert (
        classify_failure_signature(signals)
        == "low-risk"
    )


def test_build_failure_signature_respects_threshold():
    signals = [
        StressFailureSignal("blur", 0.20, 0.05),
        StressFailureSignal("rotation", 0.12, 0.04),
    ]

    signature = build_failure_signature(
        signals,
        affected_threshold=0.15,
    )

    assert signature.affected_stresses == ("blur",)


def test_build_failure_signature_requires_signals():
    with pytest.raises(
        ValueError,
        match="At least one stress failure signal",
    ):
        build_failure_signature([])


def test_build_failure_signature_rejects_negative_threshold():
    signals = [
        StressFailureSignal("blur", 0.20, 0.10),
    ]

    with pytest.raises(
        ValueError,
        match="affected_threshold",
    ):
        build_failure_signature(
            signals,
            affected_threshold=-0.01,
        )


def test_build_failure_signature_rejects_invalid_systemic_fraction():
    signals = [
        StressFailureSignal("blur", 0.20, 0.10),
    ]

    with pytest.raises(
        ValueError,
        match="systemic_fraction",
    ):
        build_failure_signature(
            signals,
            systemic_fraction=1.5,
        )


def test_build_failure_signature_rejects_negative_instability_threshold():
    signals = [
        StressFailureSignal("blur", 0.20, 0.10),
    ]

    with pytest.raises(
        ValueError,
        match="instability_threshold",
    ):
        build_failure_signature(
            signals,
            instability_threshold=-0.01,
        )