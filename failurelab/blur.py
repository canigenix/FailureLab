from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageFilter

@dataclass(frozen=True)
class BlurTest:
    radius: float
    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("blur radius cannot be negative.")
    @property
    def name(self) -> str:
        return f"blur_{self.radius:.2f}"
    def apply(self, image: Image.Image) -> Image.Image:
        return image.filter(ImageFilter.GaussianBlur(radius=self.radius))
