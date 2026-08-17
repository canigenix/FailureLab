import numpy as np

from failurelab.class_analysis import (
    analyze_class_robustness,
)
from failurelab.class_policy import (
    ClassPolicy,
    evaluate_class_policy,
)


def build_results():
    baseline = np.array(
        [
            [0.90, 0.10],
            [0.80, 0.20],
            [0.10, 0.90],
            [0.20, 0.80],
        ]
    )

    stressed = np.array(
        [
            [0.40, 0.60],
            [0.70, 0.30],
            [0.60, 0.40],
            [0.25, 0.75],
        ]
    )

    targets = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    return analyze_class_robustness(
        baseline,
        stressed,
        targets,
    )


def test_class_policy_detects_global_violation():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=0.25,
        ),
    )

    assert not evaluation.passed
    assert evaluation.status == "failed"

    assert any(
        violation.metric
        == "stressed_failure_rate"
        for violation in evaluation.violations
    )


def test_class_policy_passes_when_within_limits():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_accuracy_drop=1.0,
            maximum_confidence_drop=1.0,
            maximum_failure_rate=1.0,
            maximum_flip_rate=1.0,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "passed"
    assert evaluation.violations == []


def test_class_policy_supports_class_specific_limits():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=1.0,
        ),
        class_policies={
            0: ClassPolicy(
                maximum_flip_rate=0.25,
            )
        },
    )

    assert not evaluation.passed

    assert any(
        violation.class_index == 0
        and violation.metric
        == "prediction_flip_rate"
        for violation in evaluation.violations
    )


def test_class_policy_skips_under_sampled_classes():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=0.01,
            minimum_samples=3,
        ),
    )

    assert evaluation.passed
    assert evaluation.evaluated_classes == 0
    assert evaluation.skipped_classes == 2
    assert evaluation.violations == []


def test_class_policy_evaluates_classes_with_enough_samples():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=0.01,
            minimum_samples=2,
        ),
    )

    assert not evaluation.passed
    assert evaluation.evaluated_classes == 2
    assert evaluation.skipped_classes == 0