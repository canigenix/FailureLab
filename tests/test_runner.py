from PIL import Image

from failurelab.runner import StressTestResult, StressTestRunner
from failurelab.stress_tests import BrightnessTest


def test_runner_detects_accuracy_drop():
    def predict_fn(image):
        pixel = image.getpixel((0, 0))[0]

        # Toy classifier used only to make the expected result predictable.
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

    result = runner.run(
        dataset=dataset,
        stress_test=BrightnessTest(factor=0.4),
    )

    assert result.baseline_accuracy == 1.0
    assert result.stressed_accuracy == 0.0
    assert result.accuracy_drop == 1.0


def test_runner_reports_no_drop_when_model_is_stable():
    def predict_fn(image):
        return 1

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
                color=(50, 50, 50),
            ),
            1,
        ),
    ]

    runner = StressTestRunner(predict_fn)

    result = runner.run(
        dataset=dataset,
        stress_test=BrightnessTest(factor=0.5),
    )

    assert result.baseline_accuracy == 1.0
    assert result.stressed_accuracy == 1.0
    assert result.accuracy_drop == 0.0


def test_stress_result_severity():
    critical = StressTestResult(
        name="test",
        baseline_accuracy=0.90,
        stressed_accuracy=0.60,
    )

    medium = StressTestResult(
        name="test",
        baseline_accuracy=0.90,
        stressed_accuracy=0.82,
    )

    low = StressTestResult(
        name="test",
        baseline_accuracy=0.90,
        stressed_accuracy=0.88,
    )

    assert critical.severity == "critical"
    assert medium.severity == "medium"
    assert low.severity == "low"