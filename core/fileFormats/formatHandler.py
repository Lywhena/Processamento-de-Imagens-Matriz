from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.imageModel import ImageModel


class FormatHandler(ABC):
    @abstractmethod
    def loadFile(self, filePath: Path) -> ImageModel:
        ...

    @abstractmethod
    def saveFile(self, image: ImageModel, filePath: Path) -> None:
        ...
