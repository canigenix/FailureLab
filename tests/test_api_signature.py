import pytest

from failurelab.api import FailureLab
from failurelab.failure_diagnostic_report import (
    FailureDiagnosticReport,
)
from failurelab.failure_signature import (
    FailureSignature,
)
from failurelab.signature_comparison import (
    FailureSignatureComparison,
)
from failurelab.signature_policy import (
    SignaturePolicyResult,
)


def test_failurelab_builds_failure_signature():
    signature = FailureLab.failure_signature(
        [
            ("blur", 0.25, 0.05),
            ("rotation", 0.02, 0.01),
            ("crop", 0.01, 0.01),
        ]
    )

    assert isinstance(signature, FailureSignature)
    assert signature.dominant_stress == "blur"
    assert signature.signature_type == "localized"


def test_failurelab_diagnoses_failure_signature():
    signature = FailureLab.failure_signature(
        [
            ("blur", 0.20, 0.05),
            ("rotation", 0.18, 0.04),
            ("crop", 0.15, 0.03),
        ]
    )

    report = FailureLab.diagnose_failure_signature(
        signature
    )

    assert isinstance(report, FailureDiagnosticReport)
    assert report.signature.signature_type == "systemic"
    assert "systemic robustness degradation" in report.summary()


def test_failurelab_compares_failure_signatures():
    baseline = FailureLab.failure_signature(
        [
            ("blur", 0.10, 0.03),
            ("rotation", 0.05, 0.02),
        ]
    )

    candidate = FailureLab.failure_signature(
        [
            ("blur", 0.25, 0.08),
            ("rotation", 0.15, 0.05),
        ]
    )

    comparison = FailureLab.compare_failure_signatures(
        baseline,
        candidate,
    )

    assert isinstance(
        comparison,
        FailureSignatureComparison,
    )

    assert comparison.status == "regressed"
    assert comparison.mean_failure_rate_delta > 0


def test_failurelab_signature_comparison_respects_tolerance():
    baseline = FailureLab.failure_signature(
        [
            ("blur", 0.10, 0.03),
            ("rotation", 0.05, 0.02),
        ]
    )

    candidate = FailureLab.failure_signature(
        [
            ("blur", 0.105, 0.032),
            ("rotation", 0.05, 0.02),
        ]
    )

    comparison = FailureLab.compare_failure_signatures(
        baseline,
        candidate,
        tolerance=0.01,
    )

    assert comparison.status == "stable"


def test_failurelab_signature_policy_passes():
    baseline = FailureLab.failure_signature(
        [
            ("blur", 0.30, 0.10),
            ("rotation", 0.20, 0.08),
        ]
    )

    candidate = FailureLab.failure_signature(
        [
            ("blur", 0.10, 0.03),
            ("rotation", 0.05, 0.02),
        ]
    )

    comparison = FailureLab.compare_failure_signatures(
        baseline,
        candidate,
    )

    result = FailureLab.signature_policy(
        comparison
    )

    assert isinstance(result, SignaturePolicyResult)
    assert result.passed is True
    assert result.violations == ()


def test_failurelab_signature_policy_fails():
    baseline = FailureLab.failure_signature(
        [
            ("blur", 0.04, 0.02),
            ("rotation", 0.03, 0.01),
        ]
    )

    candidate = FailureLab.failure_signature(
        [
            ("blur", 0.20, 0.05),
            ("rotation", 0.18, 0.04),
        ]
    )

    comparison = FailureLab.compare_failure_signatures(
        baseline,
        candidate,
    )

    result = FailureLab.signature_policy(
        comparison,
        max_failure_rate_increase=0.05,
        max_flip_rate_increase=0.05,
        max_affected_stress_increase=0,
        allow_severity_regression=False,
    )

    assert result.passed is False
    assert len(result.violations) >= 1


def test_failurelab_save_signature_json(tmp_path):
    signature = FailureLab.failure_signature(
        [
            ("blur", 0.25, 0.05),
            ("rotation", 0.02, 0.01),
            ("crop", 0.01, 0.01),
        ]
    )

    diagnostic_report = FailureLab.diagnose_failure_signature(
        signature
    )

    path = tmp_path / "signature.json"

    result = FailureLab.save_signature_json(
        signature,
        path,
        diagnostic_report=diagnostic_report,
    )

    assert result == path
    assert path.exists()

def test_failurelab_signature_history():
    v1 = FailureLab.failure_signature(
        [
            ("blur", 0.30, 0.10),
            ("rotation", 0.20, 0.08),
        ]
    )

    v2 = FailureLab.failure_signature(
        [
            ("blur", 0.20, 0.06),
            ("rotation", 0.10, 0.04),
        ]
    )

    v3 = FailureLab.failure_signature(
        [
            ("blur", 0.10, 0.03),
            ("rotation", 0.05, 0.02),
        ]
    )

    report = FailureLab.signature_history(
        [
            ("v1", v1),
            ("v2", v2),
            ("v3", v3),
        ]
    )

    assert report.trend == "improving"
    assert report.improved_transitions == 2
    assert report.regressed_transitions == 0


def test_failurelab_signature_history_policy():
    v1 = FailureLab.failure_signature(
        [
            ("blur", 0.03, 0.01),
            ("rotation", 0.02, 0.01),
        ]
    )

    v2 = FailureLab.failure_signature(
        [
            ("blur", 0.20, 0.05),
            ("rotation", 0.18, 0.04),
        ]
    )

    report = FailureLab.signature_history(
        [
            ("v1", v1),
            ("v2", v2),
        ]
    )

    result = FailureLab.signature_history_policy(
        report
    )

    assert result.passed is False
    assert len(result.violations) >= 1

def test_failurelab_save_signature_history_json(tmp_path):
    v1 = FailureLab.failure_signature(
        [
            ("blur", 0.20, 0.05),
            ("rotation", 0.10, 0.03),
        ]
    )

    v2 = FailureLab.failure_signature(
        [
            ("blur", 0.10, 0.03),
            ("rotation", 0.05, 0.02),
        ]
    )

    v3 = FailureLab.failure_signature(
        [
            ("blur", 0.25, 0.08),
            ("rotation", 0.15, 0.05),
        ]
    )

    report = FailureLab.signature_history(
        [
            ("v1", v1),
            ("v2", v2),
            ("v3", v3),
        ]
    )

    policy = FailureLab.signature_history_policy(
        report,
        max_regressed_transitions=10,
        max_severity_regressions=10,
        allow_volatile=False,
    )

    path = tmp_path / "signature-history.json"

    result = FailureLab.save_signature_history_json(
        report,
        path,
        policy=policy,
    )

    assert result == path
    assert path.exists()