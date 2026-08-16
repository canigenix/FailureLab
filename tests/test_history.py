import json

import numpy as np
from PIL import Image

from failurelab.config import (
    StressSpec,
    SuiteConfig,
)
from failurelab.history import (
    HistoryEntry,
    SuiteHistory,
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


def build_result():
    config = SuiteConfig(
        name="production-vision",
        maximum_drop=0.2,
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

    return runner.run(
        dataset=[(image, 0)],
        config=config,
    )


def test_suite_history_adds_result():
    history = SuiteHistory()

    entry = history.add_result(
        build_result()
    )

    assert len(history.entries) == 1
    assert entry.suite_name == "production-vision"
    assert entry.worst_stress == "brightness_0.50"


def test_suite_history_saves_and_loads_json(tmp_path):
    history = SuiteHistory()

    history.add_result(
        build_result()
    )

    path = tmp_path / "history.json"

    history.save_json(path)

    assert path.exists()

    saved = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert len(saved["entries"]) == 1

    loaded = SuiteHistory.load_json(path)

    assert len(loaded.entries) == 1
    assert loaded.entries[0].suite_name == "production-vision"


def test_suite_history_detects_regression():
    history = SuiteHistory(
        entries=[
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T10:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.10,
                maximum_drop=0.20,
            ),
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T11:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.16,
                maximum_drop=0.20,
            ),
        ]
    )

    assert history.trend("production-vision") == "regressed"


def test_suite_history_detects_improvement():
    history = SuiteHistory(
        entries=[
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T10:00:00+00:00",
                status="failed",
                worst_stress="blur_2.00",
                worst_drop=0.30,
                maximum_drop=0.20,
            ),
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T11:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.15,
                maximum_drop=0.20,
            ),
        ]
    )

    assert history.trend("production-vision") == "improved"


def test_suite_history_queries_by_model():
    history = SuiteHistory(
        entries=[
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T10:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.10,
                maximum_drop=0.20,
                model_id="resnet18-v1",
                run_id="run-001",
            ),
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T11:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.12,
                maximum_drop=0.20,
                model_id="mobilenet-v1",
                run_id="run-002",
            ),
        ]
    )

    entries = history.entries_for_model(
        "resnet18-v1"
    )

    assert len(entries) == 1
    assert entries[0].run_id == "run-001"

    latest = history.latest_for_model(
        "resnet18-v1"
    )

    assert latest is not None
    assert latest.model_id == "resnet18-v1"


def test_suite_history_detects_model_regression():
    history = SuiteHistory(
        entries=[
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T10:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.10,
                maximum_drop=0.20,
                model_id="resnet18-v3",
                run_id="run-001",
            ),
            HistoryEntry(
                suite_name="production-vision",
                timestamp="2026-08-16T11:00:00+00:00",
                status="passed",
                worst_stress="blur_2.00",
                worst_drop=0.18,
                maximum_drop=0.20,
                model_id="resnet18-v3",
                run_id="run-002",
            ),
        ]
    )

    assert (
        history.model_trend("resnet18-v3")
        == "regressed"
    )