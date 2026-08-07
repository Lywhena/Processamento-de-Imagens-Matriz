from __future__ import annotations

from pathlib import Path

from core.fileFormats.formatHandler import FormatHandler
from core.fileFormats.matrixTextHandler import MatrixTextHandler
from core.fileFormats.standardImageHandler import StandardImageHandler

_HANDLERS_BY_EXTENSION: dict[str, FormatHandler] = {
    ".png": StandardImageHandler(),
    ".jpg": StandardImageHandler(),
    ".jpeg": StandardImageHandler(),
    ".txt": MatrixTextHandler(),
}


def getHandlerForFile(filePath: Path) -> FormatHandler:
    extension = filePath.suffix.lower()
    handler = _HANDLERS_BY_EXTENSION.get(extension)

    if handler is None:
        raise ValueError(f"unsupported file extension: {extension}")

    return handler
