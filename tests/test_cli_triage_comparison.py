import json

from failurelab.cli import main


def write_triage_file(
    tmp_path,
    rows,
    name,
):
    path = tmp_path / name

    path.write_text(
        json.dumps(rows),
        encoding="utf-8",
    )

    return path


def test_triage_compare_cli_improved(
    tmp_path,
    monkeypatch,
    capsys,
):
    baseline_path = write_triage_file(
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
        "baseline.json",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.30,
                "prediction_flip_rate": 0.20,
                "affected_fraction": 0.20,
            },
            {
                "name": "rotation",
                "failure_rate": 0.10,
                "prediction_flip_rate": 0.05,
                "affected_fraction": 0.10,
            },
        ],
        "candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Status: improved" in output
    assert "RESULT: PASSED" in output


def test_triage_compare_cli_rejects_regression(
    tmp_path,
    monkeypatch,
    capsys,
):
    baseline_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
        "baseline.json",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 1.0,
                "prediction_flip_rate": 1.0,
                "affected_fraction": 1.0,
            },
        ],
        "candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Status: regressed" in output
    assert "Failure triage regressed." in output
    assert "RESULT: FAILED" in output


def test_triage_compare_cli_can_allow_regression(
    tmp_path,
    monkeypatch,
    capsys,
):
    baseline_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
        "baseline.json",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 1.0,
                "prediction_flip_rate": 1.0,
                "affected_fraction": 1.0,
            },
        ],
        "candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--allow-regression",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Status: regressed" in output
    assert "RESULT: PASSED" in output


def test_triage_compare_cli_policy_limits(
    tmp_path,
    monkeypatch,
    capsys,
):
    baseline_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
        "baseline.json",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 1.0,
                "prediction_flip_rate": 1.0,
                "affected_fraction": 1.0,
            },
        ],
        "candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--allow-regression",
            "--max-actionable-increase",
            "0",
            "--max-critical-increase",
            "0",
            "--max-score-increase",
            "0.10",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Actionable failure increase exceeded limit" in output
    assert "Critical failure increase exceeded limit" in output
    assert "Priority score increase exceeded limit" in output
    assert "RESULT: FAILED" in output


def test_triage_compare_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    baseline_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            },
        ],
        "baseline.json",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 1.0,
                "prediction_flip_rate": 1.0,
                "affected_fraction": 1.0,
            },
        ],
        "candidate.json",
    )

    output_path = tmp_path / "comparison.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--allow-regression",
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

    assert data["status"] == "regressed"
    assert data["candidate_critical"] == 1
    assert data["policy"]["passed"] is True


def test_triage_compare_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    baseline_path = tmp_path / "baseline.json"

    baseline_path.write_text(
        json.dumps(
            {
                "name": "blur",
                "failure_rate": 0.20,
                "prediction_flip_rate": 0.10,
                "affected_fraction": 0.20,
            }
        ),
        encoding="utf-8",
    )

    candidate_path = write_triage_file(
        tmp_path,
        [
            {
                "name": "blur",
                "failure_rate": 0.30,
                "prediction_flip_rate": 0.20,
                "affected_fraction": 0.20,
            },
        ],
        "candidate.json",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "triage-compare",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Triage comparison input must be a JSON list" in captured.err