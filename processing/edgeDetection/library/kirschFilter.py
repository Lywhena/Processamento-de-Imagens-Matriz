from __future__ import annotations

from core.imageModel import ImageModel
from processing.edgeDetection.edgeMapFilter import EdgeMapFilter
from processing.edgeDetection.library._cvOps import maxResponse, renderEdgeMap, toGrayscale

RING_POSITIONS = ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0))
BASE_RING_VALUES = (5, 5, 5, -3, -3, -3, -3, -3)


def buildKirschKernels() -> list[list[list[int]]]:
    kernels = []
    for rotation in range(len(RING_POSITIONS)):
        kernel = [[0, 0, 0] for _ in range(3)]
        for index, (row, col) in enumerate(RING_POSITIONS):
            kernel[row][col] = BASE_RING_VALUES[(index - rotation) % len(BASE_RING_VALUES)]
        kernels.append(kernel)
    return kernels


KIRSCH_KERNELS = buildKirschKernels()


class KirschFilter(EdgeMapFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        response = maxResponse(toGrayscale(image.pixels), KIRSCH_KERNELS)
        return ImageModel(renderEdgeMap(response, self.thresholdRatio, self.invert))
