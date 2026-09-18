from __future__ import annotations

import math

import cv2
import numpy as np

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import NEGLIGIBLE_RESPONSE
from processing.edgeDetection.library._cvOps import finalizeEdgeMap, toGrayscale
from processing.imageFilter import ImageFilter

ALONG_EDGE_SIGMA_FACTOR = 2.0
NOISE_TO_HIGH_THRESHOLD = 5.0
LOW_TO_HIGH_THRESHOLD = 0.5
MAD_TO_STANDARD_DEVIATION = 1.4826
INT16_LIMIT = 32000.0


def buildMatchedKernels(sigma: float) -> tuple[np.ndarray, np.ndarray]:
    alongSigma = ALONG_EDGE_SIGMA_FACTOR * sigma
    size = 2 * math.ceil(3.0 * alongSigma) + 1
    offsets = np.arange(size, dtype=np.float64) - size // 2
    across = cv2.getGaussianKernel(size, sigma, cv2.CV_64F).ravel()
    derivative = -offsets / (sigma * sigma) * across
    along = cv2.getGaussianKernel(size, alongSigma, cv2.CV_64F).ravel()
    return derivative, along


def estimateNoiseLevel(gradientX: np.ndarray, gradientY: np.ndarray) -> float:
    responses = np.abs(np.concatenate((gradientX.ravel(), gradientY.ravel())))
    return MAD_TO_STANDARD_DEVIATION * float(np.median(responses))


class BoieCoxFilter(ImageFilter):
    def __init__(self, sigma: float = 2.0, invert: bool = False) -> None:
        if sigma <= 0:
            raise ValueError(f"sigma must be positive (got {sigma})")
        self.sigma = sigma
        self.invert = invert

    def apply(self, image: ImageModel) -> ImageModel:
        gray = toGrayscale(image.pixels)
        derivative, along = buildMatchedKernels(self.sigma)
        gradientX = cv2.sepFilter2D(gray, cv2.CV_64F, derivative, along, borderType=cv2.BORDER_REPLICATE)
        gradientY = cv2.sepFilter2D(gray, cv2.CV_64F, along, derivative, borderType=cv2.BORDER_REPLICATE)

        highest = float(max(np.abs(gradientX).max(), np.abs(gradientY).max()))
        if highest <= NEGLIGIBLE_RESPONSE:
            return ImageModel(finalizeEdgeMap(np.zeros(gray.shape, dtype=np.uint8), self.invert))

        scale = INT16_LIMIT / highest
        highThreshold = NOISE_TO_HIGH_THRESHOLD * estimateNoiseLevel(gradientX, gradientY) * scale
        edges = cv2.Canny(
            np.round(gradientX * scale).astype(np.int16),
            np.round(gradientY * scale).astype(np.int16),
            LOW_TO_HIGH_THRESHOLD * highThreshold,
            highThreshold,
            L2gradient=True,
        )
        return ImageModel(finalizeEdgeMap(edges, self.invert))
