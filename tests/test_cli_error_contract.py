import json

from failurelab.cli import main


def test_evaluate_missing_config_returns_2(
    tmp_path,
    monkeypatch,
    capsys,
):
    missing = tmp_path / "missing.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(missing),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "FailureLab error:" in captured.err


def test_evaluate_malformed_json_returns_2(
    tmp_path,
    monkeypatch,
    capsys,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        "{bad json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "FailureLab error:" in captured.err


def test_evaluate_invalid_profile_shape_returns_2(
    tmp_path,
    monkeypatch,
    capsys,
):
    path = tmp_path / "failurelab.json"

    path.write_text(
        json.dumps(
            [
                "invalid"
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
            str(path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2

    assert (
        "Evaluation profile must be a JSON object."
        in captured.err
    )


def test_evaluate_invalid_gate_config_returns_2(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = tmp_path / "failurelab.json"

    profile_path.write_text(
        json.dumps(
            {
                "name": "production",
                "suite_config": "suite.json",
                "occurrence_input": "failures.json",
                "run_forecast": True,
            }
        ),
        encoding="utf-8",
    )

    occurrence_path = tmp_path / "failures.json"

    occurrence_path.write_text(
        json.dumps(
            [
                {
                    "checkpoint": "v1",
                    "failure_name": "blur",
                    "priority_score": 0.8,
                },
                {
                    "checkpoint": "v2",
                    "failure_name": "blur",
                    "priority_score": 0.6,
                },
            ]
        ),
        encoding="utf-8",
    )

    gate_path = tmp_path / "gate.json"

    gate_path.write_text(
        json.dumps(
            {
                "maximum_failed_analyses": "invalid",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(profile_path),
            "--gate-config",
            str(gate_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2

    assert (
        "maximum_failed_analyses must be an integer."
        in captured.err
    )


def test_cli_errors_do_not_write_to_stdout(
    tmp_path,
    monkeypatch,
    capsys,
):
    missing = tmp_path / "missing.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "evaluate",
            "--config",
            str(missing),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert captured.out == ""
    assert captured.err