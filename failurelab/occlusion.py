from __future__ import annotations
from dataclasses import dataclass
from PIL import Image, ImageDraw

@dataclass(frozen=True)
class OcclusionTest:
    fraction: float = 0.25
    def __post_init__(self):
        if not 0.0 < self.fraction < 1.0:
            raise ValueError("occlusion fraction must be between 0 and 1.")
    @property
    def name(self) -> str:
        return f"occlusion_{self.fraction:.2f}"
    def apply(self, image: Image.Image) -> Image.Image:
        result = image.copy()
        width, height = result.size
        ow = max(1, int(width * self.fraction))
        oh = max(1, int(height * self.fraction))
        left = (width - ow) // 2
        top = (height - oh) // 2
        draw = ImageDraw.Draw(result)
        draw.rectangle((left, top, left + ow, top + oh), fill=(0, 0, 0))
        return result
