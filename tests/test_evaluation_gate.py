import pytest

from failurelab.evaluation_gate import (
    EvaluationGateResult,
    evaluate_intelligence_gate,
)
from failurelab.evaluation_health import (
    EvaluationHealth,
)
from failurelab.evaluation_intelligence import (
    EvaluationIntelligence,
)
from failurelab.evaluation_summary import (
    EvaluationSummary,
)


def make_intelligence(
    *,
    total=6,
    failed=0,
    health="healthy",
):
    return EvaluationIntelligence(
        summary=EvaluationSummary(
            total_analyses=total,
            passed_analyses=(
                total - failed
            ),
            failed_analyses=failed,
            failed_analysis_names=tuple(
                f"analysis-{index}"
                for index in range(
                    failed
                )
            ),
            status=(
                "passed"
                if failed == 0
                else "failed"
            ),
        ),
        health=EvaluationHealth(
            status=health,
            failure_ratio=(
                failed / total
            ),
            failed_analyses=failed,
            message="test",
        ),
    )


def test_gate_passes_healthy_evaluation():
    result = evaluate_intelligence_gate(
        make_intelligence()
    )

    assert isinstance(
        result,
        EvaluationGateResult,
    )

    assert result.passed is True
    assert result.status == "passed"
    assert result.violations == ()


def test_gate_rejects_failed_analysis_count():
    result = evaluate_intelligence_gate(
        make_intelligence(
            failed=2,
            health="at-risk",
        ),
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
            "watch",
            "at-risk",
        ),
    )

    assert result.passed is False

    assert (
        "Failed analyses 2 exceed maximum 1."
        in result.violations
    )


def test_gate_rejects_health_status():
    result = evaluate_intelligence_gate(
        make_intelligence(
            failed=1,
            health="watch",
        ),
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
        ),
    )

    assert result.passed is False

    assert (
        "Health status 'watch' is not allowed."
        in result.violations
    )


def test_gate_can_allow_watch():
    result = evaluate_intelligence_gate(
        make_intelligence(
            failed=1,
            health="watch",
        ),
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
            "watch",
        ),
    )

    assert result.passed is True


def test_gate_rejects_negative_maximum():
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        evaluate_intelligence_gate(
            make_intelligence(),
            maximum_failed_analyses=-1,
        )


def test_gate_requires_allowed_health_status():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        evaluate_intelligence_gate(
            make_intelligence(),
            allowed_health_statuses=(),
        )