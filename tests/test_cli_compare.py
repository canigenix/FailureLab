import json

from failurelab.cli import main


def write_snapshot(
    path,
    *,
    score,
    threshold,
    worst_drop,
):
    payload = {
        "score": score,
        "boundaries": [
            {
                "stress_name": "occlusion",
                "failure_threshold": threshold,
                "worst_top1_drop": worst_drop,
            }
        ],
    }

    path.write_text(
        json.dumps(
            payload
        ),
        encoding="utf-8",
    )


def test_cli_compare_passes(
    tmp_path,
    monkeypatch,
):
    baseline = (
        tmp_path
        / "baseline.json"
    )

    candidate = (
        tmp_path
        / "candidate.json"
    )

    write_snapshot(
        baseline,
        score=75.0,
        threshold=0.30,
        worst_drop=0.50,
    )

    write_snapshot(
        candidate,
        score=80.0,
        threshold=0.40,
        worst_drop=0.40,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
        ],
    )

    exit_code = main()

    assert exit_code == 0


def test_cli_compare_fails_on_regression(
    tmp_path,
    monkeypatch,
):
    baseline = (
        tmp_path
        / "baseline.json"
    )

    candidate = (
        tmp_path
        / "candidate.json"
    )

    write_snapshot(
        baseline,
        score=75.0,
        threshold=0.40,
        worst_drop=0.50,
    )

    write_snapshot(
        candidate,
        score=74.0,
        threshold=0.30,
        worst_drop=0.48,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
        ],
    )

    exit_code = main()

    assert exit_code == 1


def test_cli_compare_returns_two_for_missing_file(
    tmp_path,
    monkeypatch,
):
    missing = (
        tmp_path
        / "missing.json"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(missing),
            "--candidate",
            str(missing),
        ],
    )

    exit_code = main()

    assert exit_code == 2


def test_cli_compare_custom_tolerance(
    tmp_path,
    monkeypatch,
):
    baseline = (
        tmp_path
        / "baseline.json"
    )

    candidate = (
        tmp_path
        / "candidate.json"
    )

    write_snapshot(
        baseline,
        score=75.0,
        threshold=None,
        worst_drop=0.20,
    )

    write_snapshot(
        candidate,
        score=75.0,
        threshold=None,
        worst_drop=0.25,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
            "--tolerance",
            "0.10",
        ],
    )

    exit_code = main()

    assert exit_code == 0


def test_cli_compare_default_tolerance_detects_drop(
    tmp_path,
    monkeypatch,
):
    baseline = (
        tmp_path
        / "baseline.json"
    )

    candidate = (
        tmp_path
        / "candidate.json"
    )

    write_snapshot(
        baseline,
        score=75.0,
        threshold=None,
        worst_drop=0.20,
    )

    write_snapshot(
        candidate,
        score=75.0,
        threshold=None,
        worst_drop=0.25,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
        ],
    )

    exit_code = main()

    assert exit_code == 1


def test_cli_compare_rejects_negative_tolerance(
    tmp_path,
    monkeypatch,
):
    baseline = (
        tmp_path
        / "baseline.json"
    )

    candidate = (
        tmp_path
        / "candidate.json"
    )

    write_snapshot(
        baseline,
        score=75.0,
        threshold=None,
        worst_drop=0.20,
    )

    write_snapshot(
        candidate,
        score=75.0,
        threshold=None,
        worst_drop=0.20,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "failurelab",
            "compare",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
            "--tolerance",
            "-0.01",
        ],
    )

    exit_code = main()

    assert exit_code == 2