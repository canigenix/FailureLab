from __future__ import annotations

from dataclasses import dataclass, field

from failurelab.class_analysis import ClassRobustnessResult


@dataclass(frozen=True)
class ClassPolicy:
    maximum_accuracy_drop: float | None = None
    maximum_confidence_drop: float | None = None
    maximum_failure_rate: float | None = None
    maximum_flip_rate: float | None = None

    warning_accuracy_drop: float | None = None
    warning_confidence_drop: float | None = None
    warning_failure_rate: float | None = None
    warning_flip_rate: float | None = None

    minimum_samples: int = 1


@dataclass(frozen=True)
class ClassPolicyViolation:
    class_index: int
    metric: str
    observed: float
    allowed: float
    sample_count: int
    severity: str = "failure"


@dataclass(frozen=True)
class ClassPolicyEvaluation:
    violations: list[ClassPolicyViolation]
    evaluated_classes: int
    skipped_classes: int
    minimum_class_coverage: float | None = None
    warnings: list[ClassPolicyViolation] = field(
        default_factory=list
    )

    @property
    def total_classes(self) -> int:
        return (
            self.evaluated_classes
            + self.skipped_classes
        )

    @property
    def class_coverage(self) -> float:
        if self.total_classes == 0:
            return 0.0

        return (
            self.evaluated_classes
            / self.total_classes
        )

    @property
    def coverage_passed(self) -> bool:
        if self.minimum_class_coverage is None:
            return True

        return (
            self.class_coverage
            >= self.minimum_class_coverage
        )

    @property
    def passed(self) -> bool:
        return (
            not self.violations
            and self.coverage_passed
        )

    @property
    def status(self) -> str:
        if not self.passed:
            return "failed"

        if self.warnings:
            return "warning"

        return "passed"


def _validate_policy(
    policy: ClassPolicy,
) -> None:
    if policy.minimum_samples < 1:
        raise ValueError(
            "minimum_samples must be at least 1."
        )


def _validate_coverage(
    minimum_class_coverage: float | None,
) -> None:
    if minimum_class_coverage is None:
        return

    if not 0.0 <= minimum_class_coverage <= 1.0:
        raise ValueError(
            "minimum_class_coverage must be "
            "between 0.0 and 1.0."
        )


def _check_metric(
    violations: list[ClassPolicyViolation],
    warnings: list[ClassPolicyViolation],
    class_index: int,
    sample_count: int,
    metric: str,
    observed: float,
    maximum: float | None,
    warning: float | None,
) -> None:
    if maximum is not None and maximum < 0:
        raise ValueError(
            f"{metric} limit cannot be negative."
        )

    if warning is not None and warning < 0:
        raise ValueError(
            f"{metric} warning limit cannot be negative."
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
            ClassPolicyViolation(
                class_index=class_index,
                metric=metric,
                observed=observed,
                allowed=maximum,
                sample_count=sample_count,
                severity="failure",
            )
        )

        return

    if (
        warning is not None
        and observed > warning
    ):
        warnings.append(
            ClassPolicyViolation(
                class_index=class_index,
                metric=metric,
                observed=observed,
                allowed=warning,
                sample_count=sample_count,
                severity="warning",
            )
        )


def evaluate_class_policy(
    results: list[ClassRobustnessResult],
    default_policy: ClassPolicy | None = None,
    class_policies: dict[int, ClassPolicy] | None = None,
    minimum_class_coverage: float | None = None,
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

    _validate_coverage(
        minimum_class_coverage
    )

    violations: list[ClassPolicyViolation] = []
    warnings: list[ClassPolicyViolation] = []

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
            _check_metric(
                violations,
                warnings,
                result.class_index,
                result.sample_count,
                "accuracy_drop",
                result.accuracy_drop,
                policy.maximum_accuracy_drop,
                policy.warning_accuracy_drop,
            )

            _check_metric(
                violations,
                warnings,
                result.class_index,
                result.sample_count,
                "confidence_drop",
                result.confidence_drop,
                policy.maximum_confidence_drop,
                policy.warning_confidence_drop,
            )

            _check_metric(
                violations,
                warnings,
                result.class_index,
                result.sample_count,
                "stressed_failure_rate",
                result.stressed_failure_rate,
                policy.maximum_failure_rate,
                policy.warning_failure_rate,
            )

            _check_metric(
                violations,
                warnings,
                result.class_index,
                result.sample_count,
                "prediction_flip_rate",
                result.prediction_flip_rate,
                policy.maximum_flip_rate,
                policy.warning_flip_rate,
            )

    return ClassPolicyEvaluation(
        violations=violations,
        warnings=warnings,
        evaluated_classes=evaluated_classes,
        skipped_classes=skipped_classes,
        minimum_class_coverage=minimum_class_coverage,
    )