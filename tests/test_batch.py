import json

import numpy as np
from PIL import Image

from failurelab.batch import (
    BatchExperiment,
    BatchExperimentRunner,
)
from failurelab.config import (
    StressSpec,
    SuiteConfig,
)


def predict_proba_a(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness,
            1.0 - brightness,
        ]
    )


def predict_proba_b(image):
    brightness = np.asarray(image).mean() / 255.0

    return np.array(
        [
            brightness * 0.9,
            1.0 - (brightness * 0.9),
        ]
    )


def build_dataset():
    image = Image.new(
        "RGB",
        (16, 16),
        color=(200, 200, 200),
    )

    return [
        (image, 0),
    ]


def build_config():
    return SuiteConfig(
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


def test_batch_runner_executes_multiple_experiments(
    tmp_path,
):
    dataset = build_dataset()
    config = build_config()

    experiments = [
        BatchExperiment(
            model_id="model-a",
            predict_proba_fn=predict_proba_a,
            dataset=dataset,
            config=config,
            result_path=tmp_path / "model-a.json",
            history_path=tmp_path / "history.json",
            run_id="run-a",
        ),
        BatchExperiment(
            model_id="model-b",
            predict_proba_fn=predict_proba_b,
            dataset=dataset,
            config=config,
            result_path=tmp_path / "model-b.json",
            history_path=tmp_path / "history.json",
            run_id="run-b",
        ),
    ]

    runner = BatchExperimentRunner()

    output = runner.run(
        experiments
    )

    assert output.count == 2

    assert (
        tmp_path / "model-a.json"
    ).exists()

    assert (
        tmp_path / "model-b.json"
    ).exists()

    history = json.loads(
        (
            tmp_path / "history.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert len(history["entries"]) == 2

    model_ids = {
        entry["model_id"]
        for entry in history["entries"]
    }

    assert model_ids == {
        "model-a",
        "model-b",
    }


def test_batch_runner_rejects_empty_batch():
    runner = BatchExperimentRunner()

    try:
        runner.run([])
    except ValueError as exc:
        assert "at least one experiment" in str(exc)
    else:
        raise AssertionError(
            "Expected empty batch to raise ValueError."
        )


def test_batch_output_saves_summary_json(
    tmp_path,
):
    dataset = build_dataset()
    config = build_config()

    experiments = [
        BatchExperiment(
            model_id="model-a",
            predict_proba_fn=predict_proba_a,
            dataset=dataset,
            config=config,
            result_path=tmp_path / "model-a.json",
            history_path=tmp_path / "history.json",
            run_id="run-a",
        ),
        BatchExperiment(
            model_id="model-b",
            predict_proba_fn=predict_proba_b,
            dataset=dataset,
            config=config,
            result_path=tmp_path / "model-b.json",
            history_path=tmp_path / "history.json",
            run_id="run-b",
        ),
    ]

    runner = BatchExperimentRunner()

    output = runner.run(
        experiments
    )

    summary_path = tmp_path / "batch.json"

    output.save_json(
        summary_path
    )

    assert summary_path.exists()

    saved = json.loads(
        summary_path.read_text(
            encoding="utf-8"
        )
    )

    assert saved["experiment_count"] == 2

    assert saved["status"] in {
        "passed",
        "failed",
        "not_evaluated",
    }

    assert len(
        saved["experiments"]
    ) == 2

    assert saved["experiments"][0]["model_id"] == "model-a"
    assert saved["experiments"][1]["model_id"] == "model-b"