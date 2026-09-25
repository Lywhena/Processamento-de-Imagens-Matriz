from __future__ import annotations

import math

import numpy as np

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import validateRatio
from processing.edgeDetection.manual.manualOps import maxValue, padReplicate, toGrayscale
from processing.edgeDetection.manual.sobelFilter import sobelGradients
from processing.imageFilter import ImageFilter

LINE_COLOR = (255, 0, 0)
LINE_TOLERANCE = 1.5


def gradientNeighborOffsets(gradientX: float, gradientY: float) -> tuple[int, int]:
    angle = math.degrees(math.atan2(gradientY, gradientX)) % 180.0

    if angle < 22.5 or angle >= 157.5:
        return 0, 1
    if angle < 67.5:
        return 1, 1
    if angle < 112.5:
        return 1, 0
    return 1, -1


def suppressNonMaxima(
    magnitude: list[list[float]], gradientX: list[list[float]], gradientY: list[list[float]]
) -> list[list[float]]:
    height = len(magnitude)
    width = len(magnitude[0])
    padded = padReplicate(magnitude, 1)
    thinned = []

    for row in range(height):
        thinnedRow = []
        for col in range(width):
            value = magnitude[row][col]
            rowOffset, colOffset = gradientNeighborOffsets(gradientX[row][col], gradientY[row][col])
            before = padded[row + 1 - rowOffset][col + 1 - colOffset]
            after = padded[row + 1 + rowOffset][col + 1 + colOffset]
            thinnedRow.append(value if value > before and value >= after else 0.0)
        thinned.append(thinnedRow)

    return thinned


def orientationIndex(gradientX: float, gradientY: float, thetaCount: int) -> int:
    angle = math.atan2(gradientY, gradientX) % math.pi
    return int(angle * thetaCount / math.pi + 0.5) % thetaCount


def circularDistance(first: int, second: int, thetaCount: int) -> int:
    distance = abs(first - second)
    return min(distance, thetaCount - distance)


def detectEdgePoints(
    gray: list[list[float]], edgeThresholdRatio: float, thetaCount: int = 180
) -> list[tuple[int, int, int]]:
    gradientX, gradientY = sobelGradients(gray)
    magnitude = [
        [math.sqrt(gx * gx + gy * gy) for gx, gy in zip(rowX, rowY)]
        for rowX, rowY in zip(gradientX, gradientY)
    ]
    thinned = suppressNonMaxima(magnitude, gradientX, gradientY)
    threshold = edgeThresholdRatio * maxValue(magnitude)
    points = []

    for row, thinnedRow in enumerate(thinned):
        for col, value in enumerate(thinnedRow):
            if value > threshold:
                orientation = orientationIndex(gradientX[row][col], gradientY[row][col], thetaCount)
                points.append((row, col, orientation))

    return points


def trigTables(thetaCount: int) -> tuple[list[float], list[float]]:
    cosines = [math.cos(math.pi * index / thetaCount) for index in range(thetaCount)]
    sines = [math.sin(math.pi * index / thetaCount) for index in range(thetaCount)]
    return cosines, sines


def castVotes(
    accumulator: list[list[int]], point: tuple[int, int, int], cosines: list[float],
    sines: list[float], rhoOffset: int, orientationWindow: int, weight: int,
) -> None:
    row, col, orientation = point
    thetaCount = len(accumulator)
    for offset in range(-orientationWindow, orientationWindow + 1):
        thetaIndex = (orientation + offset) % thetaCount
        rho = col * cosines[thetaIndex] + row * sines[thetaIndex]
        accumulator[thetaIndex][int(rho + rhoOffset + 0.5)] += weight


def buildAccumulator(
    points: list[tuple[int, int, int]], height: int, width: int, thetaCount: int,
    orientationWindow: int,
) -> tuple[list[list[int]], int]:
    rhoOffset = math.ceil(math.sqrt(height * height + width * width))
    rhoCount = 2 * rhoOffset + 1
    cosines, sines = trigTables(thetaCount)
    accumulator = [[0] * rhoCount for _ in range(thetaCount)]

    for point in points:
        castVotes(accumulator, point, cosines, sines, rhoOffset, orientationWindow, 1)

    return accumulator, rhoOffset


