import json
import sys

import numpy as np
from PIL import Image

from failurelab.cli import main
from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.suite_runner import ConfiguredSuiteRunner


def predict_proba(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness,
            1.0 - brightness,
        ]
    )


def test_policy_evaluate_reports_class_warning(
    tmp_path,
    capsys,
):
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

    result = ConfiguredSuiteRunner(
        predict_proba
    ).run(
        dataset=[(image, 0)],
        config=config,
    )

    result_path = tmp_path / "result.json"
    result.save_json(result_path)

    policy_path = tmp_path / "policy.json"

    policy_path.write_text(
        json.dumps(
            {
                "maximum_top1_drop": 1.0,
            }
        ),
        encoding="utf-8",
    )

    class_policy_path = (
        tmp_path / "class-policy.json"
    )

    class_policy_path.write_text(
        json.dumps(
            {
                "default": {
                    "warning_failure_rate": 0.01,
                    "maximum_failure_rate": 1.0,
                }
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            "policy-evaluate",
            "--result",
            str(result_path),
            "--policy",
            str(policy_path),
            "--class-policy",
            str(class_policy_path),
        ]

        exit_code = main()

    finally:
        sys.argv = original_argv

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Class policy status: warning" in captured.out
    assert "WARNING class 0" in captured.out
    assert "stressed_failure_rate" in captured.out
    assert "RESULT: PASSED WITH WARNINGS" in captured.out