from dataclasses import dataclass

from failurelab.failure_forecast_report import (
    FailureForecastReport,
)


@dataclass(frozen=True)
class FailureForecastPolicyResult:
    """Result of evaluating forecast policy limits."""

    passed: bool
    violations: tuple[str, ...]


def evaluate_failure_forecast_policy(
    report: FailureForecastReport,
    *,
    max_worsening: int | None = None,
    max_projected_risk: int | None = None,
    max_projected_score: float | None = None,
) -> FailureForecastPolicyResult:
    """Evaluate a failure forecast against policy limits."""

    for name, value in (
        ("max_worsening", max_worsening),
        ("max_projected_risk", max_projected_risk),
    ):
        if value is not None and value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    if (
        max_projected_score is not None
        and not 0.0 <= max_projected_score <= 1.0
    ):
        raise ValueError(
            "max_projected_score must be between 0 and 1."
        )

    violations = []

    if (
        max_worsening is not None
        and report.worsening_count > max_worsening
    ):
        violations.append(
            "Worsening forecasts exceeded limit: "
            f"{report.worsening_count} > {max_worsening}."
        )

    if (
        max_projected_risk is not None
        and report.projected_risk_count
        > max_projected_risk
    ):
        violations.append(
            "Projected-risk failures exceeded limit: "
            f"{report.projected_risk_count} > "
            f"{max_projected_risk}."
        )

    if (
        max_projected_score is not None
        and report.highest_projected_risk is not None
        and report.highest_projected_risk.projected_score
        > max_projected_score
    ):
        violations.append(
            "Projected failure score exceeded limit: "
            f"{report.highest_projected_risk.projected_score:.4f} "
            f"> {max_projected_score:.4f}."
        )

    return FailureForecastPolicyResult(
        passed=not violations,
        violations=tuple(violations),
    )