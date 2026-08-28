from __future__ import annotations

import numpy as np

from core.imageModel import ImageModel
from processing.imageFilter import ImageFilter


def _rotateLeft90(pixels: np.ndarray) -> np.ndarray:
    height, width = pixels.shape[0], pixels.shape[1]
    rotated = np.empty((width, height) + pixels.shape[2:], dtype=pixels.dtype)

    for row in range(width):
        for col in range(height):
            rotated[row, col] = pixels[col, width - 1 - row]

    return rotated


def _rotateRight90(pixels: np.ndarray) -> np.ndarray:
    height, width = pixels.shape[0], pixels.shape[1]
    rotated = np.empty((width, height) + pixels.shape[2:], dtype=pixels.dtype)

    for row in range(width):
        for col in range(height):
            rotated[row, col] = pixels[height - 1 - col, row]

    return rotated


def _flipVertical(pixels: np.ndarray) -> np.ndarray:
    height, width = pixels.shape[0], pixels.shape[1]
    flipped = np.empty_like(pixels)

    for row in range(height):
        for col in range(width):
            flipped[row, col] = pixels[height - 1 - row, col]

    return flipped


def _flipHorizontal(pixels: np.ndarray) -> np.ndarray:
    height, width = pixels.shape[0], pixels.shape[1]
    flipped = np.empty_like(pixels)

    for row in range(height):
        for col in range(width):
            flipped[row, col] = pixels[row, width - 1 - col]

    return flipped


class RotateLeft90Filter(ImageFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        return ImageModel(_rotateLeft90(image.pixels))


class RotateRight90Filter(ImageFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        return ImageModel(_rotateRight90(image.pixels))


class FlipVerticalFilter(ImageFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        return ImageModel(_flipVertical(image.pixels))


class FlipHorizontalFilter(ImageFilter):
    def apply(self, image: ImageModel) -> ImageModel:
        return ImageModel(_flipHorizontal(image.pixels))
