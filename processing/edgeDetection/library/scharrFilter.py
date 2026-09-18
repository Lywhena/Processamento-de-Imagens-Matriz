from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import renderEdgeMap, toGrayscale


class ScharrFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        gradientX = cv2.Scharr(gray, cv2.CV_64F, 1, 0, borderType=cv2.BORDER_REPLICATE)
        gradientY = cv2.Scharr(gray, cv2.CV_64F, 0, 1, borderType=cv2.BORDER_REPLICATE)
        magnitude = cv2.magnitude(gradientX, gradientY)
        return ImageModel(renderEdgeMap(magnitude, self.thresholdRatio, self.invert))
