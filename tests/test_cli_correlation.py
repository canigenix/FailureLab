import json
import sys

from failurelab.cli import main
from failurelab.sample_analysis import (
    SampleFailureResult,
)
from failurelab.sample_report import (
    SampleFailureReport,
)


def build_report(tmp_path):
    report = SampleFailureReport(
        suite_name="correlation-cli-test",
        samples=[
            SampleFailureResult(
                sample_index=0,
                target=0,
                stress_count=3,
                failure_stress_count=2,
                failure_frequency=2 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "blur",
                    "noise",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
            SampleFailureResult(
                sample_index=1,
                target=1,
                stress_count=3,
                failure_stress_count=2,
                failure_frequency=2 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "blur",
                    "noise",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
            SampleFailureResult(
                sample_index=2,
                target=1,
                stress_count=3,
                failure_stress_count=1,
                failure_frequency=1 / 3,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[
                    "brightness",
                ],
                flipped_stresses=[],
                severity="localized",
            ),
        ],
    )

    path = tmp_path / "sample-report.json"

    report.save_json(
        path
    )

    return path


def run_cli(args):
    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            *args,
        ]

        return main()

    finally:
        sys.argv = original_argv


def test_correlation_cli_displays_analysis(
    tmp_path,
    capsys,
):
    report_path = build_report(
        tmp_path
    )

    exit_code = run_cli(
        [
            "correlation",
            "--input",
            str(report_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Suite: correlation-cli-test" in captured.out
    assert "Stress pairs: 3" in captured.out
    assert "Strongest pair: blur + noise" in captured.out
    assert "100.00%" in captured.out


def test_correlation_cli_saves_report(
    tmp_path,
):
    report_path = build_report(
        tmp_path
    )

    output_path = (
        tmp_path / "correlation-report.json"
    )

    exit_code = run_cli(
        [
            "correlation",
            "--input",
            str(report_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert data["suite_name"] == "correlation-cli-test"
    assert data["pair_count"] == 3

    assert (
        data["strongest_pair"]["stress_a"]
        == "blur"
    )

    assert (
        data["strongest_pair"]["stress_b"]
        == "noise"
    )


def test_correlation_cli_policy_passes(
    tmp_path,
    capsys,
):
    report_path = build_report(
        tmp_path
    )

    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_correlation": 1.0,
                "maximum_high_correlation_pairs": 1,
                "high_correlation_threshold": 0.75,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "correlation",
            "--input",
            str(report_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "RESULT: PASSED" in captured.out


def test_correlation_cli_policy_fails(
    tmp_path,
    capsys,
):
    report_path = build_report(
        tmp_path
    )

    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_correlation": 0.80,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "correlation",
            "--input",
            str(report_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "maximum_correlation" in captured.out
    assert "RESULT: FAILED" in captured.out


def test_correlation_cli_missing_input_returns_two(
    tmp_path,
    capsys,
):
    exit_code = run_cli(
        [
            "correlation",
            "--input",
            str(
                tmp_path / "missing.json"
            ),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "FailureLab error:" in captured.err