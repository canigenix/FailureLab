import json
import sys

from failurelab.cli import main


def test_history_command_reports_suite_trend(
    tmp_path,
    capsys,
):
    history_path = tmp_path / "history.json"

    history_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "suite_name": "production-vision",
                        "timestamp": "2026-08-16T10:00:00+00:00",
                        "status": "passed",
                        "worst_stress": "blur_2.00",
                        "worst_drop": 0.10,
                        "maximum_drop": 0.20,
                        "model_id": "resnet18-v2",
                        "run_id": "run-001",
                    },
                    {
                        "suite_name": "production-vision",
                        "timestamp": "2026-08-16T11:00:00+00:00",
                        "status": "passed",
                        "worst_stress": "blur_2.00",
                        "worst_drop": 0.16,
                        "maximum_drop": 0.20,
                        "model_id": "resnet18-v3",
                        "run_id": "run-002",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            "history",
            "--input",
            str(history_path),
            "--suite",
            "production-vision",
        ]

        exit_code = main()

    finally:
        sys.argv = original_argv

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Suite: production-vision" in captured.out
    assert "Latest status: passed" in captured.out
    assert "Worst stress: blur_2.00" in captured.out
    assert "Worst drop: 16.00%" in captured.out
    assert "Trend: regressed" in captured.out
    assert "Run ID: run-002" in captured.out


def test_history_command_reports_model_trend(
    tmp_path,
    capsys,
):
    history_path = tmp_path / "history.json"

    history_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "suite_name": "production-vision",
                        "timestamp": "2026-08-16T10:00:00+00:00",
                        "status": "passed",
                        "worst_stress": "brightness_0.50",
                        "worst_drop": 0.18,
                        "maximum_drop": 0.25,
                        "model_id": "resnet18-v3",
                        "run_id": "run-001",
                    },
                    {
                        "suite_name": "production-vision",
                        "timestamp": "2026-08-16T11:00:00+00:00",
                        "status": "passed",
                        "worst_stress": "brightness_0.50",
                        "worst_drop": 0.12,
                        "maximum_drop": 0.25,
                        "model_id": "resnet18-v3",
                        "run_id": "run-002",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            "history",
            "--input",
            str(history_path),
            "--model",
            "resnet18-v3",
        ]

        exit_code = main()

    finally:
        sys.argv = original_argv

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Model: resnet18-v3" in captured.out
    assert "Suite: production-vision" in captured.out
    assert "Latest status: passed" in captured.out
    assert "Worst drop: 12.00%" in captured.out
    assert "Trend: improved" in captured.out
    assert "Run ID: run-002" in captured.out