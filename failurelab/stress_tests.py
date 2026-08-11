"""Image stress tests."""
from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageEnhance

@dataclass(frozen=True)
class BrightnessTest:
    factor: float
    def __post_init__(self):
        if self.factor <= 0:
            raise ValueError("brightness factor must be greater than zero.")
    @property
    def name(self) -> str:
        return f"brightness_{self.factor:.2f}"
    def apply(self, image: Image.Image) -> Image.Image:
        return ImageEnhance.Brightness(image).enhance(self.factor)
