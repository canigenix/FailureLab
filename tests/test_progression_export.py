import json

from failurelab.progression import (
    ProgressionPoint,
    summarize_progression_history,
)
from failurelab.progression_export import (
    export_progression_json,
    progression_report_to_dict,
)
from failurelab.progression_policy import evaluate_progression_policy
from failurelab.progression_risk import score_checkpoint_risk


def build_report():
    return summarize_progression_history(
        [
            ProgressionPoint("v1", 0.20),
            ProgressionPoint("v2", 0.10),
            ProgressionPoint("v3", 0.25),
            ProgressionPoint("v4", 0.12),
        ]
    )


def test_progression_report_to_dict():
    report = build_report()

    data = progression_report_to_dict(report)

    assert data["overall_status"] == "improved"
    assert data["trend"] == "volatile"
    assert data["improved_count"] == 2
    assert data["regressed_count"] == 1

    assert len(data["points"]) == 4
    assert len(data["transitions"]) == 3

    assert data["points"][0] == {
        "label": "v1",
        "failure_rate": 0.20,
    }


def test_export_progression_json(tmp_path):
    report = build_report()

    path = tmp_path / "progression.json"

    result = export_progression_json(
        report,
        path,
    )

    assert result == path
    assert path.exists()

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert data["trend"] == "volatile"
    assert data["overall_status"] == "improved"


def test_export_progression_json_with_policy(tmp_path):
    report = build_report()

    policy = evaluate_progression_policy(
        report,
        max_overall_regression=0.05,
        max_regressed_transitions=0,
        allow_volatile=False,
    )

    path = tmp_path / "progression.json"

    export_progression_json(
        report,
        path,
        policy=policy,
    )

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert data["policy"]["passed"] is False
    assert len(data["policy"]["violations"]) >= 1


def test_export_progression_json_with_risks(tmp_path):
    report = build_report()

    risks = score_checkpoint_risk(
        report.points
    )

    path = tmp_path / "progression.json"

    export_progression_json(
        report,
        path,
        risks=risks,
    )

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert len(data["risks"]) == 4
    assert data["risks"][0]["label"] == "v1"
    assert "risk_score" in data["risks"][0]


def test_export_progression_json_with_everything(tmp_path):
    report = build_report()

    policy = evaluate_progression_policy(
        report,
        max_overall_regression=1.0,
        max_regressed_transitions=10,
        allow_volatile=True,
    )

    risks = score_checkpoint_risk(
        report.points
    )

    path = tmp_path / "progression.json"

    export_progression_json(
        report,
        path,
        policy=policy,
        risks=risks,
    )

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert data["policy"]["passed"] is True
    assert len(data["risks"]) == 4
    assert data["trend"] == "volatile"