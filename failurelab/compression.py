from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from PIL import Image

@dataclass(frozen=True)
class CompressionTest:
    quality: int
    def __post_init__(self):
        if not 1 <= self.quality <= 100:
            raise ValueError("JPEG quality must be between 1 and 100.")
    @property
    def name(self) -> str:
        return f"jpeg_{self.quality}"
    def apply(self, image: Image.Image) -> Image.Image:
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=self.quality)
        buffer.seek(0)
        result = Image.open(buffer).convert("RGB")
        result.load()
        return result
