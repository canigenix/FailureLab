import json

import numpy as np
from PIL import Image

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


def test_configured_suite_runner_executes_all_stresses():
    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    dataset = [
        (image, 0),
    ]

    config = SuiteConfig(
        stresses=[
            StressSpec(
                type="blur",
                parameters={
                    "radius": 2.0,
                },
            ),
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.5,
                },
            ),
        ]
    )

    runner = ConfiguredSuiteRunner(
        predict_proba
    )

    result = runner.run(
        dataset=dataset,
        config=config,
    )

    assert result.count == 2
    assert len(result.results) == 2

    names = [
        stress_result.name
        for stress_result in result.results
    ]

    assert any(
        name.startswith("blur")
        for name in names
    )

    assert any(
        name.startswith("brightness")
        for name in names
    )


def test_suite_result_identifies_worst_stress():
    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    dataset = [
        (image, 0),
    ]

    config = SuiteConfig(
        stresses=[
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.9,
                },
            ),
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.2,
                },
            ),
        ]
    )

    runner = ConfiguredSuiteRunner(
        predict_proba
    )

    result = runner.run(
        dataset=dataset,
        config=config,
    )

    assert result.worst_result.name == "brightness_0.20"
    assert result.worst_drop > 0.0


def test_suite_result_saves_json(tmp_path):
    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    dataset = [
        (image, 0),
    ]

    config = SuiteConfig(
        stresses=[
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.5,
                },
            ),
        ]
    )

    runner = ConfiguredSuiteRunner(
        predict_proba
    )

    result = runner.run(
        dataset=dataset,
        config=config,
    )

    output_path = tmp_path / "suite_result.json"

    result.save_json(output_path)

    assert output_path.exists()

    saved = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert saved["stress_count"] == 1
    assert saved["worst_stress"] == "brightness_0.50"
    assert len(saved["results"]) == 1


def test_suite_result_preserves_suite_name():
    config = SuiteConfig(
        name="production-vision",
        stresses=[
            StressSpec(
                type="brightness",
                parameters={
                    "factor": 0.5,
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

    assert result.name == "production-vision"
    assert result.to_dict()["suite_name"] == "production-vision"


def test_suite_result_applies_maximum_drop_gate():
    config = SuiteConfig(
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

    assert result.passes(
        maximum_drop=1.0
    )

    assert not result.passes(
        maximum_drop=0.1
    )


def test_suite_result_uses_configured_maximum_drop():
    config = SuiteConfig(
        name="production-vision",
        maximum_drop=0.1,
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

    assert result.maximum_drop == 0.1
    assert result.status == "failed"
    assert result.to_dict()["status"] == "failed"