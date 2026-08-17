from __future__ import annotations

from dataclasses import dataclass

from failurelab.class_analysis import ClassRobustnessResult


@dataclass(frozen=True)
class ClassPolicy:
    maximum_accuracy_drop: float | None = None
    maximum_confidence_drop: float | None = None
    maximum_failure_rate: float | None = None
    maximum_flip_rate: float | None = None
    minimum_samples: int = 1


@dataclass(frozen=True)
class ClassPolicyViolation:
    class_index: int
    metric: str
    observed: float
    allowed: float
    sample_count: int


@dataclass(frozen=True)
class ClassPolicyEvaluation:
    violations: list[ClassPolicyViolation]
    evaluated_classes: int
    skipped_classes: int

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def status(self) -> str:
        return "passed" if self.passed else "failed"


def _validate_policy(
    policy: ClassPolicy,
) -> None:
    if policy.minimum_samples < 1:
        raise ValueError(
            "minimum_samples must be at least 1."
        )


def _check_limit(
    violations: list[ClassPolicyViolation],
    class_index: int,
    sample_count: int,
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
                sample_count=sample_count,
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

    _validate_policy(
        default_policy
    )

    for policy in class_policies.values():
        _validate_policy(
            policy
        )

    violations: list[ClassPolicyViolation] = []

    evaluated_classes = 0
    skipped_classes = 0

    for result in results:
        specific_policy = class_policies.get(
            result.class_index
        )

        effective_minimum = (
            specific_policy.minimum_samples
            if specific_policy is not None
            else default_policy.minimum_samples
        )

        if result.sample_count < effective_minimum:
            skipped_classes += 1
            continue

        evaluated_classes += 1

        policies = [
            default_policy,
        ]

        if specific_policy is not None:
            policies.append(
                specific_policy
            )

        for policy in policies:
            _check_limit(
                violations,
                result.class_index,
                result.sample_count,
                "accuracy_drop",
                result.accuracy_drop,
                policy.maximum_accuracy_drop,
            )

            _check_limit(
                violations,
                result.class_index,
                result.sample_count,
                "confidence_drop",
                result.confidence_drop,
                policy.maximum_confidence_drop,
            )

            _check_limit(
                violations,
                result.class_index,
                result.sample_count,
                "stressed_failure_rate",
                result.stressed_failure_rate,
                policy.maximum_failure_rate,
            )

            _check_limit(
                violations,
                result.class_index,
                result.sample_count,
                "prediction_flip_rate",
                result.prediction_flip_rate,
                policy.maximum_flip_rate,
            )

    return ClassPolicyEvaluation(
        violations=violations,
        evaluated_classes=evaluated_classes,
        skipped_classes=skipped_classes,
    )