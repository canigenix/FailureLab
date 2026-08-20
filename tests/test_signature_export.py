import json

from failurelab.failure_diagnostic_report import (
    build_failure_diagnostic_report,
)
from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)
from failurelab.signature_comparison import (
    compare_failure_signatures,
)
from failurelab.signature_export import (
    diagnostic_report_to_dict,
    export_signature_json,
    failure_signature_to_dict,
    signature_comparison_to_dict,
)
from failurelab.signature_policy import (
    evaluate_signature_policy,
)


def build_signature():
    return build_failure_signature(
        [
            StressFailureSignal("blur", 0.25, 0.05),
            StressFailureSignal("rotation", 0.02, 0.01),
            StressFailureSignal("crop", 0.01, 0.01),
        ]
    )


def test_failure_signature_to_dict():
    signature = build_signature()

    data = failure_signature_to_dict(signature)

    assert data["dominant_stress"] == "blur"
    assert data["signature_type"] == "localized"
    assert data["affected_stresses"] == ["blur"]


def test_diagnostic_report_to_dict():
    signature = build_signature()

    report = build_failure_diagnostic_report(
        signature
    )

    data = diagnostic_report_to_dict(report)

    assert data["signature"]["dominant_stress"] == "blur"
    assert "localized robustness weakness" in (
        data["diagnosis"]["diagnosis"]
    )
    assert "summary" in data


def test_signature_comparison_to_dict():
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

    data = signature_comparison_to_dict(
        comparison
    )

    assert data["status"] == "regressed"
    assert data["mean_failure_rate_delta"] > 0


def test_export_signature_json(tmp_path):
    signature = build_signature()

    path = tmp_path / "signature.json"

    result = export_signature_json(
        signature,
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["signature"]["dominant_stress"] == "blur"


def test_export_signature_json_with_everything(
    tmp_path,
):
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

    diagnostic_report = (
        build_failure_diagnostic_report(
            candidate
        )
    )

    comparison = compare_failure_signatures(
        baseline,
        candidate,
    )

    policy = evaluate_signature_policy(
        comparison,
        max_failure_rate_increase=0.05,
        max_flip_rate_increase=0.05,
        max_affected_stress_increase=0,
        allow_severity_regression=False,
    )

    path = tmp_path / "signature.json"

    export_signature_json(
        candidate,
        path,
        diagnostic_report=diagnostic_report,
        comparison=comparison,
        policy=policy,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["signature"]["signature_type"] == "systemic"
    assert "diagnostic_report" in data
    assert data["comparison"]["status"] == "regressed"
    assert data["policy"]["passed"] is False