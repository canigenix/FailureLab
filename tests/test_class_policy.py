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
    assert evaluation.warnings == []


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


def test_class_policy_calculates_coverage():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=1.0,
            minimum_samples=2,
        ),
    )

    assert evaluation.total_classes == 2
    assert evaluation.class_coverage == 1.0


def test_class_policy_fails_insufficient_coverage():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=1.0,
            minimum_samples=3,
        ),
        minimum_class_coverage=0.80,
    )

    assert evaluation.evaluated_classes == 0
    assert evaluation.skipped_classes == 2
    assert evaluation.class_coverage == 0.0
    assert not evaluation.coverage_passed
    assert not evaluation.passed
    assert evaluation.status == "failed"


def test_class_policy_accepts_sufficient_coverage():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            maximum_failure_rate=1.0,
            minimum_samples=2,
        ),
        minimum_class_coverage=0.80,
    )

    assert evaluation.class_coverage == 1.0
    assert evaluation.coverage_passed
    assert evaluation.passed


def test_class_policy_rejects_invalid_coverage():
    results = build_results()

    try:
        evaluate_class_policy(
            results,
            minimum_class_coverage=1.20,
        )
    except ValueError as exc:
        assert "between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid coverage threshold to fail."
        )


def test_class_policy_reports_warning_without_failure():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            warning_failure_rate=0.25,
            maximum_failure_rate=1.0,
        ),
    )

    assert evaluation.passed
    assert evaluation.status == "warning"
    assert evaluation.violations == []
    assert len(evaluation.warnings) >= 1

    assert (
        evaluation.warnings[0].severity
        == "warning"
    )


def test_class_policy_failure_takes_priority_over_warning():
    results = build_results()

    evaluation = evaluate_class_policy(
        results,
        default_policy=ClassPolicy(
            warning_failure_rate=0.10,
            maximum_failure_rate=0.25,
        ),
    )

    assert not evaluation.passed
    assert evaluation.status == "failed"
    assert len(evaluation.violations) >= 1


def test_class_policy_rejects_warning_above_maximum():
    results = build_results()

    try:
        evaluate_class_policy(
            results,
            default_policy=ClassPolicy(
                warning_failure_rate=0.50,
                maximum_failure_rate=0.25,
            ),
        )
    except ValueError as exc:
        assert (
            "warning threshold cannot exceed"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected invalid class warning threshold to fail."
        )