import json
import sys

import numpy as np
from PIL import Image

from failurelab.cli import main
from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.suite_runner import (
    ConfiguredSuiteRunner,
)


def predict_proba(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness,
            1.0 - brightness,
        ]
    )


def build_saved_result(tmp_path):
    config = SuiteConfig(
        name="production-vision",
        maximum_drop=1.0,
        stresses=[
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.2,
                },
            ),
        ],
    )

    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    runner = ConfiguredSuiteRunner(
        predict_proba
    )

    result = runner.run(
        dataset=[(image, 0)],
        config=config,
    )

    result_path = tmp_path / "result.json"
    result.save_json(result_path)

    return result_path


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


def test_policy_evaluate_passes(
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
                "maximum_top1_drop": 1.0,
                "maximum_top5_drop": 1.0,
                "maximum_confidence_drop": 1.0,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "policy-evaluate",
            "--result",
            str(result_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Suite: production-vision" in captured.out
    assert "Policy status: passed" in captured.out
    assert "RESULT: PASSED" in captured.out


def test_policy_evaluate_fails_policy(
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
                "maximum_top1_drop": 0.01,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "policy-evaluate",
            "--result",
            str(result_path),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Policy status: failed" in captured.out
    assert "RESULT: FAILED" in captured.out
    assert "brightness" in captured.out


def test_policy_evaluate_invalid_input_returns_two(
    tmp_path,
    capsys,
):
    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_top1_drop": 0.20,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(
        [
            "policy-evaluate",
            "--result",
            str(
                tmp_path / "missing.json"
            ),
            "--policy",
            str(policy_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "FailureLab error:" in captured.err