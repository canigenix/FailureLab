import json

from failurelab.export import (
    export_vision_html,
    export_vision_json,
)
from failurelab.score import RobustnessScore
from failurelab.vision_report import VisionWeakness


def make_weaknesses():
    return [
        VisionWeakness(
            name="blur",
            severity="critical",
            top1_drop=0.34,
            top5_drop=0.32,
            confidence_drop=0.247,
        ),
        VisionWeakness(
            name="compression",
            severity="medium",
            top1_drop=0.07,
            top5_drop=0.03,
            confidence_drop=0.027,
        ),
    ]


def make_score():
    return RobustnessScore(
        score=79.5,
        grade="C",
        status="Needs Improvement",
    )


def test_export_vision_json(tmp_path):
    path = tmp_path / "report.json"

    export_vision_json(
        make_weaknesses(),
        path,
        robustness_score=make_score(),
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["failurelab_version"] == "0.1.0"
    assert len(data["weaknesses"]) == 2

    assert data["robustness_score"]["score"] == 79.5
    assert data["robustness_score"]["grade"] == "C"
    assert (
        data["robustness_score"]["status"]
        == "Needs Improvement"
    )

    assert data["weaknesses"][0]["name"] == "blur"
    assert data["weaknesses"][0]["severity"] == "critical"


def test_export_vision_html(tmp_path):
    path = tmp_path / "report.html"

    export_vision_html(
        make_weaknesses(),
        path,
        robustness_score=make_score(),
    )

    assert path.exists()

    content = path.read_text(
        encoding="utf-8"
    )

    assert "FailureLab Vision Robustness Report" in content
    assert "Robustness Score" in content
    assert "79.5" in content
    assert "Grade C" in content
    assert "Needs Improvement" in content
    assert "Blur" in content
    assert "34.0%" in content
    assert "Compression" in content