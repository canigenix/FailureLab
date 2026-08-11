from failurelab.ranking import WeaknessRanker
from failurelab.runner import StressTestResult
from failurelab.sweeps import SweepResult


def test_ranker_orders_largest_accuracy_drop_first():
    brightness = SweepResult(
        test_name="brightness",
        results=[
            StressTestResult(
                name="brightness_0.50",
                baseline_accuracy=0.90,
                stressed_accuracy=0.70,
            ),
        ],
    )

    blur = SweepResult(
        test_name="blur",
        results=[
            StressTestResult(
                name="blur_3.00",
                baseline_accuracy=0.90,
                stressed_accuracy=0.50,
            ),
        ],
    )

    ranker = WeaknessRanker()

    weaknesses = ranker.rank(
        [
            brightness,
            blur,
        ]
    )

    assert weaknesses[0].name == "blur"
    assert weaknesses[0].severity == "critical"
    assert weaknesses[0].accuracy_drop == 0.40
    assert weaknesses[0].stress_level == "blur_3.00"

    assert weaknesses[1].name == "brightness"