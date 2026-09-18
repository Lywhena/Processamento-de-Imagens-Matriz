from __future__ import annotations

import cv2
import numpy as np

from processing.edgeDetection.edgeMapFilter import NEGLIGIBLE_RESPONSE


def toGrayscale(pixels: np.ndarray) -> np.ndarray:
    if pixels.ndim == 2:
        return pixels.astype(np.float64)
    return cv2.cvtColor(pixels.astype(np.float32), cv2.COLOR_RGB2GRAY).astype(np.float64)


def toGrayscaleUint8(pixels: np.ndarray) -> np.ndarray:
    if pixels.ndim == 2:
        return pixels.copy()
    return cv2.cvtColor(pixels, cv2.COLOR_RGB2GRAY)


def applyKernel(gray: np.ndarray, kernel) -> np.ndarray:
    return cv2.filter2D(
        gray, cv2.CV_64F, np.asarray(kernel, dtype=np.float64), borderType=cv2.BORDER_REPLICATE
    )


def maxResponse(gray: np.ndarray, kernels) -> np.ndarray:
    strongest = applyKernel(gray, kernels[0])
    for kernel in kernels[1:]:
        strongest = cv2.max(strongest, applyKernel(gray, kernel))
    return strongest


def finalizeEdgeMap(edgeMap: np.ndarray, invert: bool) -> np.ndarray:
    return cv2.bitwise_not(edgeMap) if invert else edgeMap


def renderEdgeMap(response: np.ndarray, thresholdRatio: float | None, invert: bool) -> np.ndarray:
    magnitude = np.abs(response)
    highest = float(magnitude.max())

    if highest <= NEGLIGIBLE_RESPONSE:
        edgeMap = np.zeros(magnitude.shape, dtype=np.uint8)
    elif thresholdRatio is None:
        edgeMap = cv2.normalize(magnitude, None, 255.0, 0.0, cv2.NORM_INF, cv2.CV_8U)
    else:
        _, binary = cv2.threshold(magnitude, thresholdRatio * highest, 255.0, cv2.THRESH_BINARY)
        edgeMap = binary.astype(np.uint8)

    return finalizeEdgeMap(edgeMap, invert)
