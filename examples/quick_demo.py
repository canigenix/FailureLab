from PIL import Image

from failurelab.diagnostics import diagnose_model


def predict_fn(image):
    """
    Tiny demo classifier.

    Bright images are treated as class 1 and darker images as class 0.
    This is intentionally simple so we can predict how the stress tests
    should affect it.
    """
    pixel = image.getpixel((0, 0))[0]

    return 1 if pixel >= 100 else 0


dataset = [
    (
        Image.new(
            "RGB",
            (20, 20),
            color=(220, 220, 220),
        ),
        1,
    ),
    (
        Image.new(
            "RGB",
            (20, 20),
            color=(200, 200, 200),
        ),
        1,
    ),
    (
        Image.new(
            "RGB",
            (20, 20),
            color=(180, 180, 180),
        ),
        1,
    ),
]


report = diagnose_model(
    predict_fn=predict_fn,
    dataset=dataset,
)

print(report)