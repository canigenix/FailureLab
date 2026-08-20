import json
from pathlib import Path

from failurelab.signature_history import SignatureHistoryReport
from failurelab.signature_history_policy import (
    SignatureHistoryPolicyResult,
)


def signature_history_to_dict(
    report: SignatureHistoryReport,
) -> dict:
    """Convert a signature history report into a JSON-safe dictionary."""

    return {
        "checkpoints": [
            {
                "label": checkpoint.label,
                "signature_type": checkpoint.signature.signature_type,
                "dominant_stress": checkpoint.signature.dominant_stress,
                "dominant_failure_rate": (
                    checkpoint.signature.dominant_failure_rate
                ),
                "mean_failure_rate": (
                    checkpoint.signature.mean_failure_rate
                ),
                "mean_flip_rate": (
                    checkpoint.signature.mean_flip_rate
                ),
                "affected_stresses": list(
                    checkpoint.signature.affected_stresses
                ),
            }
            for checkpoint in report.checkpoints
        ],
        "transitions": [
            {
                "baseline_dominant_stress": (
                    transition.baseline_dominant_stress
                ),
                "candidate_dominant_stress": (
                    transition.candidate_dominant_stress
                ),
                "dominant_stress_changed": (
                    transition.dominant_stress_changed
                ),
                "mean_failure_rate_delta": (
                    transition.mean_failure_rate_delta
                ),
                "mean_flip_rate_delta": (
                    transition.mean_flip_rate_delta
                ),
                "affected_stress_delta": (
                    transition.affected_stress_delta
                ),
                "baseline_signature_type": (
                    transition.baseline_signature_type
                ),
                "candidate_signature_type": (
                    transition.candidate_signature_type
                ),
                "status": transition.status,
            }
            for transition in report.transitions
        ],
        "dominant_stress_changes": report.dominant_stress_changes,
        "severity_regressions": report.severity_regressions,
        "improved_transitions": report.improved_transitions,
        "stable_transitions": report.stable_transitions,
        "regressed_transitions": report.regressed_transitions,
        "trend": report.trend,
    }


def export_signature_history_json(
    report: SignatureHistoryReport,
    path,
    *,
    policy: SignatureHistoryPolicyResult | None = None,
) -> Path:
    """Export signature-history analysis as JSON."""

    output_path = Path(path)

    data = signature_history_to_dict(report)

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