from __future__ import annotations

import numpy as np


class ImageModel:
    def __init__(self, pixels: np.ndarray) -> None:
        if pixels.ndim not in (2, 3):
            raise ValueError("pixels must be a 2D (grayscale) or 3D (RGB) array")
        if pixels.ndim == 3 and pixels.shape[2] != 3:
            raise ValueError("color images must have exactly 3 channels (RGB)")

        self.pixels = pixels.astype(np.uint8, copy=False)

    @property
    def width(self) -> int:
        return self.pixels.shape[1]

    @property
    def height(self) -> int:
        return self.pixels.shape[0]

    @property
    def channelCount(self) -> int:
        return 1 if self.pixels.ndim == 2 else self.pixels.shape[2]

    @property
    def isGrayscale(self) -> bool:
        return self.channelCount == 1
