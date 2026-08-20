import pytest

from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_comparison import (
    FailureSignatureComparison,
    compare_failure_signatures,
)


def test_compare_failure_signatures():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.30, 0.10),
            StressFailureSignal("rotation", 0.15, 0.04),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert isinstance(
        comparison,
        FailureSignatureComparison,
    )

    assert comparison.baseline_dominant_stress == "blur"
    assert comparison.candidate_dominant_stress == "blur"
    assert comparison.dominant_stress_changed is False

    assert comparison.mean_failure_rate_delta == pytest.approx(
        0.10
    )

    assert comparison.mean_flip_rate_delta == pytest.approx(
        0.035
    )

    assert comparison.affected_stress_delta == 1


def test_compare_failure_signatures_detects_dominant_change():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.30, 0.05),
            StressFailureSignal("rotation", 0.10, 0.02),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.10, 0.04),
            StressFailureSignal("rotation", 0.35, 0.08),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert comparison.dominant_stress_changed is True
    assert comparison.baseline_dominant_stress == "blur"
    assert comparison.candidate_dominant_stress == "rotation"


def test_compare_failure_signatures_detects_improvement():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.30, 0.10),
            StressFailureSignal("rotation", 0.20, 0.08),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.15, 0.05),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert comparison.mean_failure_rate_delta < 0
    assert comparison.mean_flip_rate_delta < 0
    assert comparison.affected_stress_delta < 0


def test_compare_failure_signatures_tracks_type_change():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.04, 0.02),
            StressFailureSignal("rotation", 0.03, 0.01),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.18, 0.04),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert comparison.baseline_signature_type == "low-risk"
    assert comparison.candidate_signature_type == "systemic"


def test_signature_comparison_status_regressed():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.25, 0.08),
            StressFailureSignal("rotation", 0.15, 0.05),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert comparison.status == "regressed"


def test_signature_comparison_status_improved():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.30, 0.10),
            StressFailureSignal("rotation", 0.20, 0.08),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    assert comparison.status == "improved"


def test_signature_comparison_status_stable_with_tolerance():
    baseline = build_failure_signature(
        [
            StressFailureSignal("blur", 0.10, 0.03),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    candidate = build_failure_signature(
        [
            StressFailureSignal("blur", 0.105, 0.032),
            StressFailureSignal("rotation", 0.05, 0.02),
        ]
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
        tolerance=0.01,
    )

    assert comparison.status == "stable"