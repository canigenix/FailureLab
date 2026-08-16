from __future__ import annotations

from dataclasses import dataclass, field

from failurelab.suite_runner import SuiteResult


@dataclass(frozen=True)
class StressPolicy:
    maximum_top1_drop: float | None = None
    maximum_top5_drop: float | None = None
    maximum_confidence_drop: float | None = None


@dataclass(frozen=True)
class RobustnessPolicy:
    maximum_top1_drop: float | None = None
    maximum_top5_drop: float | None = None
    maximum_confidence_drop: float | None = None
    stresses: dict[str, StressPolicy] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PolicyViolation:
    stress_name: str
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class PolicyEvaluation:
    violations: list[PolicyViolation]

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"


def _check_limit(
    violations: list[PolicyViolation],
    stress_name: str,
    metric: str,
    observed: float,
    allowed: float | None,
) -> None:
    if allowed is None:
        return

    if allowed < 0:
        raise ValueError(
            f"{metric} limit cannot be negative."
        )

    if observed > allowed:
        violations.append(
            PolicyViolation(
                stress_name=stress_name,
                metric=metric,
                observed=observed,
                allowed=allowed,
            )
        )


def evaluate_policy(
    result: SuiteResult,
    policy: RobustnessPolicy,
) -> PolicyEvaluation:
    violations: list[PolicyViolation] = []

    for stress_result in result.results:
        stress_name = stress_result.name

        _check_limit(
            violations,
            stress_name,
            "top1_drop",
            stress_result.top1_drop,
            policy.maximum_top1_drop,
        )

        _check_limit(
            violations,
            stress_name,
            "top5_drop",
            stress_result.top5_drop,
            policy.maximum_top5_drop,
        )

        _check_limit(
            violations,
            stress_name,
            "confidence_drop",
            stress_result.target_confidence_drop,
            policy.maximum_confidence_drop,
        )

        base_name = stress_name.split("_")[0]

        stress_policy = policy.stresses.get(
            base_name
        )

        if stress_policy is None:
            continue

        _check_limit(
            violations,
            stress_name,
            "top1_drop",
            stress_result.top1_drop,
            stress_policy.maximum_top1_drop,
        )

        _check_limit(
            violations,
            stress_name,
            "top5_drop",
            stress_result.top5_drop,
            stress_policy.maximum_top5_drop,
        )

        _check_limit(
            violations,
            stress_name,
            "confidence_drop",
            stress_result.target_confidence_drop,
            stress_policy.maximum_confidence_drop,
        )

    return PolicyEvaluation(
        violations=violations
    )