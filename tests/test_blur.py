import pytest
from PIL import Image

from failurelab.blur import BlurTest


def test_blur_test_preserves_image_size():
    image = Image.new(
        "RGB",
        (10, 10),
        color=(200, 200, 200),
    )

    result = BlurTest(
        radius=2.0
    ).apply(image)

    assert result.size == image.size


def test_blur_test_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (10, 10),
        color=(200, 200, 200),
    )

    original_pixel = image.getpixel(
        (0, 0)
    )

    BlurTest(
        radius=2.0
    ).apply(image)

    assert image.getpixel(
        (0, 0)
    ) == original_pixel


def test_blur_test_rejects_negative_radius():
    with pytest.raises(ValueError):
        BlurTest(
            radius=-1
        )