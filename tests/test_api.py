import numpy as np
from PIL import Image

from failurelab import FailureLab, FailureLabReport
from failurelab.stress_tests import BrightnessTest


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

    assert len(
        report.raw_results
    ) == 1

    assert report.weaknesses[0].name == "brightness"


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