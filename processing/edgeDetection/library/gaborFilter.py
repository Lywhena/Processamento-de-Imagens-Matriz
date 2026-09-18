from __future__ import annotations

import math

import cv2
import numpy as np

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import applyKernel, renderEdgeMap, toGrayscale

GABOR_SIGMA_PER_WAVELENGTH = 0.56
GABOR_ASPECT_RATIO = 0.5
GABOR_ORIENTATIONS = 8


def buildQuadraturePair(wavelength: float, theta: float) -> tuple[np.ndarray, np.ndarray]:
    sigma = GABOR_SIGMA_PER_WAVELENGTH * wavelength
    size = 2 * math.ceil(3.0 * sigma) + 1
    even = cv2.getGaborKernel(
        (size, size), sigma, theta, wavelength, GABOR_ASPECT_RATIO, 0.0, ktype=cv2.CV_64F
    )
    odd = cv2.getGaborKernel(
        (size, size), sigma, theta, wavelength, GABOR_ASPECT_RATIO, math.pi / 2, ktype=cv2.CV_64F
    )
    return even - even.mean(), odd


class GaborFilter(EdgeMapFilter):
    def __init__(
        self, wavelength: float = 4.0, thresholdRatio: float | None = None, invert: bool = False
    ) -> None:
        super().__init__(thresholdRatio, invert)
        if wavelength < 2:
            raise ValueError(f"wavelength must be at least 2 pixels (got {wavelength})")
        self.wavelength = wavelength

    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        strongest = np.zeros(gray.shape, dtype=np.float64)

        for index in range(GABOR_ORIENTATIONS):
            even, odd = buildQuadraturePair(self.wavelength, math.pi * index / GABOR_ORIENTATIONS)
            energy = cv2.magnitude(applyKernel(gray, even), applyKernel(gray, odd))
            strongest = cv2.max(strongest, energy)

        return ImageModel(renderEdgeMap(strongest, self.thresholdRatio, self.invert))
