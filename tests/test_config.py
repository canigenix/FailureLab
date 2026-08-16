import json

from failurelab.config import (
    build_stress_tests,
    load_suite_config,
)


def test_load_suite_config(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "stresses": [
                    {
                        "type": "blur",
                        "radius": 3.0,
                    },
                    {
                        "type": "rotation",
                        "degrees": 20,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    config = load_suite_config(path)

    assert len(config.stresses) == 2
    assert config.stresses[0].type == "blur"
    assert config.stresses[0].parameters["radius"] == 3.0
    assert config.stresses[1].type == "rotation"


def test_build_stress_tests(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "stresses": [
                    {
                        "type": "blur",
                        "radius": 2.0,
                    },
                    {
                        "type": "rotation",
                        "degrees": 15,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    config = load_suite_config(path)
    stress_tests = build_stress_tests(config)

    assert len(stress_tests) == 2
    assert stress_tests[0].name.startswith("blur")
    assert stress_tests[1].name.startswith("rotation")


def test_build_stress_tests_rejects_unknown_type(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "stresses": [
                    {
                        "type": "does_not_exist",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    config = load_suite_config(path)

    try:
        build_stress_tests(config)
    except ValueError as exc:
        assert "unknown stress type" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown stress type to raise ValueError."
        )


def test_load_suite_config_rejects_empty_stresses(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "stresses": []
            }
        ),
        encoding="utf-8",
    )

    try:
        load_suite_config(path)
    except ValueError as exc:
        assert "non-empty 'stresses' list" in str(exc)
    else:
        raise AssertionError(
            "Expected empty stress list to raise ValueError."
        )


def test_load_suite_config_reads_suite_name(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "name": "production-vision",
                "stresses": [
                    {
                        "type": "blur",
                        "radius": 2.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_suite_config(path)

    assert config.name == "production-vision"


def test_load_suite_config_reads_maximum_drop(tmp_path):
    path = tmp_path / "suite.json"

    path.write_text(
        json.dumps(
            {
                "name": "production-vision",
                "maximum_drop": 0.20,
                "stresses": [
                    {
                        "type": "blur",
                        "radius": 2.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_suite_config(path)

    assert config.maximum_drop == 0.20