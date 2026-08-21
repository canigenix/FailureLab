import json

from failurelab.cli import main


def write_forecast_file(
    tmp_path,
    rows,
    name="forecast.json",
):
    path = tmp_path / name

    path.write_text(
        json.dumps(rows),
        encoding="utf-8",
    )

    return path


def test_forecast_cli_passes(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_forecast_file(
        tmp_path,
        [
            {
                "checkpoint": "v1",
                "failure_name": "blur",
                "priority_score": 0.80,
            },
            {
                "checkpoint": "v2",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
            {
                "checkpoint": "v3",
                "failure_name": "blur",
                "priority_score": 0.40,
            },
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.20,
            },
            {
                "checkpoint": "v2",
                "failure_name": "rotation",
                "priority_score": 0.40,
            },
            {
                "checkpoint": "v3",
                "failure_name": "rotation",
                "priority_score": 0.60,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Failures: 2" in output
    assert "Improving: 1" in output
    assert "Worsening: 1" in output
    assert "Highest projected risk: rotation" in output
    assert "RESULT: PASSED" in output


def test_forecast_cli_respects_tolerance(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_forecast_file(
        tmp_path,
        [
            {
                "checkpoint": "v1",
                "failure_name": "blur",
                "priority_score": 0.50,
            },
            {
                "checkpoint": "v2",
                "failure_name": "blur",
                "priority_score": 0.505,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
            "--input",
            str(input_path),
            "--tolerance",
            "0.01",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Stable: 1" in output
    assert "Worsening: 0" in output


def test_forecast_cli_policy_failure(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_forecast_file(
        tmp_path,
        [
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.20,
            },
            {
                "checkpoint": "v2",
                "failure_name": "rotation",
                "priority_score": 0.60,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
            "--input",
            str(input_path),
            "--max-worsening",
            "0",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Worsening forecasts exceeded limit" in output
    assert "RESULT: FAILED" in output


def test_forecast_cli_projected_score_policy(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_forecast_file(
        tmp_path,
        [
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.20,
            },
            {
                "checkpoint": "v2",
                "failure_name": "rotation",
                "priority_score": 0.60,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
            "--input",
            str(input_path),
            "--max-projected-score",
            "0.90",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Projected failure score exceeded limit" in output


def test_forecast_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    input_path = write_forecast_file(
        tmp_path,
        [
            {
                "checkpoint": "v1",
                "failure_name": "blur",
                "priority_score": 0.80,
            },
            {
                "checkpoint": "v2",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.20,
            },
            {
                "checkpoint": "v2",
                "failure_name": "rotation",
                "priority_score": 0.60,
            },
        ],
    )

    output_path = tmp_path / "forecast-report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
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
    assert data["improving_count"] == 1
    assert data["worsening_count"] == 1
    assert data["highest_projected_risk"]["failure_name"] == "rotation"


def test_forecast_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "bad-forecast.json"

    input_path.write_text(
        json.dumps(
            {
                "checkpoint": "v1",
                "failure_name": "blur",
                "priority_score": 0.80,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "forecast",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Forecast input must be a JSON list" in captured.err