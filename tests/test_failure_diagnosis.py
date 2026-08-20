from failurelab.failure_diagnosis import (
    FailureDiagnosis,
    diagnose_failure_signature,
)
from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)


def test_diagnose_low_risk_signature():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.03, 0.01),
            StressFailureSignal("rotation", 0.02, 0.01),
        ]
    )

    diagnosis = diagnose_failure_signature(signature)

    assert isinstance(diagnosis, FailureDiagnosis)
    assert "No broad failure pattern" in diagnosis.diagnosis


def test_diagnose_localized_signature():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.25, 0.05),
            StressFailureSignal("rotation", 0.02, 0.01),
            StressFailureSignal("crop", 0.01, 0.01),
        ]
    )

    diagnosis = diagnose_failure_signature(signature)

    assert "localized robustness weakness" in diagnosis.diagnosis
    assert "blur" in diagnosis.diagnosis
    assert "targeted evaluation" in diagnosis.recommended_action


def test_diagnose_systemic_signature():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.18, 0.04),
            StressFailureSignal("crop", 0.15, 0.03),
        ]
    )

    diagnosis = diagnose_failure_signature(signature)

    assert "systemic robustness degradation" in diagnosis.diagnosis
    assert "brittle visual features" in diagnosis.likely_cause


def test_diagnose_unstable_signature():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.05, 0.30),
            StressFailureSignal("rotation", 0.04, 0.25),
        ]
    )

    diagnosis = diagnose_failure_signature(signature)

    assert "prediction instability" in diagnosis.diagnosis
    assert "prediction flips" in diagnosis.recommended_action