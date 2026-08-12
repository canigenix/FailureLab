import numpy as np
import pytest

from PIL import Image

from failurelab import FailureLab


def predict_proba_fn(image):
    pixel = image.getpixel(
        (0, 0)
    )[0]

    if pixel >= 100:
        return np.array(
            [0.10, 0.90]
        )

    return np.array(
        [0.90, 0.10]
    )


def make_dataset():
    return [
        (
            Image.new(
                "RGB",
                (8, 8),
                color=(200, 200, 200),
            ),
            1,
        )
    ]


def test_public_api_can_run_brightness_sweep():
    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=make_dataset(),
    )

    result = lab.sweep(
        "brightness"
    )

    assert result.name == "brightness"
    assert len(result.points) == 5

    assert (
        result.points[0].severity_value
        == 0.90
    )


def test_public_api_sweep_detects_failure_threshold():
    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=make_dataset(),
    )

    result = lab.sweep(
        "brightness"
    )

    assert (
        result.failure_threshold
        is not None
    )

    assert result.worst_top1_drop > 0.0


def test_public_api_rejects_unknown_sweep():
    lab = FailureLab(
        predict_proba_fn=predict_proba_fn,
        dataset=make_dataset(),
    )

    with pytest.raises(
        ValueError
    ):
        lab.sweep(
            "earthquake"
        )