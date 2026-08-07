from __future__ import annotations

from abc import ABC, abstractmethod

from core.imageModel import ImageModel


class ImageFilter(ABC):
    @abstractmethod
    def apply(self, image: ImageModel) -> ImageModel:
        ...
