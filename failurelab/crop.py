from __future__ import annotations
from dataclasses import dataclass
from PIL import Image

@dataclass(frozen=True)
class CenterCropTest:
    fraction: float
    def __post_init__(self):
        if not 0.0 < self.fraction <= 1.0:
            raise ValueError("crop fraction must be greater than 0 and at most 1.")
    @property
    def name(self) -> str:
        return f"crop_{self.fraction:.2f}"
    def apply(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        crop_width = max(1, int(width * self.fraction))
        crop_height = max(1, int(height * self.fraction))
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        cropped = image.crop((left, top, left + crop_width, top + crop_height))
        return cropped.resize((width, height), resample=Image.Resampling.BILINEAR)
