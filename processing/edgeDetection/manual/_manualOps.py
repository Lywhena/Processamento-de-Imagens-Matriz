from __future__ import annotations

import numpy as np

from processing.edgeDetection.edgeMapFilter import NEGLIGIBLE_RESPONSE

LUMA_RED = 0.299
LUMA_GREEN = 0.587
LUMA_BLUE = 0.114


def toGrayscale(pixels: np.ndarray) -> list[list[float]]:
    rows = pixels.tolist()

    if pixels.ndim == 2:
        return [[float(value) for value in row] for row in rows]

    return [
        [LUMA_RED * red + LUMA_GREEN * green + LUMA_BLUE * blue for red, green, blue in row]
        for row in rows
    ]


def padRowReplicate(row: list[float], radius: int) -> list[float]:
    return [row[0]] * radius + row + [row[-1]] * radius


def padReplicate(matrix: list[list[float]], radius: int) -> list[list[float]]:
    paddedRows = [padRowReplicate(row, radius) for row in matrix]
    return [paddedRows[0]] * radius + paddedRows + [paddedRows[-1]] * radius


def convolveRows(matrix: list[list[float]], kernel: list[float]) -> list[list[float]]:
    radius = len(kernel) // 2
    result = []

    for row in matrix:
        padded = padRowReplicate(row, radius)
        filteredRow = []
        for col in range(len(row)):
            total = 0.0
            for offset, weight in enumerate(kernel):
                total += padded[col + offset] * weight
            filteredRow.append(total)
        result.append(filteredRow)

    return result


def convolveColumns(matrix: list[list[float]], kernel: list[float]) -> list[list[float]]:
    radius = len(kernel) // 2
    height = len(matrix)
    width = len(matrix[0])
    padded = [matrix[0]] * radius + matrix + [matrix[-1]] * radius
    result = []

    for row in range(height):
        filteredRow = [0.0] * width
        for offset, weight in enumerate(kernel):
            sourceRow = padded[row + offset]
            for col in range(width):
                filteredRow[col] += sourceRow[col] * weight
        result.append(filteredRow)

    return result


def maxValue(matrix: list[list[float]]) -> float:
    highest = 0.0
    for row in matrix:
        for value in row:
            if value > highest:
                highest = value
    return highest


def renderEdgeMap(
    response: list[list[float]], thresholdRatio: float | None, invert: bool
) -> np.ndarray:
    height = len(response)
    width = len(response[0])
    highest = maxValue(response)
    if highest <= NEGLIGIBLE_RESPONSE:
        highest = 0.0
    edgeMap = np.empty((height, width), dtype=np.uint8)

    for row in range(height):
        for col in range(width):
            value = response[row][col]
            if thresholdRatio is None:
                level = int(value * 255.0 / highest + 0.5) if highest > 0 else 0
            else:
                level = 255 if highest > 0 and value > thresholdRatio * highest else 0
            edgeMap[row, col] = 255 - level if invert else level

    return edgeMap


def renderBinaryMask(mask: list[list[bool]], invert: bool) -> np.ndarray:
    height = len(mask)
    width = len(mask[0])
    edgeValue, backgroundValue = (0, 255) if invert else (255, 0)
    edgeMap = np.empty((height, width), dtype=np.uint8)

    for row in range(height):
        for col in range(width):
            edgeMap[row, col] = edgeValue if mask[row][col] else backgroundValue

    return edgeMap
