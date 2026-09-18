from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.library._cvOps import finalizeEdgeMap, toGrayscaleUint8
from processing.imageFilter import ImageFilter


class CannyFilter(ImageFilter):
    def __init__(
        self,
        lowThreshold: float = 30,
        highThreshold: float = 90,
        blurSigma: float = 1.4,
        invert: bool = False,
    ) -> None:
        if not 0 <= lowThreshold < highThreshold:
            raise ValueError("thresholds must satisfy 0 <= low < high")
        self.lowThreshold = lowThreshold
        self.highThreshold = highThreshold
        self.blurSigma = blurSigma
        self.invert = invert

    def apply(self, image: ImageModel) -> ImageModel:
        smoothed = cv2.GaussianBlur(
            toGrayscaleUint8(image.pixels), (0, 0), self.blurSigma, borderType=cv2.BORDER_REPLICATE
        )
        edges = cv2.Canny(smoothed, self.lowThreshold, self.highThreshold, L2gradient=True)
        return ImageModel(finalizeEdgeMap(edges, self.invert))
