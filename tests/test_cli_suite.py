import json
import sys

from failurelab.cli import main


def test_suite_command_loads_config(tmp_path, capsys):
    config_path = tmp_path / "suite.json"

    config_path.write_text(
        json.dumps(
            {
                "stresses": [
                    {
                        "type": "blur",
                        "radius": 2.0,
                    },
                    {
                        "type": "brightness",
                        "factor": 0.5,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "failurelab",
            "suite",
            "--config",
            str(config_path),
        ]

        exit_code = main()

    finally:
        sys.argv = original_argv

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Loaded 2 configured stress test(s)." in captured.out
    assert "blur_2.00" in captured.out
    assert "brightness_0.50" in captured.out