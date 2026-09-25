from __future__ import annotations

import math

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import NEGLIGIBLE_RESPONSE, validateRatio
from processing.edgeDetection.manual.manualOps import (
    convolveColumns,
    convolveRows,
    padReplicate,
    renderBinaryMask,
    toGrayscale,
)
from processing.imageFilter import ImageFilter

NEIGHBOR_OFFSETS = ((0, -1), (0, 1), (-1, 0), (1, 0))


def kernelRadius(sigma: float) -> int:
    return math.ceil(3.0 * sigma)


def buildLogKernels(sigma: float) -> tuple[list[float], list[float]]:
    radius = kernelRadius(sigma)
    variance = sigma * sigma
    scale = 1.0 / (2.0 * math.pi * variance)
    gaussian = []
    secondDerivative = []

    for offset in range(-radius, radius + 1):
        weight = math.exp(-(offset * offset) / (2.0 * variance))
        gaussian.append(weight)
        secondDerivative.append(scale * (offset * offset - variance) / (variance * variance) * weight)

    mean = sum(secondDerivative) / len(secondDerivative)
    secondDerivative = [value - mean for value in secondDerivative]
    return secondDerivative, gaussian


def laplacianOfGaussian(gray: list[list[float]], sigma: float) -> list[list[float]]:
    secondDerivative, gaussian = buildLogKernels(sigma)
    horizontalTerm = convolveColumns(convolveRows(gray, secondDerivative), gaussian)
    verticalTerm = convolveColumns(convolveRows(gray, gaussian), secondDerivative)
    return [
        [horizontal + vertical for horizontal, vertical in zip(rowH, rowV)]
        for rowH, rowV in zip(horizontalTerm, verticalTerm)
    ]


def zeroCrossings(response: list[list[float]], slopeThresholdRatio: float) -> list[list[bool]]:
    height = len(response)
    width = len(response[0])
    highest = 0.0
    for row in response:
        for value in row:
            if abs(value) > highest:
                highest = abs(value)

    if highest <= NEGLIGIBLE_RESPONSE:
        return [[False] * width for _ in range(height)]

    threshold = slopeThresholdRatio * highest
    padded = padReplicate(response, 1)
    mask = []

    for row in range(height):
        maskRow = []
        for col in range(width):
            center = response[row][col]
            isEdge = False
            if center < 0:
                for rowOffset, colOffset in NEIGHBOR_OFFSETS:
                    neighbor = padded[row + 1 + rowOffset][col + 1 + colOffset]
                    if neighbor >= 0 and neighbor - center > threshold:
                        isEdge = True
                        break
            maskRow.append(isEdge)
        mask.append(maskRow)

    return mask


class LaplacianOfGaussianFilter(ImageFilter):
    def __init__(
        self, sigma: float = 2.0, slopeThresholdRatio: float = 0.10, invert: bool = False
    ) -> None:
        if sigma <= 0:
            raise ValueError(f"sigma must be positive (got {sigma})")
        validateRatio(slopeThresholdRatio, "slopeThresholdRatio")
        self.sigma = sigma
        self.slopeThresholdRatio = slopeThresholdRatio
        self.invert = invert

    def apply(self, image: ImageModel) -> ImageModel:
        response = laplacianOfGaussian(toGrayscale(image.pixels), self.sigma)
        mask = zeroCrossings(response, self.slopeThresholdRatio)
        return ImageModel(renderBinaryMask(mask, self.invert))
