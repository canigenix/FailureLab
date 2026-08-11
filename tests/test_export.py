import json

from failurelab.failurelab.export import (
    export_vision_html,
    export_vision_json,
)
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


def test_export_vision_json(tmp_path):
    path = tmp_path / "report.json"

    export_vision_json(
        make_weaknesses(),
        path,
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["failurelab_version"] == "0.1.0"
    assert len(data["weaknesses"]) == 2

    assert data["weaknesses"][0]["name"] == "blur"
    assert data["weaknesses"][0]["severity"] == "critical"


def test_export_vision_html(tmp_path):
    path = tmp_path / "report.html"

    export_vision_html(
        make_weaknesses(),
        path,
    )

    assert path.exists()

    content = path.read_text(
        encoding="utf-8"
    )

    assert "FailureLab Vision Robustness Report" in content
    assert "Blur" in content
    assert "34.0%" in content
    assert "Compression" in content