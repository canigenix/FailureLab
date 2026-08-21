import json

from failurelab.evaluation_gate_service import (
    evaluate_report_gate,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)


def test_gate_service_passes_healthy_report(
    tmp_path,
):
    config_path = tmp_path / "gate.json"

    config_path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 0,
                "allowed_health_statuses": [
                    "healthy",
                ],
            }
        ),
        encoding="utf-8",
    )

    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="progression",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    result = evaluate_report_gate(
        report,
        config_path,
    )

    assert result.passed is True
    assert result.status == "passed"
    assert result.violations == ()


def test_gate_service_rejects_failed_analysis(
    tmp_path,
):
    config_path = tmp_path / "gate.json"

    config_path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 0,
                "allowed_health_statuses": [
                    "healthy",
                    "watch",
                ],
            }
        ),
        encoding="utf-8",
    )

    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="progression",
                passed=False,
            ),
            EvaluationStepResult(
                analysis="signature",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    result = evaluate_report_gate(
        report,
        config_path,
    )

    assert result.passed is False

    assert (
        "Failed analyses 1 exceed maximum 0."
        in result.violations
    )


def test_gate_service_rejects_health_status(
    tmp_path,
):
    config_path = tmp_path / "gate.json"

    config_path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 1,
                "allowed_health_statuses": [
                    "healthy",
                ],
            }
        ),
        encoding="utf-8",
    )

    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="progression",
                passed=False,
            ),
            EvaluationStepResult(
                analysis="signature",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    result = evaluate_report_gate(
        report,
        config_path,
    )

    assert result.passed is False

    assert (
        "Health status 'watch' is not allowed."
        in result.violations
    )


def test_gate_service_allows_configured_watch(
    tmp_path,
):
    config_path = tmp_path / "gate.json"

    config_path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": 1,
                "allowed_health_statuses": [
                    "healthy",
                    "watch",
                ],
            }
        ),
        encoding="utf-8",
    )

    report = EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="progression",
                passed=False,
            ),
            EvaluationStepResult(
                analysis="signature",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="triage",
                passed=True,
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    result = evaluate_report_gate(
        report,
        config_path,
    )

    assert result.passed is True
    assert result.violations == ()