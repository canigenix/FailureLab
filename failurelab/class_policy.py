from __future__ import annotations

from dataclasses import dataclass

from failurelab.class_analysis import ClassRobustnessResult


@dataclass(frozen=True)
class ClassPolicy:
    maximum_accuracy_drop: float | None = None
    maximum_confidence_drop: float | None = None
    maximum_failure_rate: float | None = None
    maximum_flip_rate: float | None = None


@dataclass(frozen=True)
class ClassPolicyViolation:
    class_index: int
    metric: str
    observed: float
    allowed: float


@dataclass(frozen=True)
class ClassPolicyEvaluation:
    violations: list[ClassPolicyViolation]

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"


def _check_limit(
    violations: list[ClassPolicyViolation],
    class_index: int,
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
            ClassPolicyViolation(
                class_index=class_index,
                metric=metric,
                observed=observed,
                allowed=allowed,
            )
        )


def evaluate_class_policy(
    results: list[ClassRobustnessResult],
    default_policy: ClassPolicy | None = None,
    class_policies: dict[int, ClassPolicy] | None = None,
) -> ClassPolicyEvaluation:
    if default_policy is None:
        default_policy = ClassPolicy()

    if class_policies is None:
        class_policies = {}

    violations: list[ClassPolicyViolation] = []

    for result in results:
        policies = [
            default_policy,
        ]

        specific_policy = class_policies.get(
            result.class_index
        )

        if specific_policy is not None:
            policies.append(
                specific_policy
            )

        for policy in policies:
            _check_limit(
                violations,
                result.class_index,
                "accuracy_drop",
                result.accuracy_drop,
                policy.maximum_accuracy_drop,
            )

            _check_limit(
                violations,
                result.class_index,
                "confidence_drop",
                result.confidence_drop,
                policy.maximum_confidence_drop,
            )

            _check_limit(
                violations,
                result.class_index,
                "stressed_failure_rate",
                result.stressed_failure_rate,
                policy.maximum_failure_rate,
            )

            _check_limit(
                violations,
                result.class_index,
                "prediction_flip_rate",
                result.prediction_flip_rate,
                policy.maximum_flip_rate,
            )

    return ClassPolicyEvaluation(
        violations=violations
    )