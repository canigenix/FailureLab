import pytest
from PIL import Image

from failurelab.compression import CompressionTest


def test_compression_preserves_image_size():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(150, 100, 50),
    )

    result = CompressionTest(
        quality=40
    ).apply(image)

    assert result.size == image.size


def test_compression_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(150, 100, 50),
    )

    original_pixel = image.getpixel((0, 0))

    CompressionTest(
        quality=20
    ).apply(image)

    assert image.getpixel((0, 0)) == original_pixel


def test_compression_rejects_invalid_quality():
    with pytest.raises(ValueError):
        CompressionTest(
            quality=0
        )