import json

import numpy as np
from PIL import Image

from failurelab import FailureLab, FailureLabReport
from failurelab.stress_tests import BrightnessTest
from tests.test_snapshot import make_report


def test_failurelab_public_api_runs():
    def predict_proba_fn(image):
        pixel = image.getpixel((0, 0))[0]

        if pixel >= 100:
            return np.array(
                [0.10, 0.90]
            )

        return np.array(
            [0.80, 0.20]
        )

    dataset = [
        (
            Image.new(
                "RGB",
                (10, 10),
                color=(200, 200, 200),
            ),
            1,
        ),
    ]

    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=dataset,
    )

    report = lab.run(
        stress_tests=[
            BrightnessTest(
                factor=0.40
            )
        ]
    )

    assert isinstance(
        report,
        FailureLabReport,
    )

    assert len(report.raw_results) == 1
    assert report.weaknesses[0].name == "brightness"

    assert report.robustness_score.score >= 0.0
    assert report.robustness_score.score <= 100.0
    assert report.robustness_score.grade
    assert report.robustness_score.status


def test_failurelab_report_contains_recommendations():
    def predict_proba_fn(image):
        pixel = image.getpixel((0, 0))[0]

        if pixel >= 100:
            return np.array(
                [0.05, 0.95]
            )

        return np.array(
            [0.95, 0.05]
        )

    dataset = [
        (
            Image.new(
                "RGB",
                (10, 10),
                color=(200, 200, 200),
            ),
            1,
        ),
    ]

    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=dataset,
    )

    report = lab.run(
        stress_tests=[
            BrightnessTest(
                factor=0.40
            )
        ]
    )

    assert len(report.recommendations) == 1

    recommendation = report.recommendations[0]

    assert recommendation.weakness_name == "brightness"
    assert recommendation.diagnosis
    assert recommendation.likely_cause
    assert recommendation.suggested_action


def test_failurelab_report_exports(tmp_path):
    def predict_proba_fn(image):
        return np.array(
            [0.10, 0.90]
        )

    dataset = [
        (
            Image.new(
                "RGB",
                (10, 10),
                color=(200, 200, 200),
            ),
            1,
        ),
    ]

    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=dataset,
    )

    report = lab.run(
        stress_tests=[
            BrightnessTest(
                factor=0.50
            )
        ]
    )

    json_path = report.save_json(
        tmp_path / "report.json"
    )

    html_path = report.save_html(
        tmp_path / "report.html"
    )

    assert json_path.exists()
    assert html_path.exists()


def test_report_save_snapshot(tmp_path):
    report = make_report()

    path = report.save_snapshot(
        tmp_path / "report_snapshot.json"
    )

    assert path.exists()

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert data["format"] == "failurelab_snapshot"
    assert data["score"] == 75.0
    assert len(data["boundaries"]) == 2