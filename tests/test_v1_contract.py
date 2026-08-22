import json

import failurelab

from failurelab.cli import main
from failurelab.evaluation_gate import (
    evaluate_intelligence_gate,
)
from failurelab.evaluation_health import (
    classify_evaluation_health,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)
from failurelab.evaluation_summary import (
    build_evaluation_summary,
)


def test_v1_public_contract():
    required = {
        "FailureLab",
        "EvaluationProfile",
        "EvaluationReport",
        "EvaluationSummary",
        "EvaluationHealth",
        "EvaluationIntelligence",
        "EvaluationGateConfig",
        "EvaluationGateResult",
        "run_evaluation",
        "run_evaluation_gate",
        "evaluate_report_gate",
    }

    assert required.issubset(
        set(
            failurelab.__all__
        )
    )


def test_v1_evaluation_intelligence_contract():
    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="progression",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="signature",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    assert report.passed is True
    assert report.health_status == "healthy"

    intelligence = report.intelligence

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


def test_v1_gate_contract():
    summary = build_evaluation_summary(
        [
            EvaluationStepResult(
                analysis="progression",
                passed=False,
            ),
            EvaluationStepResult(
                analysis="signature",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
        ]
    )

    health = classify_evaluation_health(
        summary
    )

    intelligence = failurelab.EvaluationIntelligence(
        summary=summary,
        health=health,
    )

    passed_gate = evaluate_intelligence_gate(
        intelligence,
        maximum_failed_analyses=1,
        allowed_health_statuses=(
            "healthy",
            "watch",
        ),
    )

    assert passed_gate.passed is True

    failed_gate = evaluate_intelligence_gate(
        intelligence,
        maximum_failed_analyses=0,
        allowed_health_statuses=(
            "healthy",
        ),
    )

    assert failed_gate.passed is False
    assert failed_gate.violations


def test_v1_cli_success_contract(
    tmp_path,
    monkeypatch,
    capsys,
):
    failures = tmp_path / "failures.json"

    failures.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.8,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.6,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = tmp_path / "failurelab.json"

    profile.write_text(
        json.dumps(
            {
                "name": "production",
                "suite_config": "suite.json",
                "occurrence_input": "failures.json",
                "run_forecast": True,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(profile),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 0
    assert "Health: healthy" in captured.out
    assert "RESULT: PASSED" in captured.out
    assert captured.err == ""


def test_v1_cli_gate_failure_contract(
    tmp_path,
    monkeypatch,
    capsys,
):
    failures = tmp_path / "failures.json"

    failures.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.8,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.6,
                },
            ]
        ),
        encoding="utf-8",
    )

    profile = tmp_path / "failurelab.json"

    profile.write_text(
        json.dumps(
            {
                "name": "production",
                "suite_config": "suite.json",
                "occurrence_input": "failures.json",
                "run_forecast": True,
            }
        ),
        encoding="utf-8",
    )

    gate = tmp_path / "gate.json"

    gate.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 1,
                "allowed_health_statuses": [
                    "watch",
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(profile),
            "--gate-config",
            str(gate),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Gate: FAILED" in captured.out
    assert "RESULT: FAILED" in captured.out