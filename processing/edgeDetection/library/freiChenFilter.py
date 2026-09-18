from __future__ import annotations

import math

import cv2
import numpy as np

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import applyKernel, renderEdgeMap, toGrayscale

SQRT2 = math.sqrt(2.0)
FREI_CHEN_THRESHOLD_RATIO = 0.15

FREI_CHEN_EDGE_BASIS = (
    np.array([[1, SQRT2, 1], [0, 0, 0], [-1, -SQRT2, -1]]) / (2 * SQRT2),
    np.array([[1, 0, -1], [SQRT2, 0, -SQRT2], [1, 0, -1]]) / (2 * SQRT2),
    np.array([[0, -1, SQRT2], [1, 0, -1], [-SQRT2, 1, 0]]) / (2 * SQRT2),
    np.array([[SQRT2, -1, 0], [-1, 0, 1], [0, 1, -SQRT2]]) / (2 * SQRT2),
)

FREI_CHEN_OTHER_BASIS = (
    np.array([[0, 1, 0], [-1, 0, -1], [0, 1, 0]]) / 2,
    np.array([[-1, 0, 1], [0, 0, 0], [1, 0, -1]]) / 2,
    np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]]) / 6,
    np.array([[-2, 1, -2], [1, 4, 1], [-2, 1, -2]]) / 6,
    np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) / 3,
)


def projectionEnergy(gray: np.ndarray, basis) -> np.ndarray:
    energy = np.zeros(gray.shape, dtype=np.float64)
    for kernel in basis:
        energy = cv2.add(energy, cv2.pow(applyKernel(gray, kernel), 2))
    return energy


class FreiChenFilter(EdgeMapFilter):
    def __init__(
        self, thresholdRatio: float | None = FREI_CHEN_THRESHOLD_RATIO, invert: bool = False
    ) -> None:
        super().__init__(thresholdRatio, invert)

    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        edgeEnergy = projectionEnergy(gray, FREI_CHEN_EDGE_BASIS)
        totalEnergy = cv2.add(edgeEnergy, projectionEnergy(gray, FREI_CHEN_OTHER_BASIS))
        response = cv2.sqrt(cv2.divide(edgeEnergy, totalEnergy))
        return ImageModel(renderEdgeMap(response, self.thresholdRatio, self.invert))
