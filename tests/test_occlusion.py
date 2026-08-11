import pytest
from PIL import Image

from failurelab.occlusion import OcclusionTest


def test_occlusion_preserves_image_size():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(200, 200, 200),
    )

    result = OcclusionTest(
        fraction=0.25
    ).apply(image)

    assert result.size == image.size


def test_occlusion_changes_center_pixel():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(200, 200, 200),
    )

    result = OcclusionTest(
        fraction=0.25
    ).apply(image)

    assert result.getpixel((10, 10)) == (0, 0, 0)


def test_occlusion_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(200, 200, 200),
    )

    OcclusionTest(
        fraction=0.25
    ).apply(image)

    assert image.getpixel((10, 10)) == (
        200,
        200,
        200,
    )


def test_occlusion_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        OcclusionTest(
            fraction=1.0
        )