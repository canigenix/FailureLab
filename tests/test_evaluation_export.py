import json

from failurelab.evaluation_export import (
    evaluation_report_to_dict,
    export_evaluation_json,
)
from failurelab.evaluation_report import (
    EvaluationReport,
    EvaluationStepResult,
)


def make_report():
    return EvaluationReport(
        profile_name="production",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="triage",
                passed=True,
                message="Triage passed.",
            ),
            EvaluationStepResult(
                analysis="forecast",
                passed=False,
                message="Projected risk exceeded.",
            ),
        ),
    )


def test_evaluation_report_to_dict():
    data = evaluation_report_to_dict(
        make_report()
    )

    assert data["profile_name"] == "production"
    assert data["suite_config"] == "suite.json"
    assert data["passed"] is False
    assert data["passed_count"] == 1
    assert data["failed_count"] == 1
    assert len(data["steps"]) == 2

    assert (
        data["steps"][0]["analysis"]
        == "triage"
    )

    assert (
        data["steps"][1]["analysis"]
        == "forecast"
    )


def test_export_evaluation_json(
    tmp_path,
):
    path = tmp_path / "evaluation.json"

    result = export_evaluation_json(
        make_report(),
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["profile_name"] == "production"
    assert data["passed"] is False
    assert data["failed_count"] == 1


def test_export_preserves_step_messages(
    tmp_path,
):
    path = tmp_path / "evaluation.json"

    export_evaluation_json(
        make_report(),
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        data["steps"][0]["message"]
        == "Triage passed."
    )

    assert (
        data["steps"][1]["message"]
        == "Projected risk exceeded."
    )


def test_export_passing_report(
    tmp_path,
):
    report = EvaluationReport(
        profile_name="basic",
        suite_config="suite.json",
        steps=(
            EvaluationStepResult(
                analysis="forecast",
                passed=True,
            ),
        ),
    )

    path = tmp_path / "passing.json"

    export_evaluation_json(
        report,
        path,
    )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["passed"] is True
    assert data["passed_count"] == 1
    assert data["failed_count"] == 0