from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import DEFAULT_THRESHOLD_RATIO, EdgeMapFilter
from processing.edgeDetection.library._cvOps import renderEdgeMap, toGrayscale


class GaussianGradientFilter(EdgeMapFilter):
    def __init__(
        self,
        sigma: float = 1.0,
        thresholdRatio: float | None = DEFAULT_THRESHOLD_RATIO,
        invert: bool = False,
    ) -> None:
        super().__init__(thresholdRatio, invert)
        if sigma <= 0:
            raise ValueError(f"sigma must be positive (got {sigma})")
        self.sigma = sigma

    def apply(self, image: ImageModel) -> ImageModel:
        smoothed = cv2.GaussianBlur(
            toGrayscale(image.pixels), (0, 0), self.sigma, borderType=cv2.BORDER_REPLICATE
        )
        gradientX = cv2.Sobel(smoothed, cv2.CV_64F, 1, 0, ksize=3, borderType=cv2.BORDER_REPLICATE)
        gradientY = cv2.Sobel(smoothed, cv2.CV_64F, 0, 1, ksize=3, borderType=cv2.BORDER_REPLICATE)
        magnitude = cv2.magnitude(gradientX, gradientY)
        return ImageModel(renderEdgeMap(magnitude, self.thresholdRatio, self.invert))
