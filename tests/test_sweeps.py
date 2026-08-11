from PIL import Image

from failurelab.runner import StressTestRunner
from failurelab.sweeps import (
    BlurSweep,
    BrightnessSweep,
)


def test_brightness_sweep_finds_breaking_point():
    def predict_fn(image):
        pixel = image.getpixel((0, 0))[0]
        return 1 if pixel >= 100 else 0

    dataset = [
        (
            Image.new(
                "RGB",
                (2, 2),
                color=(200, 200, 200),
            ),
            1,
        ),
        (
            Image.new(
                "RGB",
                (2, 2),
                color=(180, 180, 180),
            ),
            1,
        ),
    ]

    runner = StressTestRunner(predict_fn)

    sweep = BrightnessSweep(
        factors=[
            0.90,
            0.60,
            0.40,
        ]
    )

    result = sweep.run(
        runner,
        dataset,
    )

    assert len(result.results) == 3

    first_failure = result.first_failure(
        minimum_drop=0.50
    )

    assert first_failure is not None
    assert first_failure.name == "brightness_0.40"
    assert first_failure.accuracy_drop == 1.0


def test_brightness_sweep_identifies_worst_result():
    def predict_fn(image):
        pixel = image.getpixel((0, 0))[0]
        return 1 if pixel >= 100 else 0

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

    runner = StressTestRunner(predict_fn)

    sweep = BrightnessSweep(
        factors=[
            0.90,
            0.60,
            0.30,
        ]
    )

    result = sweep.run(
        runner,
        dataset,
    )

    worst = result.worst_result()

    assert worst.name == "brightness_0.30"
    assert worst.stressed_accuracy == 0.0


def test_blur_sweep_runs_all_levels():
    def predict_fn(image):
        return 1

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

    runner = StressTestRunner(predict_fn)

    sweep = BlurSweep(
        radii=[
            0.5,
            1.0,
            2.0,
        ]
    )

    result = sweep.run(
        runner,
        dataset,
    )

    assert result.test_name == "blur"
    assert len(result.results) == 3

    assert result.results[0].name == "blur_0.50"
    assert result.results[1].name == "blur_1.00"
    assert result.results[2].name == "blur_2.00"


def test_sweep_severity_uses_worst_result():
    def predict_fn(image):
        pixel = image.getpixel((0, 0))[0]
        return 1 if pixel >= 100 else 0

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

    runner = StressTestRunner(predict_fn)

    sweep = BrightnessSweep(
        factors=[
            0.90,
            0.30,
        ]
    )

    result = sweep.run(
        runner,
        dataset,
    )

    assert result.severity() == "critical"