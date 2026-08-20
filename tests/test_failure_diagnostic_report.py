from failurelab.failure_diagnostic_report import (
    FailureDiagnosticReport,
    build_failure_diagnostic_report,
)
from failurelab.failure_signature import (
    StressFailureSignal,
    build_failure_signature,
)


def test_build_failure_diagnostic_report():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.25, 0.05),
            StressFailureSignal("rotation", 0.02, 0.01),
            StressFailureSignal("crop", 0.01, 0.01),
        ]
    )

    report = build_failure_diagnostic_report(signature)

    assert isinstance(report, FailureDiagnosticReport)
    assert report.signature == signature
    assert report.diagnosis is not None


def test_failure_diagnostic_report_summary():
    signature = build_failure_signature(
        [
            StressFailureSignal("blur", 0.20, 0.05),
            StressFailureSignal("rotation", 0.18, 0.04),
            StressFailureSignal("crop", 0.15, 0.03),
        ]
    )

    report = build_failure_diagnostic_report(signature)

    summary = report.summary()

    assert "systemic" in summary
    assert "systemic robustness degradation" in summary