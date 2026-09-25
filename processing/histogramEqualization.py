from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.imageModel import ImageModel
from processing.edgeDetection.manual.manualOps import toGrayscale
from processing.imageFilter import ImageFilter

INTENSITY_LEVELS = 256 #qnt de tons
VALID_CLASS_COUNTS = (2, 4, 8, 16, 32, 64, 128) #qnt de classes permitidas


@dataclass(frozen=True)
class ClassTableRow:
    classNumber: int  # Classes
    rangeStart: int  # Faixa Int Inicial
    rangeEnd: int  # Faixa Int Final
    pixelCount: int  # nk
    probability: float  # pr(rk)
    cumulativeProbability: float  # sk
    referenceLevel: float  # rk(R)
    newClassNumber: int  # new (sk)
    difference: int  # Diferença
    shift: int  # FxD




def bandWidthFor(classCount: int) -> int:
    return INTENSITY_LEVELS // classCount


def toGrayLevels(pixels: np.ndarray) -> list[list[int]]:
    return [[int(value + 0.5) for value in row] for row in toGrayscale(pixels)]


def countPixelsPerClass(grayLevels: list[list[int]], classCount: int) -> list[int]:
    bandWidth = bandWidthFor(classCount)
    counts = [0] * classCount

    for row in grayLevels:
        for value in row:
            counts[value // bandWidth] += 1

    return counts


def buildClassTable(pixelCounts: list[int]) -> list[ClassTableRow]:
    classCount = len(pixelCounts)

    bandWidth = bandWidthFor(classCount)
    totalPixels = sum(pixelCounts)
    if totalPixels == 0:
        raise ValueError("cannot equalize an empty image")

    table = []
    cumulativeCount = 0

    for index, pixelCount in enumerate(pixelCounts):
        cumulativeCount += pixelCount
        cumulativeProbability = cumulativeCount / totalPixels
        newClassIndex = int(cumulativeProbability * (classCount - 1) + 0.5)
        difference = newClassIndex - index
        table.append(
            ClassTableRow(
                classNumber=index + 1,
                rangeStart=index * bandWidth,
                rangeEnd=(index + 1) * bandWidth - 1,
                pixelCount=pixelCount,
                probability=pixelCount / totalPixels,
                cumulativeProbability=cumulativeProbability,
                referenceLevel=index / (classCount - 1),
                newClassNumber=newClassIndex + 1,
                difference=difference,
                shift=difference * bandWidth,
            )
        )

    return table


def buildLookupTable(table: list[ClassTableRow]) -> list[int]:
    bandWidth = bandWidthFor(len(table))
    return [value + table[value // bandWidth].shift for value in range(INTENSITY_LEVELS)]


def equalizedPixelCounts(table: list[ClassTableRow]) -> list[int]:
    counts = [0] * len(table)
    for row in table:
        counts[row.newClassNumber - 1] += row.pixelCount
    return counts


class HistogramEqualizationFilter(ImageFilter):
    def __init__(self, classCount: int = 8) -> None:

        self.classCount = classCount
        self.classTable: list[ClassTableRow] = []

    def apply(self, image: ImageModel) -> ImageModel:
        grayLevels = toGrayLevels(image.pixels)
        self.classTable = buildClassTable(countPixelsPerClass(grayLevels, self.classCount))
        lookupTable = buildLookupTable(self.classTable)
        equalized = [[lookupTable[value] for value in row] for row in grayLevels]
        return ImageModel(np.array(equalized, dtype=np.uint8))
