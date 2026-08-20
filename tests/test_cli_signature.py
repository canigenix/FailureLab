import json

from failurelab.cli import main


def write_signature_file(tmp_path, rows, name="signature.json"):
    path = tmp_path / name

    path.write_text(
        json.dumps(rows),
        encoding="utf-8",
    )

    return path


def test_signature_cli_basic(tmp_path, monkeypatch, capsys):
    input_path = write_signature_file(
        tmp_path,
        [
            {
                "stress_name": "blur",
                "failure_rate": 0.25,
                "prediction_flip_rate": 0.05,
            },
            {
                "stress_name": "rotation",
                "failure_rate": 0.02,
                "prediction_flip_rate": 0.01,
            },
            {
                "stress_name": "crop",
                "failure_rate": 0.01,
                "prediction_flip_rate": 0.01,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Signature type: localized" in output
    assert "Dominant stress: blur" in output
    assert "RESULT: PASSED" in output


def test_signature_cli_with_baseline(tmp_path, monkeypatch, capsys):
    baseline_path = write_signature_file(
        tmp_path,
        [
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
        name="baseline.json",
    )

    input_path = write_signature_file(
        tmp_path,
        [
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
        name="candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature",
            "--input",
            str(input_path),
            "--baseline",
            str(baseline_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Comparison status: regressed" in output
    assert "Mean failure-rate delta:" in output


def test_signature_cli_exports_json(tmp_path, monkeypatch):
    input_path = write_signature_file(
        tmp_path,
        [
            {
                "stress_name": "blur",
                "failure_rate": 0.25,
                "prediction_flip_rate": 0.05,
            },
            {
                "stress_name": "rotation",
                "failure_rate": 0.02,
                "prediction_flip_rate": 0.01,
            },
        ],
    )

    output_path = tmp_path / "report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature",
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

    assert data["signature"]["dominant_stress"] == "blur"
    assert "diagnostic_report" in data


def test_signature_cli_respects_thresholds(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_signature_file(
        tmp_path,
        [
            {
                "stress_name": "blur",
                "failure_rate": 0.12,
                "prediction_flip_rate": 0.05,
            },
            {
                "stress_name": "rotation",
                "failure_rate": 0.11,
                "prediction_flip_rate": 0.04,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature",
            "--input",
            str(input_path),
            "--affected-threshold",
            "0.15",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Signature type: low-risk" in output


def test_signature_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "signature.json"

    input_path.write_text(
        json.dumps(
            {
                "stress_name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.05,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "signature",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Signature input must be a JSON list" in captured.err