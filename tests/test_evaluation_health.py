from failurelab.evaluation_health import (
    EvaluationHealth,
    classify_evaluation_health,
)
from failurelab.evaluation_summary import (
    EvaluationSummary,
)


def make_summary(
    total,
    failed,
):
    return EvaluationSummary(
        total_analyses=total,
        passed_analyses=total - failed,
        failed_analyses=failed,
        failed_analysis_names=tuple(
            f"analysis-{index}"
            for index in range(failed)
        ),
        status=(
            "passed"
            if failed == 0
            else "failed"
        ),
    )


def test_health_is_healthy_when_all_pass():
    health = classify_evaluation_health(
        make_summary(
            6,
            0,
        )
    )

    assert isinstance(
        health,
        EvaluationHealth,
    )

    assert health.status == "healthy"
    assert health.failure_ratio == 0.0
    assert health.failed_analyses == 0


def test_health_is_watch_for_limited_failures():
    health = classify_evaluation_health(
        make_summary(
            6,
            1,
        )
    )

    assert health.status == "watch"
    assert health.failed_analyses == 1


def test_health_is_at_risk_for_multiple_failures():
    health = classify_evaluation_health(
        make_summary(
            6,
            3,
        )
    )

    assert health.status == "at-risk"
    assert health.failure_ratio == 0.5


def test_health_is_critical_when_most_fail():
    health = classify_evaluation_health(
        make_summary(
            6,
            4,
        )
    )

    assert health.status == "critical"
    assert health.failed_analyses == 4