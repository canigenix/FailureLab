import pytest
from PIL import Image

from failurelab.stress_tests import BrightnessTest


def test_brightness_test_darkens_image():
    image = Image.new(
        "RGB",
        (2, 2),
        color=(200, 200, 200),
    )

    test = BrightnessTest(
        factor=0.5
    )

    result = test.apply(image)

    pixel = result.getpixel(
        (0, 0)
    )

    assert pixel[0] < 200
    assert pixel[1] < 200
    assert pixel[2] < 200


def test_brightness_test_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (2, 2),
        color=(200, 200, 200),
    )

    original_pixel = image.getpixel(
        (0, 0)
    )

    BrightnessTest(
        factor=0.5
    ).apply(image)

    assert image.getpixel(
        (0, 0)
    ) == original_pixel


def test_brightness_test_rejects_invalid_factor():
    with pytest.raises(ValueError):
        BrightnessTest(
            factor=0
        )