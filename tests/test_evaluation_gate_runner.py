from failurelab.evaluation_gate import (
    EvaluationGateResult,
)
from failurelab.evaluation_gate_config import (
    EvaluationGateConfig,
)
from failurelab.evaluation_gate_runner import (
    run_evaluation_gate,
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


def test_runner_passes_healthy_evaluation():
    config = EvaluationGateConfig()

    result = run_evaluation_gate(
        make_intelligence(),
        config,
    )

    assert isinstance(
        result,
        EvaluationGateResult,
    )

    assert result.passed is True
    assert result.status == "passed"
    assert result.violations == ()


def test_runner_applies_failed_analysis_limit():
    config = EvaluationGateConfig(
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
            "watch",
            "at-risk",
        ),
    )

    result = run_evaluation_gate(
        make_intelligence(
            failed=2,
            health="at-risk",
        ),
        config,
    )

    assert result.passed is False

    assert (
        "Failed analyses 2 exceed maximum 1."
        in result.violations
    )


def test_runner_applies_health_policy():
    config = EvaluationGateConfig(
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
        ),
    )

    result = run_evaluation_gate(
        make_intelligence(
            failed=1,
            health="watch",
        ),
        config,
    )

    assert result.passed is False

    assert (
        "Health status 'watch' is not allowed."
        in result.violations
    )


def test_runner_allows_configured_degradation():
    config = EvaluationGateConfig(
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
            "watch",
        ),
    )

    result = run_evaluation_gate(
        make_intelligence(
            failed=1,
            health="watch",
        ),
        config,
    )

    assert result.passed is True
    assert result.violations == ()