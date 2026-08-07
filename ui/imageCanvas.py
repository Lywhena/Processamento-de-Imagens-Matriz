from __future__ import annotations

import tkinter as tk

from PIL import Image, ImageTk

from core.imageModel import ImageModel


class ImageCanvas(tk.Canvas):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, background="gray20")
        self._displayedPhoto: ImageTk.PhotoImage | None = None

    def showImage(self, image: ImageModel) -> None:
        mode = "L" if image.isGrayscale else "RGB"
        pilImage = Image.fromarray(image.pixels, mode=mode)

        self.config(width=image.width, height=image.height)
        self._displayedPhoto = ImageTk.PhotoImage(pilImage)
        self.delete("all")
        self.create_image(0, 0, anchor="nw", image=self._displayedPhoto)
