from __future__ import annotations

from pathlib import Path

import numpy as np

from core.fileFormats.formatHandler import FormatHandler
from core.imageModel import ImageModel

# File layout:
#   line 1: "width height channelCount"
#   then one blank-line-separated block per channel (1 block if grayscale, 3 if RGB in R,G,B order)
#   each block has `height` rows of `width` space-separated integers (0-255)


class MatrixTextHandler(FormatHandler):
    def loadFile(self, filePath: Path) -> ImageModel:
        content = filePath.read_text(encoding="utf-8")
        blocks = [block for block in content.strip().split("\n\n") if block.strip()]

        if not blocks:
            raise ValueError("matrix file is empty")

        width, height, channelCount = (int(value) for value in blocks[0].split())
        matrixBlocks = blocks[1 : 1 + channelCount]

        if len(matrixBlocks) != channelCount:
            raise ValueError(
                f"expected {channelCount} channel block(s), found {len(matrixBlocks)}"
            )

        channels = [self._parseMatrix(block, width, height) for block in matrixBlocks]
        pixels = channels[0] if channelCount == 1 else np.stack(channels, axis=2)

        return ImageModel(pixels)

    def saveFile(self, image: ImageModel, filePath: Path) -> None:
        blocks = [f"{image.width} {image.height} {image.channelCount}"]

        if image.isGrayscale:
            blocks.append(self._formatMatrix(image.pixels))
        else:
            for channelIndex in range(3):
                blocks.append(self._formatMatrix(image.pixels[:, :, channelIndex]))

        filePath.write_text("\n\n".join(blocks), encoding="utf-8")

    @staticmethod
    def _parseMatrix(block: str, width: int, height: int) -> np.ndarray:
        rows = [
            [int(value) for value in line.split()]
            for line in block.splitlines()
            if line.strip()
        ]
        matrix = np.array(rows, dtype=np.uint8)

        if matrix.shape != (height, width):
            raise ValueError(
                f"matrix shape {matrix.shape} does not match header ({height}, {width})"
            )

        return matrix

    @staticmethod
    def _formatMatrix(matrix: np.ndarray) -> str:
        return "\n".join(" ".join(str(value) for value in row) for row in matrix)
