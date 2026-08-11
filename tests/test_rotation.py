from PIL import Image

from failurelab.rotation import RotationTest


def test_rotation_preserves_image_size():
    image = Image.new(
        "RGB",
        (20, 30),
        color=(200, 200, 200),
    )

    result = RotationTest(
        degrees=15
    ).apply(image)

    assert result.size == image.size


def test_rotation_keeps_original_unchanged():
    image = Image.new(
        "RGB",
        (20, 20),
        color=(200, 200, 200),
    )

    original_pixel = image.getpixel((0, 0))

    RotationTest(
        degrees=20
    ).apply(image)

    assert image.getpixel((0, 0)) == original_pixel