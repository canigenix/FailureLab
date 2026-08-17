from __future__ import annotations

from dataclasses import dataclass, field

from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class StressPolicy:
    maximum_top1_drop: float | None = None
    maximum_top5_drop: float | None = None
    maximum_confidence_drop: float | None = None

    warning_top1_drop: float | None = None
    warning_top5_drop: float | None = None
    warning_confidence_drop: float | None = None


@dataclass(frozen=True)
class RobustnessPolicy:
    maximum_top1_drop: float | None = None
    maximum_top5_drop: float | None = None
    maximum_confidence_drop: float | None = None

    warning_top1_drop: float | None = None
    warning_top5_drop: float | None = None
    warning_confidence_drop: float | None = None

    stresses: dict[str, StressPolicy] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PolicyViolation:
    stress_name: str
    metric: str
    observed: float
    allowed: float
    severity: str = "failure"


@dataclass(frozen=True)
class PolicyEvaluation:
    violations: list[PolicyViolation]
    warnings: list[PolicyViolation] = field(
        default_factory=list
    )

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def status(self) -> str:
        if self.violations:
            return "failed"

        if self.warnings:
            return "warning"

        return "passed"


def _validate_limit(
    value: float | None,
    name: str,
) -> None:
    if value is not None and value < 0:
        raise ValueError(
            f"{name} limit cannot be negative."
        )


def _check_metric(
    violations: list[PolicyViolation],
    warnings: list[PolicyViolation],
    stress_name: str,
    metric: str,
    observed: float,
    maximum: float | None,
    warning: float | None,
) -> None:
    _validate_limit(
        maximum,
        metric,
    )

    _validate_limit(
        warning,
        f"{metric} warning",
    )

    if (
        maximum is not None
        and warning is not None
        and warning > maximum
    ):
        raise ValueError(
            f"{metric} warning threshold cannot "
            "exceed its maximum threshold."
        )

    if (
        maximum is not None
        and observed > maximum
    ):
        violations.append(
            PolicyViolation(
                stress_name=stress_name,
                metric=metric,
                observed=observed,
                allowed=maximum,
                severity="failure",
            )
        )

        return

    if (
        warning is not None
        and observed > warning
    ):
        warnings.append(
            PolicyViolation(
                stress_name=stress_name,
                metric=metric,
                observed=observed,
                allowed=warning,
                severity="warning",
            )
        )


def _evaluate_single_policy(
    violations: list[PolicyViolation],
    warnings: list[PolicyViolation],
    stress_name: str,
    result,
    policy,
) -> None:
    _check_metric(
        violations,
        warnings,
        stress_name,
        "top1_drop",
        result.top1_drop,
        policy.maximum_top1_drop,
        policy.warning_top1_drop,
    )

    _check_metric(
        violations,
        warnings,
        stress_name,
        "top5_drop",
        result.top5_drop,
        policy.maximum_top5_drop,
        policy.warning_top5_drop,
    )

    _check_metric(
        violations,
        warnings,
        stress_name,
        "confidence_drop",
        result.target_confidence_drop,
        policy.maximum_confidence_drop,
        policy.warning_confidence_drop,
    )


def evaluate_policy(
    result: SuiteResult,
    policy: RobustnessPolicy,
) -> PolicyEvaluation:
    violations: list[PolicyViolation] = []
    warnings: list[PolicyViolation] = []

    for stress_result in result.results:
        stress_name = stress_result.name

        _evaluate_single_policy(
            violations,
            warnings,
            stress_name,
            stress_result,
            policy,
        )

        base_name = stress_name.split("_")[0]

        stress_policy = policy.stresses.get(
            base_name
        )

        if stress_policy is None:
            continue

        _evaluate_single_policy(
            violations,
            warnings,
            stress_name,
            stress_result,
            stress_policy,
        )

    return PolicyEvaluation(
        violations=violations,
        warnings=warnings,
    )