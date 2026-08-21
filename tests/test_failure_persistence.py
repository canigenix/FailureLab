import json

from failurelab.cli import main


def write_persistence_file(
    tmp_path,
    rows,
    name="persistence.json",
):
    path = tmp_path / name

    path.write_text(
        json.dumps(rows),
        encoding="utf-8",
    )

    return path


def test_persistence_cli_passes(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_persistence_file(
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
                "priority_score": 0.70,
            },
            {
                "checkpoint": "v3",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.40,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "persistence",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 0
    assert "Failures: 2" in output
    assert "Persistent: 1" in output
    assert "Highest persistence: blur" in output
    assert "RESULT: PASSED" in output


def test_persistence_cli_policy_failure(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_persistence_file(
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
                "priority_score": 0.70,
            },
            {
                "checkpoint": "v3",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "persistence",
            "--input",
            str(input_path),
            "--max-persistent",
            "0",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Persistent failures exceeded limit" in output
    assert "RESULT: FAILED" in output


def test_persistence_cli_recurrence_rate_policy(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = write_persistence_file(
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
                "priority_score": 0.70,
            },
            {
                "checkpoint": "v3",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "persistence",
            "--input",
            str(input_path),
            "--max-recurrence-rate",
            "0.90",
        ],
    )

    result = main()
    output = capsys.readouterr().out

    assert result == 1
    assert "Highest recurrence rate exceeded limit" in output
    assert "RESULT: FAILED" in output


def test_persistence_cli_exports_json(
    tmp_path,
    monkeypatch,
):
    input_path = write_persistence_file(
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
                "priority_score": 0.70,
            },
            {
                "checkpoint": "v3",
                "failure_name": "blur",
                "priority_score": 0.60,
            },
            {
                "checkpoint": "v1",
                "failure_name": "rotation",
                "priority_score": 0.40,
            },
        ],
    )

    output_path = tmp_path / "persistence-report.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "persistence",
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
    assert data["persistent_count"] == 1
    assert data["highest_persistence"]["failure_name"] == "blur"


def test_persistence_cli_rejects_invalid_input(
    tmp_path,
    monkeypatch,
    capsys,
):
    input_path = tmp_path / "bad-persistence.json"

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
            "persistence",
            "--input",
            str(input_path),
        ],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 2
    assert "Persistence input must be a JSON list" in captured.err