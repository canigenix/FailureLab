import json

import numpy as np
from PIL import Image

from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.experiment import ExperimentRunner


def predict_proba(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness,
            1.0 - brightness,
        ]
    )


def test_experiment_runner_saves_result_and_history(tmp_path):
    config = SuiteConfig(
        name="production-vision",
        maximum_drop=0.50,
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

    result_path = tmp_path / "result.json"
    history_path = tmp_path / "history.json"

    runner = ExperimentRunner(
        predict_proba
    )

    output = runner.run(
        dataset=[
            (image, 0),
        ],
        config=config,
        result_path=result_path,
        history_path=history_path,
    )

    assert result_path.exists()
    assert history_path.exists()

    assert output.result_path == result_path
    assert output.history_path == history_path
    assert output.result.name == "production-vision"

    result_data = json.loads(
        result_path.read_text(
            encoding="utf-8"
        )
    )

    history_data = json.loads(
        history_path.read_text(
            encoding="utf-8"
        )
    )

    assert result_data["suite_name"] == "production-vision"
    assert len(history_data["entries"]) == 1

    assert (
        history_data["entries"][0]["suite_name"]
        == "production-vision"
    )


def test_experiment_runner_appends_history(tmp_path):
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

    result_path = tmp_path / "result.json"
    history_path = tmp_path / "history.json"

    runner = ExperimentRunner(
        predict_proba
    )

    dataset = [
        (image, 0),
    ]

    runner.run(
        dataset=dataset,
        config=config,
        result_path=result_path,
        history_path=history_path,
    )

    runner.run(
        dataset=dataset,
        config=config,
        result_path=result_path,
        history_path=history_path,
    )

    history_data = json.loads(
        history_path.read_text(
            encoding="utf-8"
        )
    )

    assert len(history_data["entries"]) == 2


def test_experiment_runner_records_model_metadata(tmp_path):
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

    result_path = tmp_path / "result.json"
    history_path = tmp_path / "history.json"

    runner = ExperimentRunner(
        predict_proba
    )

    output = runner.run(
        dataset=[(image, 0)],
        config=config,
        result_path=result_path,
        history_path=history_path,
        model_id="resnet18-v3",
        run_id="run-001",
    )

    result_data = json.loads(
        result_path.read_text(
            encoding="utf-8"
        )
    )

    history_data = json.loads(
        history_path.read_text(
            encoding="utf-8"
        )
    )

    assert output.model_id == "resnet18-v3"
    assert output.run_id == "run-001"

    assert result_data["model_id"] == "resnet18-v3"
    assert result_data["run_id"] == "run-001"

    assert (
        history_data["entries"][0]["model_id"]
        == "resnet18-v3"
    )

    assert (
        history_data["entries"][0]["run_id"]
        == "run-001"
    )