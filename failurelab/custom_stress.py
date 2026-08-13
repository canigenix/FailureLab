from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class CustomStressTest(ABC):
    """Base class for user-defined image stress tests."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the stress test."""
        raise NotImplementedError

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply the stress transformation to an image."""
        raise NotImplementedError