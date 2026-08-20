from dataclasses import dataclass

from failurelab.progression import ProgressionHistoryReport


@dataclass(frozen=True)
class ProgressionPolicyResult:
    """Result of evaluating a progression history against policy rules."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_progression_policy(
    report: ProgressionHistoryReport,
    *,
    max_overall_regression: float = 0.0,
    max_regressed_transitions: int = 0,
    allow_volatile: bool = True,
) -> ProgressionPolicyResult:
    """Evaluate a model progression report against CI-style policy rules."""

    if max_overall_regression < 0:
        raise ValueError(
            "max_overall_regression must be greater than or equal to 0."
        )

    if max_regressed_transitions < 0:
        raise ValueError(
            "max_regressed_transitions must be greater than or equal to 0."
        )

    violations = []

    if report.overall_delta > max_overall_regression:
        violations.append(
            "Overall failure-rate regression "
            f"{report.overall_delta:.4f} exceeds allowed "
            f"{max_overall_regression:.4f}."
        )

    if report.regressed_count > max_regressed_transitions:
        violations.append(
            "Regressed transitions "
            f"{report.regressed_count} exceed allowed "
            f"{max_regressed_transitions}."
        )

    if report.trend == "volatile" and not allow_volatile:
        violations.append(
            "Volatile progression histories are not allowed."
        )

    return ProgressionPolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )