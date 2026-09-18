from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import applyKernel, renderEdgeMap, toGrayscale

ROBERTS_MAIN_DIAGONAL = ((1, 0), (0, -1))
ROBERTS_ANTI_DIAGONAL = ((0, 1), (-1, 0))


class RobertsFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        magnitude = cv2.magnitude(
            applyKernel(gray, ROBERTS_MAIN_DIAGONAL), applyKernel(gray, ROBERTS_ANTI_DIAGONAL)
        )
        return ImageModel(renderEdgeMap(magnitude, self.thresholdRatio, self.invert))