def neighborhoodVotes(votes: list[int], rhoIndex: int) -> int:
    total = votes[rhoIndex]
    if rhoIndex > 0:
        total += votes[rhoIndex - 1]
    if rhoIndex < len(votes) - 1:
        total += votes[rhoIndex + 1]
    return total


def isNearLine(
    thetaIndex: int, rho: int, line: tuple[int, int], thetaCount: int,
    thetaRadius: int, rhoRadius: int,
) -> bool:
    otherTheta, otherRho = line
    thetaDistance = abs(thetaIndex - otherTheta)

    if thetaDistance <= thetaRadius and abs(rho - otherRho) <= rhoRadius:
        return True
    return thetaCount - thetaDistance <= thetaRadius and abs(rho + otherRho) <= rhoRadius


def strongestCandidate(
    accumulator: list[list[int]], candidates: list[tuple[int, int]], threshold: int
) -> tuple[int, int] | None:
    best = None
    bestTotal = -1
    bestCenter = -1
    survivors = []

    for thetaIndex, rhoIndex in candidates:
        votes = accumulator[thetaIndex]
        total = neighborhoodVotes(votes, rhoIndex)
        if total < threshold:
            continue
        survivors.append((thetaIndex, rhoIndex))
        center = votes[rhoIndex]
        if total > bestTotal or (total == bestTotal and center > bestCenter):
            best = (thetaIndex, rhoIndex)
            bestTotal = total
            bestCenter = center

    candidates[:] = survivors
    return best


def extractLines(
    points: list[tuple[int, int, int]], height: int, width: int, thetaCount: int,
    orientationWindow: int, minVotes: int, maxLines: int, thetaRadius: int, rhoRadius: int,
    lineTolerance: float,
) -> list[tuple[int, int]]:
    accumulator, rhoOffset = buildAccumulator(points, height, width, thetaCount, orientationWindow)
    cosines, sines = trigTables(thetaCount)
    threshold = max(minVotes, 1)
    activePoints = list(points)

    candidates = []
    for thetaIndex, votes in enumerate(accumulator):
        for rhoIndex in range(len(votes)):
            if votes[rhoIndex] > 0 and neighborhoodVotes(votes, rhoIndex) >= threshold:
                candidates.append((thetaIndex, rhoIndex))

    lines = []
    while candidates and len(lines) < maxLines:
        best = strongestCandidate(accumulator, candidates, threshold)
        if best is None:
            break
        candidates.remove(best)
        thetaIndex, rhoIndex = best

        rho = rhoIndex - rhoOffset
        if any(isNearLine(thetaIndex, rho, line, thetaCount, thetaRadius, rhoRadius) for line in lines):
            continue
        lines.append((thetaIndex, rho))

        cosine = cosines[thetaIndex]
        sine = sines[thetaIndex]
        remaining = []
        for point in activePoints:
            row, col, orientation = point
            explained = (
                abs(col * cosine + row * sine - rho) <= lineTolerance
                and circularDistance(orientation, thetaIndex, thetaCount) <= orientationWindow
            )
            if explained:
                castVotes(accumulator, point, cosines, sines, rhoOffset, orientationWindow, -1)
            else:
                remaining.append(point)
        activePoints = remaining

    return lines


def linePixels(
    thetaIndex: int, rho: int, thetaCount: int, height: int, width: int
) -> list[tuple[int, int]]:
    theta = math.pi * thetaIndex / thetaCount
    cosine = math.cos(theta)
    sine = math.sin(theta)
    pixels = []

    if abs(sine) >= abs(cosine):
        for col in range(width):
            row = math.floor((rho - col * cosine) / sine + 0.5)
            if 0 <= row < height:
                pixels.append((row, col))
    else:
        for row in range(height):
            col = math.floor((rho - row * sine) / cosine + 0.5)
            if 0 <= col < width:
                pixels.append((row, col))

    return pixels


def buildOrientationMap(
    points: list[tuple[int, int, int]], height: int, width: int
) -> list[list[int]]:
    orientations = [[-1] * width for _ in range(height)]
    for row, col, orientation in points:
        orientations[row][col] = orientation
    return orientations


