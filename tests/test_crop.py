import pytest
from PIL import Image

from failurelab.crop import CenterCropTest


def test_crop_preserves_image_size():
    image = Image.new(
        "RGB",
        (20, 30),
        color=(200, 200, 200),
    )

    result = CenterCropTest(
        fraction=0.75
    ).apply(image)

    assert result.size == image.size


def test_crop_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(200, 200, 200),
    )

    original_size = image.size

    CenterCropTest(
        fraction=0.50
    ).apply(image)

    assert image.size == original_size


def test_crop_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        CenterCropTest(
            fraction=0
        )