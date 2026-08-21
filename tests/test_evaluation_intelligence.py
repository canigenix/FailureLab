from failurelab.evaluation_intelligence import (
    EvaluationIntelligence,
    build_evaluation_intelligence,
)
from failurelab.evaluation_report import (
    EvaluationStepResult,
)


def make_step(
    analysis,
    passed,
):
    return EvaluationStepResult(
        analysis=analysis,
        passed=passed,
        message=f"{analysis} result.",
    )


def test_build_healthy_intelligence():
    intelligence = build_evaluation_intelligence(
        [
            make_step(
                "progression",
                True,
            ),
            make_step(
                "signature",
                True,
            ),
            make_step(
                "triage",
                True,
            ),
        ]
    )

    assert isinstance(
        intelligence,
        EvaluationIntelligence,
    )

    assert (
        intelligence.summary.total_analyses
        == 3
    )

    assert (
        intelligence.summary.failed_analyses
        == 0
    )

    assert (
        intelligence.health.status
        == "healthy"
    )


def test_build_watch_intelligence():
    intelligence = build_evaluation_intelligence(
        [
            make_step(
                "progression",
                False,
            ),
            make_step(
                "signature",
                True,
            ),
            make_step(
                "triage",
                True,
            ),
            make_step(
                "forecast",
                True,
            ),
        ]
    )

    assert (
        intelligence.summary.failed_analysis_names
        == (
            "progression",
        )
    )

    assert (
        intelligence.health.status
        == "watch"
    )


def test_build_at_risk_intelligence():
    intelligence = build_evaluation_intelligence(
        [
            make_step(
                "progression",
                False,
            ),
            make_step(
                "signature",
                True,
            ),
            make_step(
                "triage",
                False,
            ),
            make_step(
                "forecast",
                True,
            ),
        ]
    )

    assert (
        intelligence.summary.failed_analyses
        == 2
    )

    assert (
        intelligence.health.status
        == "at-risk"
    )


def test_build_critical_intelligence():
    intelligence = build_evaluation_intelligence(
        [
            make_step(
                "progression",
                False,
            ),
            make_step(
                "signature",
                False,
            ),
            make_step(
                "triage",
                False,
            ),
            make_step(
                "forecast",
                True,
            ),
        ]
    )

    assert (
        intelligence.summary.failed_analyses
        == 3
    )

    assert (
        intelligence.health.status
        == "critical"
    )