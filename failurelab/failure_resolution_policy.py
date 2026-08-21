from dataclasses import dataclass

from failurelab.failure_resolution_report import (
    FailureResolutionReport,
)


@dataclass(frozen=True)
class FailureResolutionPolicyResult:
    """Result of evaluating failure resolution policy."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_failure_resolution_policy(
    report: FailureResolutionReport,
    *,
    max_worsening: int | None = None,
    max_unchanged: int | None = None,
    max_unresolved: int | None = None,
    max_score_regression: float | None = None,
) -> FailureResolutionPolicyResult:
    """Evaluate failure resolution against policy limits."""

    for name, value in (
        ("max_worsening", max_worsening),
        ("max_unchanged", max_unchanged),
        ("max_unresolved", max_unresolved),
    ):
        if value is not None and value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    if (
        max_score_regression is not None
        and max_score_regression < 0.0
    ):
        raise ValueError(
            "max_score_regression cannot be negative."
        )

    violations = []

    if (
        max_worsening is not None
        and report.worsening_count > max_worsening
    ):
        violations.append(
            "Worsening failures exceeded limit: "
            f"{report.worsening_count} > {max_worsening}."
        )

    if (
        max_unchanged is not None
        and report.unchanged_count > max_unchanged
    ):
        violations.append(
            "Unchanged failures exceeded limit: "
            f"{report.unchanged_count} > {max_unchanged}."
        )

    if (
        max_unresolved is not None
        and report.unresolved_count > max_unresolved
    ):
        violations.append(
            "Unresolved failures exceeded limit: "
            f"{report.unresolved_count} > {max_unresolved}."
        )

    if (
        max_score_regression is not None
        and report.worst_resolution is not None
        and report.worst_resolution.score_delta
        > max_score_regression
    ):
        violations.append(
            "Failure score regression exceeded limit: "
            f"{report.worst_resolution.score_delta:.4f} > "
            f"{max_score_regression:.4f}."
        )

    return FailureResolutionPolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )