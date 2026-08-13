from PIL import Image

from failurelab.custom_stress import CustomStressTest


class InvertStress(CustomStressTest):
    @property
    def name(self) -> str:
        return "invert"

    def apply(self, image: Image.Image) -> Image.Image:
        return Image.eval(image, lambda value: 255 - value)


def test_custom_stress_test_can_be_implemented():
    stress = InvertStress()

    image = Image.new(
        "L",
        (1, 1),
        color=100,
    )

    stressed = stress.apply(image)

    assert stress.name == "invert"
    assert stressed.getpixel((0, 0)) == 155


import numpy as np

from failurelab.vision_runner import VisionStressRunner


def test_custom_stress_test_runs_through_vision_runner():
    def predict_proba(image):
        value = image.getpixel((0, 0))

        if value < 128:
            return np.array([0.9, 0.1])

        return np.array([0.1, 0.9])

    dataset = [
        (
            Image.new("L", (1, 1), color=100),
            0,
        )
    ]

    runner = VisionStressRunner(predict_proba)

    result = runner.run(
        dataset=dataset,
        stress_test=InvertStress(),
    )

    assert result.name == "invert"
    assert result.baseline.top1_accuracy == 1.0
    assert result.stressed.top1_accuracy == 0.0
    assert result.top1_drop == 1.0