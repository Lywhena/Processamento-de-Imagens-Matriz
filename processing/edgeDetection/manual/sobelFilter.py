from __future__ import annotations

import math

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.manual._manualOps import padReplicate, renderEdgeMap, toGrayscale


def sobelGradients(
    gray: list[list[float]],
) -> tuple[list[list[float]], list[list[float]]]:
    height = len(gray)
    width = len(gray[0])
    padded = padReplicate(gray, 1)
    gradientX = []
    gradientY = []

    for row in range(height):
        above = padded[row]
        center = padded[row + 1]
        below = padded[row + 2]
        rowX = []
        rowY = []

        for col in range(width):
            left = above[col] + 2.0 * center[col] + below[col]
            right = above[col + 2] + 2.0 * center[col + 2] + below[col + 2]
            top = above[col] + 2.0 * above[col + 1] + above[col + 2]
            bottom = below[col] + 2.0 * below[col + 1] + below[col + 2]
            rowX.append(right - left)
            rowY.append(bottom - top)

        gradientX.append(rowX)
        gradientY.append(rowY)

    return gradientX, gradientY


def sobelMagnitude(gray: list[list[float]]) -> list[list[float]]:
    gradientX, gradientY = sobelGradients(gray)
    return [
        [math.sqrt(gx * gx + gy * gy) for gx, gy in zip(rowX, rowY)]
        for rowX, rowY in zip(gradientX, gradientY)
    ]


class SobelFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        magnitude = sobelMagnitude(toGrayscale(image.pixels))
        return ImageModel(renderEdgeMap(magnitude, self.thresholdRatio, self.invert))
