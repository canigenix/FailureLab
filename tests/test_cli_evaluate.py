import json

from failurelab.cli import main


def write_profile(
    tmp_path,
    data,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def write_occurrence_input(
    tmp_path,
):
    path = tmp_path / "failures.json"

    path.write_text(
        json.dumps(
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
            ]
        ),
        encoding="utf-8",
    )

    return path


def write_triage_input(
    tmp_path,
):
    path = tmp_path / "triage.json"

    path.write_text(
        json.dumps(
            [
                {
                    "name": "blur",
                    "failure_rate": 0.80,
                    "prediction_flip_rate": 0.60,
                    "affected_fraction": 0.70,
                    "severity_weight": 1.0,
                },
                {
                    "name": "rotation",
                    "failure_rate": 0.20,
                    "prediction_flip_rate": 0.10,
                    "affected_fraction": 0.20,
                    "severity_weight": 1.0,
                },
            ]
        ),
        encoding="utf-8",
    )

    return path


def write_progression_input(
    tmp_path,
):
    path = tmp_path / "progression.json"

    path.write_text(
        json.dumps(
            [
                {
                    "label": "v1",
                    "failure_rate": 0.50,
                },
                {
                    "label": "v2",
                    "failure_rate": 0.40,
                },
                {
                    "label": "v3",
                    "failure_rate": 0.30,
                },
            ]
        ),
        encoding="utf-8",
    )

    return path


def write_signature_input(
    tmp_path,
):
    path = tmp_path / "signature.json"

    path.write_text(
        json.dumps(
            [
                {
                    "stress_name": "blur",
                    "failure_rate": 0.60,
                    "prediction_flip_rate": 0.10,
                },
                {
                    "stress_name": "rotation",
                    "failure_rate": 0.20,
                    "prediction_flip_rate": 0.05,
                },
            ]
        ),
        encoding="utf-8",
    )

    return path


def test_evaluate_cli_loads_profile(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_occurrence_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "production",
            "suite_config": "suite.json",
            "forecast_input": "failures.json",
            "run_forecast": True,
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Evaluation profile: production" in output
    assert "Suite config: suite.json" in output
    assert "Analyses: 1" in output
    assert "- forecast" in output
    assert "forecast: PASSED" in output
    assert "RESULT: PASSED" in output


def test_evaluate_cli_runs_forecast_step(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_occurrence_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "forecast-only",
            "suite_config": "suite.json",
            "forecast_input": "failures.json",
            "run_forecast": True,
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "- forecast" in output
    assert "forecast: PASSED" in output
    assert "2 failures analyzed" in output


def test_evaluate_cli_runs_all_analyses(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_occurrence_input(
        tmp_path
    )

    write_triage_input(
        tmp_path
    )

    write_progression_input(
        tmp_path
    )

    write_signature_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "full-production",
            "suite_config": "suite.json",
            "occurrence_input": "failures.json",
            "triage_input": "triage.json",
            "progression_input": "progression.json",
            "signature_input": "signature.json",
            "run_progression": True,
            "run_signature": True,
            "run_triage": True,
            "run_persistence": True,
            "run_resolution": True,
            "run_forecast": True,
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Evaluation profile: full-production" in output
    assert "Analyses: 6" in output

    expected_plan = [
        "- progression",
        "- signature",
        "- triage",
        "- persistence",
        "- resolution",
        "- forecast",
    ]

    positions = [
        output.index(item)
        for item in expected_plan
    ]

    assert positions == sorted(
        positions
    )

    assert "progression: PASSED" in output
    assert "signature: PASSED" in output
    assert "triage: PASSED" in output
    assert "persistence: PASSED" in output
    assert "resolution: PASSED" in output
    assert "forecast: PASSED" in output
    assert "RESULT: PASSED" in output


def test_evaluate_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    write_occurrence_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "production",
            "suite_config": "suite.json",
            "occurrence_input": "failures.json",
            "run_forecast": True,
        },
    )

    output_path = (
        tmp_path
        / "evaluation-report.json"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
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

    assert data["profile_name"] == "production"
    assert data["suite_config"] == "suite.json"
    assert data["passed"] is True
    assert data["passed_count"] == 1
    assert data["failed_count"] == 0

    assert [
        step["analysis"]
        for step in data["steps"]
    ] == [
        "forecast",
    ]

    assert (
        data["steps"][0]["analysis"]
        == "forecast"
    )

    assert (
        data["steps"][0]["passed"]
        is True
    )


def test_evaluate_cli_exports_all_analyses(
    tmp_path,
    monkeypatch,
):
    write_occurrence_input(
        tmp_path
    )

    write_triage_input(
        tmp_path
    )

    write_progression_input(
        tmp_path
    )

    write_signature_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "full-production",
            "suite_config": "suite.json",
            "occurrence_input": "failures.json",
            "triage_input": "triage.json",
            "progression_input": "progression.json",
            "signature_input": "signature.json",
            "run_progression": True,
            "run_signature": True,
            "run_triage": True,
            "run_persistence": True,
            "run_resolution": True,
            "run_forecast": True,
        },
    )

    output_path = (
        tmp_path
        / "full-evaluation-report.json"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
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

    assert data["profile_name"] == "full-production"
    assert data["passed"] is True
    assert data["passed_count"] == 6
    assert data["failed_count"] == 0

    assert [
        step["analysis"]
        for step in data["steps"]
    ] == [
        "progression",
        "signature",
        "triage",
        "persistence",
        "resolution",
        "forecast",
    ]


def test_evaluate_cli_rejects_no_analysis(
    tmp_path,
    monkeypatch,
    capsys,
):
    config_path = write_profile(
        tmp_path,
        {
            "name": "production",
            "suite_config": "suite.json",
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 1

    assert (
        "at least one analysis"
        in captured.err
    )


def test_evaluate_cli_rejects_empty_name(
    tmp_path,
    monkeypatch,
    capsys,
):
    config_path = write_profile(
        tmp_path,
        {
            "name": " ",
            "suite_config": "suite.json",
            "run_forecast": True,
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 1

    assert (
        "name cannot be empty"
        in captured.err
    )


def test_evaluate_cli_invalid_json_shape(
    tmp_path,
    monkeypatch,
    capsys,
):
    config_path = (
        tmp_path
        / "failurelab.json"
    )

    config_path.write_text(
        json.dumps(
            [
                "bad"
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2

    assert (
        "Evaluation profile must be a JSON object"
        in captured.err
    )

def test_evaluate_cli_prints_health_summary(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_occurrence_input(
        tmp_path
    )

    config_path = write_profile(
        tmp_path,
        {
            "name": "production",
            "suite_config": "suite.json",
            "occurrence_input": "failures.json",
            "run_forecast": True,
        },
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(config_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0

    assert "Health: healthy" in output
    assert "Failed analyses: 0/1" in output
    assert "Failure ratio: 0.00%" in output

    assert (
        "All enabled analyses passed."
        in output
    )