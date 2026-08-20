import json
from pathlib import Path

from failurelab.failure_diagnostic_report import (
    FailureDiagnosticReport,
)
from failurelab.failure_signature import FailureSignature
from failurelab.signature_comparison import (
    FailureSignatureComparison,
)
from failurelab.signature_policy import (
    SignaturePolicyResult,
)


def failure_signature_to_dict(
    signature: FailureSignature,
) -> dict:
    return {
        "dominant_stress": signature.dominant_stress,
        "dominant_failure_rate": signature.dominant_failure_rate,
        "mean_failure_rate": signature.mean_failure_rate,
        "mean_flip_rate": signature.mean_flip_rate,
        "affected_stresses": list(
            signature.affected_stresses
        ),
        "signature_type": signature.signature_type,
    }


def diagnostic_report_to_dict(
    report: FailureDiagnosticReport,
) -> dict:
    return {
        "signature": failure_signature_to_dict(
            report.signature
        ),
        "diagnosis": {
            "diagnosis": report.diagnosis.diagnosis,
            "likely_cause": report.diagnosis.likely_cause,
            "recommended_action": (
                report.diagnosis.recommended_action
            ),
        },
        "summary": report.summary(),
    }


def signature_comparison_to_dict(
    comparison: FailureSignatureComparison,
) -> dict:
    return {
        "baseline_dominant_stress": (
            comparison.baseline_dominant_stress
        ),
        "candidate_dominant_stress": (
            comparison.candidate_dominant_stress
        ),
        "dominant_stress_changed": (
            comparison.dominant_stress_changed
        ),
        "mean_failure_rate_delta": (
            comparison.mean_failure_rate_delta
        ),
        "mean_flip_rate_delta": (
            comparison.mean_flip_rate_delta
        ),
        "affected_stress_delta": (
            comparison.affected_stress_delta
        ),
        "baseline_signature_type": (
            comparison.baseline_signature_type
        ),
        "candidate_signature_type": (
            comparison.candidate_signature_type
        ),
        "status": comparison.status,
    }


def export_signature_json(
    signature: FailureSignature,
    path,
    *,
    diagnostic_report: FailureDiagnosticReport | None = None,
    comparison: FailureSignatureComparison | None = None,
    policy: SignaturePolicyResult | None = None,
) -> Path:
    output_path = Path(path)

    data = {
        "signature": failure_signature_to_dict(
            signature
        ),
    }

    if diagnostic_report is not None:
        data["diagnostic_report"] = diagnostic_report_to_dict(
            diagnostic_report
        )

    if comparison is not None:
        data["comparison"] = signature_comparison_to_dict(
            comparison
        )

    if policy is not None:
        data["policy"] = {
            "passed": policy.passed,
            "violations": list(policy.violations),
        }

    output_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    return output_path