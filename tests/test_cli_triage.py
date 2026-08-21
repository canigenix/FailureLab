import json

from failurelab.cli import main


def write_triage_file(
    tmp_path,
    rows,
    name="triage.json",
):
    path = tmp_path / name

    path.write_text(
        json.dumps(rows),
        encoding="utf-8",
    )

    return path


def test_triage_cli_passes(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.80,
                "prediction_flip_rate": 0.70,
                "affected_fraction": 0.80,
            },
            {
                "name": "rotation",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Failures: 2" in output
    assert "Highest priority: blur" in output
    assert "RESULT: PASSED" in output


def test_triage_cli_policy_failure(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 1.0,
                "prediction_flip_rate": 1.0,
                "affected_fraction": 1.0,
            },
            {
                "name": "rotation",
                "failure_rate": 0.60,
                "prediction_flip_rate": 0.50,
                "affected_fraction": 0.50,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage",
            "--input",
            str(input_path),
            "--max-critical",
            "0",
            "--max-high",
            "0",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Critical failures exceeded limit" in output
    assert "High-priority failures exceeded limit" in output
    assert "RESULT: FAILED" in output


def test_triage_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    input_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.80,
                "prediction_flip_rate": 0.70,
                "affected_fraction": 0.80,
            },
            {
                "name": "rotation",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
    )

    output_path = tmp_path / "triage-report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage",
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

    assert data["total_failures"] == 2
    assert data["highest_priority"]["name"] == "blur"
    assert len(data["remediations"]) == 2


def test_triage_cli_respects_severity_weight(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.40,
                "prediction_flip_rate": 0.20,
                "affected_fraction": 0.30,
                "severity_weight": 1.5,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Highest priority: blur" in output


def test_triage_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "bad-triage.json"

    input_path.write_text(
        json.dumps(
            {
                "name": "blur",
                "failure_rate": 0.80,
                "prediction_flip_rate": 0.70,
                "affected_fraction": 0.80,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Triage input must be a JSON list" in captured.err