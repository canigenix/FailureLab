import numpy as np
from PIL import Image

from failurelab.stress_tests import BrightnessTest
from failurelab.vision_runner import VisionStressRunner


def test_vision_runner_detects_confidence_drop():
    def predict_proba_fn(image):
        pixel = image.getpixel((0, 0))[0]

        if pixel >= 100:
            return np.array(
                [0.10, 0.90]
            )

        return np.array(
            [0.45, 0.55]
        )

    dataset = [
        (
            Image.new(
                "RGB",
                (2, 2),
                color=(200, 200, 200),
            ),
            1,
        ),
    ]

    runner = VisionStressRunner(
        predict_proba_fn
    )

    result = runner.run(
        dataset=dataset,
        stress_test=BrightnessTest(
            factor=0.4
        ),
    )

    assert result.baseline.top1_accuracy == 1.0
    assert result.stressed.top1_accuracy == 1.0

    assert result.target_confidence_drop == 0.35