def isSupported(
    orientations: list[list[int]], row: int, col: int, thetaIndex: int,
    thetaCount: int, orientationWindow: int,
) -> bool:
    height = len(orientations)
    width = len(orientations[0])
    for neighborRow in range(max(row - 1, 0), min(row + 2, height)):
        for neighborCol in range(max(col - 1, 0), min(col + 2, width)):
            orientation = orientations[neighborRow][neighborCol]
            if orientation >= 0 and circularDistance(orientation, thetaIndex, thetaCount) <= orientationWindow:
                return True
    return False


def supportedSegments(
    pixels: list[tuple[int, int]], orientations: list[list[int]], thetaIndex: int,
    thetaCount: int, orientationWindow: int, maxGap: int, minLength: int,
) -> list[list[tuple[int, int]]]:
    segments = []
    start = None
    lastSupported = None

    for index, (row, col) in enumerate(pixels):
        if not isSupported(orientations, row, col, thetaIndex, thetaCount, orientationWindow):
            continue
        if start is None:
            start = index
        elif index - lastSupported > maxGap + 1:
            if lastSupported - start + 1 >= minLength:
                segments.append(pixels[start:lastSupported + 1])
            start = index
        lastSupported = index

    if start is not None and lastSupported - start + 1 >= minLength:
        segments.append(pixels[start:lastSupported + 1])

    return segments


def toRgbCopy(pixels: np.ndarray) -> np.ndarray:
    height, width = pixels.shape[0], pixels.shape[1]
    rgb = np.empty((height, width, 3), dtype=np.uint8)

    for row in range(height):
        for col in range(width):
            if pixels.ndim == 2:
                value = pixels[row, col]
                rgb[row, col] = (value, value, value)
            else:
                rgb[row, col] = pixels[row, col]

    return rgb


class HoughLinesFilter(ImageFilter):
    def __init__(
        self,
        minLineRatio: float = 0.05,
        edgeThresholdRatio: float = 0.25,
        maxLines: int = 50,
        maxGap: int = 5,
        orientationWindow: int = 10,
        thetaCount: int = 180,
        thetaRadius: int = 4,
        rhoRadius: int = 8,
    ) -> None:
        validateRatio(minLineRatio, "minLineRatio")
        validateRatio(edgeThresholdRatio, "edgeThresholdRatio")
        self.minLineRatio = minLineRatio
        self.edgeThresholdRatio = edgeThresholdRatio
        self.maxLines = maxLines
        self.maxGap = maxGap
        self.orientationWindow = orientationWindow
        self.thetaCount = thetaCount
        self.thetaRadius = thetaRadius
        self.rhoRadius = rhoRadius

    def minLineLength(self, image: ImageModel) -> int:
        return max(2, round(self.minLineRatio * min(image.height, image.width)))

    def detectLines(self, image: ImageModel) -> list[tuple[int, int]]:
        return self._linesFromPoints(self._edgePoints(image), image)

    def detectSegments(self, image: ImageModel) -> list[list[tuple[int, int]]]:
        points = self._edgePoints(image)
        orientations = buildOrientationMap(points, image.height, image.width)
        minLength = self.minLineLength(image)
        segments = []

        for thetaIndex, rho in self._linesFromPoints(points, image):
            pixels = linePixels(thetaIndex, rho, self.thetaCount, image.height, image.width)
            segments += supportedSegments(
                pixels, orientations, thetaIndex, self.thetaCount,
                self.orientationWindow, self.maxGap, minLength,
            )

        return segments

    def _edgePoints(self, image: ImageModel) -> list[tuple[int, int, int]]:
        return detectEdgePoints(toGrayscale(image.pixels), self.edgeThresholdRatio, self.thetaCount)

    def _linesFromPoints(
        self, points: list[tuple[int, int, int]], image: ImageModel
    ) -> list[tuple[int, int]]:
        return extractLines(
            points, image.height, image.width, self.thetaCount, self.orientationWindow,
            self.minLineLength(image), self.maxLines, self.thetaRadius, self.rhoRadius,
            LINE_TOLERANCE,
        )

    def apply(self, image: ImageModel) -> ImageModel:
        output = toRgbCopy(image.pixels)

        for segment in self.detectSegments(image):
            for row, col in segment:
                output[row, col] = LINE_COLOR

        return ImageModel(output)
