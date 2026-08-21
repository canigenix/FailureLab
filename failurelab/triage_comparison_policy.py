from dataclasses import dataclass

from failurelab.triage_comparison import (
    FailureTriageComparison,
)


@dataclass(frozen=True)
class TriageComparisonPolicyResult:
    """Result of evaluating triage comparison policy."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_triage_comparison_policy(
    comparison: FailureTriageComparison,
    *,
    allow_regression: bool = False,
    max_actionable_increase: int | None = None,
    max_critical_increase: int | None = None,
    max_score_increase: float | None = None,
) -> TriageComparisonPolicyResult:
    """Evaluate triage changes against regression limits."""

    if (
        max_actionable_increase is not None
        and max_actionable_increase < 0
    ):
        raise ValueError(
            "max_actionable_increase cannot be negative."
        )

    if (
        max_critical_increase is not None
        and max_critical_increase < 0
    ):
        raise ValueError(
            "max_critical_increase cannot be negative."
        )

    if (
        max_score_increase is not None
        and max_score_increase < 0.0
    ):
        raise ValueError(
            "max_score_increase cannot be negative."
        )

    violations = []

    if (
        comparison.status == "regressed"
        and not allow_regression
    ):
        violations.append(
            "Failure triage regressed."
        )

    if (
        max_actionable_increase is not None
        and comparison.actionable_delta
        > max_actionable_increase
    ):
        violations.append(
            "Actionable failure increase exceeded limit: "
            f"{comparison.actionable_delta} > "
            f"{max_actionable_increase}."
        )

    if (
        max_critical_increase is not None
        and comparison.critical_delta
        > max_critical_increase
    ):
        violations.append(
            "Critical failure increase exceeded limit: "
            f"{comparison.critical_delta} > "
            f"{max_critical_increase}."
        )

    if (
        max_score_increase is not None
        and comparison.highest_score_delta
        > max_score_increase
    ):
        violations.append(
            "Priority score increase exceeded limit: "
            f"{comparison.highest_score_delta:.4f} > "
            f"{max_score_increase:.4f}."
        )

    return TriageComparisonPolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )