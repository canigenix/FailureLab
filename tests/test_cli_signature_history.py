import json

from failurelab.cli import main


def write_history_file(
    tmp_path,
    checkpoints,
    name="signature-history.json",
):
    path = tmp_path / name

    path.write_text(
        json.dumps(checkpoints),
        encoding="utf-8",
    )

    return path


def test_signature_history_cli_passes(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_history_file(
        tmp_path,
        [
            {
                "label": "v1",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.30,
                        "prediction_flip_rate": 0.10,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.20,
                        "prediction_flip_rate": 0.08,
                    },
                ],
            },
            {
                "label": "v2",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.20,
                        "prediction_flip_rate": 0.06,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.04,
                    },
                ],
            },
            {
                "label": "v3",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.03,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.05,
                        "prediction_flip_rate": 0.02,
                    },
                ],
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature-history",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Trend: improving" in output
    assert "Improved transitions: 2" in output
    assert "RESULT: PASSED" in output


def test_signature_history_cli_policy_failure(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_history_file(
        tmp_path,
        [
            {
                "label": "v1",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.20,
                        "prediction_flip_rate": 0.05,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.03,
                    },
                ],
            },
            {
                "label": "v2",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.03,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.05,
                        "prediction_flip_rate": 0.02,
                    },
                ],
            },
            {
                "label": "v3",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.25,
                        "prediction_flip_rate": 0.08,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.15,
                        "prediction_flip_rate": 0.05,
                    },
                ],
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature-history",
            "--input",
            str(input_path),
            "--max-regressed-transitions",
            "0",
            "--reject-volatile",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Regressed signature transitions exceeded limit" in output
    assert "Signature history trend is volatile" in output
    assert "RESULT: FAILED" in output


def test_signature_history_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    input_path = write_history_file(
        tmp_path,
        [
            {
                "label": "v1",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.20,
                        "prediction_flip_rate": 0.05,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.03,
                    },
                ],
            },
            {
                "label": "v2",
                "signals": [
                    {
                        "stress_name": "blur",
                        "failure_rate": 0.10,
                        "prediction_flip_rate": 0.03,
                    },
                    {
                        "stress_name": "rotation",
                        "failure_rate": 0.05,
                        "prediction_flip_rate": 0.02,
                    },
                ],
            },
        ],
    )

    output_path = tmp_path / "history-report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature-history",
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

    assert data["trend"] == "improving"
    assert len(data["checkpoints"]) == 2
    assert len(data["transitions"]) == 1


def test_signature_history_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "bad-history.json"

    input_path.write_text(
        json.dumps(
            {
                "label": "v1",
                "signals": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature-history",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Signature history input must be a JSON list" in captured.err