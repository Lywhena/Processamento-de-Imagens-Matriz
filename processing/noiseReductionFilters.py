from __future__ import annotations

from abc import abstractmethod

import numpy as np

from core.imageModel import ImageModel
from processing.imageFilter import ImageFilter

VALID_MASK_SIZES = (3, 5, 7, 9, 21, 45)


def _validateMaskSize(maskSize: int) -> None:
    if maskSize not in VALID_MASK_SIZES:
        raise ValueError(
            f"unsupported mask size: {maskSize} (expected one of {VALID_MASK_SIZES})"
        )


def _clampIndex(index: int, upperBound: int) -> int:
    if index < 0:
        return 0
    if index >= upperBound:
        return upperBound - 1
    return index


def _buildUniformWeights(maskSize: int) -> list[list[float]]:
    weight = 1.0 / (maskSize * maskSize)
    return [[weight for _ in range(maskSize)] for _ in range(maskSize)]


def _buildBinomialWeights(maskSize: int) -> list[list[float]]:
    row = [1.0]
    for k in range(1, maskSize):
        row.append(row[k - 1] * (maskSize - k) / k)

    total = 0.0
    for a in row:
        for b in row:
            total += a * b

    return [[(a * b) / total for b in row] for a in row]


def _applyWeightedWindow(
    channel: np.ndarray, maskSize: int, weights: list[list[float]]
) -> np.ndarray:
    height, width = channel.shape
    radius = maskSize // 2
    result = np.empty((height, width), dtype=np.float64)

    for row in range(height):
        for col in range(width):
            total = 0.0
            for di in range(maskSize):
                neighborRow = _clampIndex(row + di - radius, height)
                for dj in range(maskSize):
                    neighborCol = _clampIndex(col + dj - radius, width)
                    total += float(channel[neighborRow, neighborCol]) * weights[di][dj]

            result[row, col] = total

    return result


def _histogramMedian(histogram: list[int], middleIndex: int) -> int:
    cumulative = 0
    for value in range(256):
        cumulative += histogram[value]
        if cumulative > middleIndex:
            return value

    return 255


def _medianFilterChannel(channel: np.ndarray, maskSize: int) -> np.ndarray:
    height, width = channel.shape
    radius = maskSize // 2
    middleIndex = (maskSize * maskSize) // 2
    result = np.empty((height, width), dtype=np.float64)

    for row in range(height):
        histogram = [0] * 256

        for di in range(maskSize):
            neighborRow = _clampIndex(row + di - radius, height)
            for dj in range(maskSize):
                neighborCol = _clampIndex(dj - radius, width)
                histogram[int(channel[neighborRow, neighborCol])] += 1

        result[row, 0] = _histogramMedian(histogram, middleIndex)

        for col in range(1, width):
            leavingCol = _clampIndex(col - 1 - radius, width)
            enteringCol = _clampIndex(col + radius, width)

            for di in range(maskSize):
                neighborRow = _clampIndex(row + di - radius, height)
                histogram[int(channel[neighborRow, leavingCol])] -= 1
                histogram[int(channel[neighborRow, enteringCol])] += 1

            result[row, col] = _histogramMedian(histogram, middleIndex)

    return result


def _applyPerChannel(pixels: np.ndarray, channelFilter) -> np.ndarray:
    if pixels.ndim == 2:
        filtered = channelFilter(pixels)
    else:
        filtered = np.stack(
            [channelFilter(pixels[:, :, index]) for index in range(pixels.shape[2])],
            axis=2,
        )

    return np.clip(np.round(filtered), 0, 255).astype(np.uint8)


class _MaskedFilter(ImageFilter):
    def __init__(self, maskSize: int) -> None:
        _validateMaskSize(maskSize)
        self.maskSize = maskSize

    def apply(self, image: ImageModel) -> ImageModel:
        return ImageModel(_applyPerChannel(image.pixels, self._filterChannel))

    @abstractmethod
    def _filterChannel(self, channel: np.ndarray) -> np.ndarray:
        ...


class MeanFilter(_MaskedFilter):

    def _filterChannel(self, channel: np.ndarray) -> np.ndarray:
        weights = _buildUniformWeights(self.maskSize)
        return _applyWeightedWindow(channel, self.maskSize, weights)


class WeightedMeanFilter(_MaskedFilter):

    def _filterChannel(self, channel: np.ndarray) -> np.ndarray:
        weights = _buildBinomialWeights(self.maskSize)
        return _applyWeightedWindow(channel, self.maskSize, weights)


class MedianFilter(_MaskedFilter):

    def _filterChannel(self, channel: np.ndarray) -> np.ndarray:
        return _medianFilterChannel(channel, self.maskSize)
