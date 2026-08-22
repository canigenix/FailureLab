import subprocess
import sys


EXPECTED_COMMANDS = {
    "check",
    "compare",
    "visualize",
    "suite",
    "history",
    "policy-evaluate",
    "cross-stress",
    "sample-report",
    "correlation",
    "clusters",
    "progression",
    "signature",
    "signature-history",
    "triage",
    "triage-compare",
    "persistence",
    "resolution",
    "forecast",
    "evaluate",
}


def run_cli(*args):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "failurelab.cli",
            *args,
        ],
        capture_output=True,
        text=True,
    )

    return result


def test_v1_cli_help_succeeds():
    result = run_cli(
        "--help"
    )

    assert result.returncode == 0

    assert (
        "Stress-test machine-learning models"
        in result.stdout
    )


def test_v1_cli_exposes_all_frozen_commands():
    result = run_cli(
        "--help"
    )

    assert result.returncode == 0

    for command in EXPECTED_COMMANDS:
        assert command in result.stdout


def test_v1_cli_command_count():
    assert len(
        EXPECTED_COMMANDS
    ) == 19


def test_v1_cli_version_flag_succeeds():
    result = run_cli(
        "--version"
    )

    assert result.returncode == 0

    assert "failurelab" in result.stdout.lower()


def test_v1_evaluate_help_contract():
    result = run_cli(
        "evaluate",
        "--help",
    )

    assert result.returncode == 0

    assert "--config" in result.stdout
    assert "--output" in result.stdout
    assert "--gate-config" in result.stdout


def test_v1_forecast_help_contract():
    result = run_cli(
        "forecast",
        "--help",
    )

    assert result.returncode == 0

    assert "--input" in result.stdout
    assert "--output" in result.stdout


def test_v1_resolution_help_contract():
    result = run_cli(
        "resolution",
        "--help",
    )

    assert result.returncode == 0

    assert "--input" in result.stdout
    assert "--tolerance" in result.stdout


def test_v1_progression_help_contract():
    result = run_cli(
        "progression",
        "--help",
    )

    assert result.returncode == 0

    assert "--input" in result.stdout


def test_v1_signature_help_contract():
    result = run_cli(
        "signature",
        "--help",
    )

    assert result.returncode == 0

    assert "--input" in result.stdout


def test_v1_triage_help_contract():
    result = run_cli(
        "triage",
        "--help",
    )

    assert result.returncode == 0

    assert "--input" in result.stdout