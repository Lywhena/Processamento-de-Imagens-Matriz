from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import applyKernel, renderEdgeMap, toGrayscale

PREWITT_X = ((-1, 0, 1), (-1, 0, 1), (-1, 0, 1))
PREWITT_Y = ((-1, -1, -1), (0, 0, 0), (1, 1, 1))


class PrewittFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        magnitude = cv2.magnitude(applyKernel(gray, PREWITT_X), applyKernel(gray, PREWITT_Y))
        return ImageModel(renderEdgeMap(magnitude, self.thresholdRatio, self.invert))
