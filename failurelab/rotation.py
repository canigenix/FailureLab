from __future__ import annotations
from dataclasses import dataclass
from PIL import Image

@dataclass(frozen=True)
class RotationTest:
    degrees: float
    @property
    def name(self) -> str:
        return f"rotation_{self.degrees:.1f}"
    def apply(self, image: Image.Image) -> Image.Image:
        return image.rotate(self.degrees, resample=Image.Resampling.BILINEAR, expand=False)
