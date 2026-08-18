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
        suite_name="production-vision",
        samples=[
            SampleFailureResult(
                sample_index=0,
                target=1,
                stress_count=3,
                failure_stress_count=3,
                failure_frequency=1.0,
                flip_stress_count=2,
                flip_frequency=2 / 3,
                failed_stresses=[
                    "blur",
                    "noise",
                    "brightness",
                ],
                flipped_stresses=[
                    "blur",
                    "noise",
                ],
                severity="systemic",
            ),
            SampleFailureResult(
                sample_index=1,
                target=0,
                stress_count=3,
                failure_stress_count=0,
                failure_frequency=0.0,
                flip_stress_count=0,
                flip_frequency=0.0,
                failed_stresses=[],
                flipped_stresses=[],
                severity="stable",
            ),
        ],
    )

    path = tmp_path / "sample-report.json"
    report.save_json(path)

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


def test_sample_report_cli_displays_report(
    tmp_path,
    capsys,
):
    report_path = build_report(
        tmp_path
    )

    exit_code = run_cli(
        [
            "sample-report",
            "--input",
            str(report_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Suite: production-vision" in captured.out
    assert "Samples analyzed: 2" in captured.out
    assert "Systemic: 1" in captured.out
    assert "Stable: 1" in captured.out
    assert "sample 0: systemic" in captured.out


def test_sample_report_cli_policy_passes(
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
                "maximum_systemic_samples": 1,
                "maximum_systemic_fraction": 0.50,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "sample-report",
            "--input",
            str(report_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "RESULT: PASSED" in captured.out


def test_sample_report_cli_policy_fails(
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
                "maximum_systemic_samples": 0,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "sample-report",
            "--input",
            str(report_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "systemic_samples" in captured.out
    assert "RESULT: FAILED" in captured.out


def test_sample_report_cli_missing_input_returns_two(
    tmp_path,
    capsys,
):
    exit_code = run_cli(
        [
            "sample-report",
            "--input",
            str(
                tmp_path / "missing.json"
            ),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "FailureLab error:" in captured.err