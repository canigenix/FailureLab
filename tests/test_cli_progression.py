import json

from failurelab.cli import main


def write_progression_file(tmp_path, points):
    path = tmp_path / "progression.json"

    path.write_text(
        json.dumps(points),
        encoding="utf-8",
    )

    return path


def test_progression_cli_passes(tmp_path, monkeypatch, capsys):
    input_path = write_progression_file(
        tmp_path,
        [
            {"label": "v1", "failure_rate": 0.30},
            {"label": "v2", "failure_rate": 0.20},
            {"label": "v3", "failure_rate": 0.10},
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "progression",
            "--input",
            str(input_path),
        ],
    )

    result = main()

    output = capsys.readouterr().out

    assert result == 0
    assert "Overall status: improved" in output
    assert "Trend: improving" in output
    assert "RESULT: PASSED" in output


def test_progression_cli_policy_failure(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_progression_file(
        tmp_path,
        [
            {"label": "v1", "failure_rate": 0.10},
            {"label": "v2", "failure_rate": 0.20},
            {"label": "v3", "failure_rate": 0.15},
            {"label": "v4", "failure_rate": 0.30},
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "progression",
            "--input",
            str(input_path),
            "--max-regression",
            "0.05",
            "--max-regressed-transitions",
            "1",
            "--reject-volatile",
        ],
    )

    result = main()

    output = capsys.readouterr().out

    assert result == 1
    assert "RESULT: FAILED" in output
    assert "Overall failure-rate regression" in output
    assert "Regressed transitions" in output
    assert "Volatile progression histories" in output


def test_progression_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    input_path = write_progression_file(
        tmp_path,
        [
            {"label": "v1", "failure_rate": 0.20},
            {"label": "v2", "failure_rate": 0.10},
            {"label": "v3", "failure_rate": 0.15},
        ],
    )

    output_path = tmp_path / "report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "progression",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    result = main()

    assert result == 0
    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["overall_status"] == "improved"
    assert data["trend"] == "volatile"
    assert len(data["risks"]) == 3


def test_progression_cli_respects_tolerance(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_progression_file(
        tmp_path,
        [
            {"label": "v1", "failure_rate": 0.10},
            {"label": "v2", "failure_rate": 0.105},
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "progression",
            "--input",
            str(input_path),
            "--tolerance",
            "0.01",
        ],
    )

    result = main()

    output = capsys.readouterr().out

    assert result == 0
    assert "Overall status: stable" in output
    assert "Trend: stable" in output


def test_progression_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "progression.json"

    input_path.write_text(
        json.dumps(
            {
                "label": "v1",
                "failure_rate": 0.10,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "progression",
            "--input",
            str(input_path),
        ],
    )

    result = main()

    captured = capsys.readouterr()

    assert result == 2
    assert "Progression input must be a JSON list" in captured.err