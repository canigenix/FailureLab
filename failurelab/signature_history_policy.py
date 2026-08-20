from dataclasses import dataclass

from failurelab.signature_history import (
    SignatureHistoryReport,
)


@dataclass(frozen=True)
class SignatureHistoryPolicyResult:
    """Result of evaluating signature history against policy rules."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_signature_history_policy(
    report: SignatureHistoryReport,
    *,
    max_regressed_transitions: int = 0,
    max_severity_regressions: int = 0,
    max_dominant_stress_changes: int | None = None,
    allow_volatile: bool = False,
) -> SignatureHistoryPolicyResult:
    """Evaluate failure-signature history against policy limits."""

    if max_regressed_transitions < 0:
        raise ValueError(
            "max_regressed_transitions cannot be negative."
        )

    if max_severity_regressions < 0:
        raise ValueError(
            "max_severity_regressions cannot be negative."
        )

    if (
        max_dominant_stress_changes is not None
        and max_dominant_stress_changes < 0
    ):
        raise ValueError(
            "max_dominant_stress_changes cannot be negative."
        )

    violations = []

    if (
        report.regressed_transitions
        > max_regressed_transitions
    ):
        violations.append(
            "Regressed signature transitions exceeded limit: "
            f"{report.regressed_transitions} > "
            f"{max_regressed_transitions}."
        )

    if (
        report.severity_regressions
        > max_severity_regressions
    ):
        violations.append(
            "Signature severity regressions exceeded limit: "
            f"{report.severity_regressions} > "
            f"{max_severity_regressions}."
        )

    if (
        max_dominant_stress_changes is not None
        and report.dominant_stress_changes
        > max_dominant_stress_changes
    ):
        violations.append(
            "Dominant stress changes exceeded limit: "
            f"{report.dominant_stress_changes} > "
            f"{max_dominant_stress_changes}."
        )

    if (
        report.trend == "volatile"
        and not allow_volatile
    ):
        violations.append(
            "Signature history trend is volatile."
        )

    return SignatureHistoryPolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )