from __future__ import annotations

import cv2

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import renderEdgeMap, toGrayscale


class LaplacianFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        response = cv2.Laplacian(
            toGrayscale(image.pixels), cv2.CV_64F, ksize=1, borderType=cv2.BORDER_REPLICATE
        )
        return ImageModel(renderEdgeMap(response, self.thresholdRatio, self.invert))
