from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from core.fileFormats.formatHandler import FormatHandler
from core.imageModel import ImageModel


class StandardImageHandler(FormatHandler):
    def loadFile(self, filePath: Path) -> ImageModel:
        with Image.open(filePath) as openedImage:
            if openedImage.mode not in ("L", "RGB"):
                openedImage = openedImage.convert("RGB")
            pixels = np.array(openedImage)

        return ImageModel(pixels)

    def saveFile(self, image: ImageModel, filePath: Path) -> None:
        mode = "L" if image.isGrayscale else "RGB"
        pilImage = Image.fromarray(image.pixels, mode=mode)
        pilImage.save(filePath)
