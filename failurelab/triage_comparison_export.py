import json
from pathlib import Path

from failurelab.triage_comparison import (
    FailureTriageComparison,
)
from failurelab.triage_comparison_policy import (
    TriageComparisonPolicyResult,
)


def triage_comparison_to_dict(
    comparison: FailureTriageComparison,
) -> dict:
    """Convert a triage comparison into a JSON-safe dictionary."""

    return {
        "baseline_actionable": comparison.baseline_actionable,
        "candidate_actionable": comparison.candidate_actionable,
        "actionable_delta": comparison.actionable_delta,
        "baseline_critical": comparison.baseline_critical,
        "candidate_critical": comparison.candidate_critical,
        "critical_delta": comparison.critical_delta,
        "baseline_highest_score": (
            comparison.baseline_highest_score
        ),
        "candidate_highest_score": (
            comparison.candidate_highest_score
        ),
        "highest_score_delta": (
            comparison.highest_score_delta
        ),
        "status": comparison.status,
    }


def export_triage_comparison_json(
    comparison: FailureTriageComparison,
    path,
    *,
    policy: TriageComparisonPolicyResult | None = None,
) -> Path:
    """Export triage comparison analysis as JSON."""

    output_path = Path(path)

    data = triage_comparison_to_dict(
        comparison
    )

    if policy is not None:
        data["policy"] = {
            "passed": policy.passed,
            "violations": list(
                policy.violations
            ),
        }

    output_path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path