from __future__ import annotations

from processing.imageFilter import ImageFilter

DEFAULT_THRESHOLD_RATIO = 0.20
NEGLIGIBLE_RESPONSE = 1e-9


def validateRatio(ratio: float, name: str) -> None:
    if not 0.0 < ratio < 1.0:
        raise ValueError(f"{name} must be between 0 and 1 (got {ratio})")


class EdgeMapFilter(ImageFilter):
    def __init__(
        self, thresholdRatio: float | None = DEFAULT_THRESHOLD_RATIO, invert: bool = False
    ) -> None:
        if thresholdRatio is not None:
            validateRatio(thresholdRatio, "thresholdRatio")
        self.thresholdRatio = thresholdRatio
        self.invert = invert
