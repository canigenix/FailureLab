from dataclasses import dataclass

from failurelab.failure_diagnosis import (
    FailureDiagnosis,
    diagnose_failure_signature,
)
from failurelab.failure_signature import FailureSignature


@dataclass(frozen=True)
class FailureDiagnosticReport:
    """Combined failure signature and diagnosis."""

    signature: FailureSignature
    diagnosis: FailureDiagnosis

    def summary(self) -> str:
        return (
            f"{self.signature.signature_type}: "
            f"{self.diagnosis.diagnosis}"
        )


def build_failure_diagnostic_report(
    signature: FailureSignature,
) -> FailureDiagnosticReport:
    """Build a diagnostic report from a failure signature."""

    return FailureDiagnosticReport(
        signature=signature,
        diagnosis=diagnose_failure_signature(signature),
    )