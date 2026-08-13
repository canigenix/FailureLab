import json
import sys

from failurelab.cli import main


def test_visualize_command_creates_png(tmp_path):
    input_path = tmp_path / "weaknesses.json"
    output_path = tmp_path / "robustness.png"

    input_path.write_text(
        json.dumps(
            {
                "weaknesses": [
                    {
                        "name": "blur",
                        "severity": "high",
                        "top1_drop": 0.20,
                        "top5_drop": 0.10,
                        "confidence_drop": 0.15,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            "visualize",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ]

        exit_code = main()

    finally:
        sys.argv = original_argv

    assert exit_code == 0
    assert output_path.exists()
    assert output_path.stat().st_size > 0