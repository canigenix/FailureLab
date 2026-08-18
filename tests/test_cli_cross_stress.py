import json
import sys

from failurelab.class_analysis import (
    ClassRobustnessResult,
)
from failurelab.cli import main
from failurelab.suite_runner import (
    SavedStressResult,
    SuiteResult,
)


def class_result(
    class_index,
    accuracy_drop,
    failure_rate,
):
    return ClassRobustnessResult(
        class_index=class_index,
        sample_count=10,
        baseline_accuracy=1.0,
        stressed_accuracy=(
            1.0 - accuracy_drop
        ),
        accuracy_drop=accuracy_drop,
        baseline_confidence=0.9,
        stressed_confidence=0.8,
        confidence_drop=0.1,
        stressed_failure_rate=failure_rate,
        prediction_flip_rate=failure_rate,
        top_confusion_class=None,
        top_confusion_rate=0.0,
    )


def build_saved_result(tmp_path):
    result = SuiteResult(
        name="production-vision",
        results=[
            SavedStressResult(
                name="blur",
                top1_drop=0.4,
                top5_drop=0.0,
                target_confidence_drop=0.1,
                class_results=[
                    class_result(
                        0,
                        0.5,
                        0.5,
                    ),
                    class_result(
                        1,
                        0.0,
                        0.0,
                    ),
                ],
            ),
            SavedStressResult(
                name="brightness",
                top1_drop=0.3,
                top5_drop=0.0,
                target_confidence_drop=0.1,
                class_results=[
                    class_result(
                        0,
                        0.4,
                        0.4,
                    ),
                    class_result(
                        1,
                        0.0,
                        0.0,
                    ),
                ],
            ),
        ],
    )

    path = tmp_path / "suite-result.json"

    result.save_json(
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


def test_cross_stress_cli_reports_analysis(
    tmp_path,
    capsys,
):
    result_path = build_saved_result(
        tmp_path
    )

    exit_code = run_cli(
        [
            "cross-stress",
            "--result",
            str(result_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Suite: production-vision" in captured.out
    assert "Classes analyzed: 2" in captured.out
    assert "Systemic: 1" in captured.out
    assert "Stable: 1" in captured.out
    assert "class 0: systemic" in captured.out


def test_cross_stress_cli_saves_report(
    tmp_path,
):
    result_path = build_saved_result(
        tmp_path
    )

    output_path = tmp_path / "cross-stress.json"

    exit_code = run_cli(
        [
            "cross-stress",
            "--result",
            str(result_path),
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

    assert data["suite_name"] == "production-vision"
    assert data["systemic_count"] == 1


def test_cross_stress_cli_policy_passes(
    tmp_path,
    capsys,
):
    result_path = build_saved_result(
        tmp_path
    )

    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_systemic_classes": 1,
                "maximum_systemic_fraction": 0.50,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "cross-stress",
            "--result",
            str(result_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "RESULT: PASSED" in captured.out


def test_cross_stress_cli_policy_fails(
    tmp_path,
    capsys,
):
    result_path = build_saved_result(
        tmp_path
    )

    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_systemic_classes": 0,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "cross-stress",
            "--result",
            str(result_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "systemic_classes" in captured.out
    assert "RESULT: FAILED" in captured.out


def test_cross_stress_cli_invalid_input_returns_two(
    tmp_path,
    capsys,
):
    exit_code = run_cli(
        [
            "cross-stress",
            "--result",
            str(
                tmp_path / "missing.json"
            ),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "FailureLab error:" in captured.err