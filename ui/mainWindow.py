from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from core.fileFormats.formatRegistry import getHandlerForFile
from core.imageModel import ImageModel
from ui.imageCanvas import ImageCanvas

OPEN_IMAGE_FILE_TYPES = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
OPEN_MATRIX_FILE_TYPES = [("Matrix files", "*.txt"), ("All files", "*.*")]
SAVE_MATRIX_FILE_TYPES = [("Matrix files", "*.txt")]


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Image Editor")
        self.currentImage: ImageModel | None = None

        self._buildToolbar()
        self.imageCanvas = ImageCanvas(self)
        self.imageCanvas.pack(padx=10, pady=(0, 10))
        self._buildStatusBar()

    def _buildToolbar(self) -> None:
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        tk.Button(toolbar, text="Open Image", command=self._onOpenImage).pack(side="left", padx=5)
        tk.Button(toolbar, text="Open Matrix", command=self._onOpenMatrix).pack(side="left", padx=5)
        tk.Button(toolbar, text="Save as Matrix", command=self._onSaveAsMatrix).pack(side="left", padx=5)

    def _buildStatusBar(self) -> None:
        self.statusLabel = tk.Label(self, text="No image loaded", anchor="w")
        self.statusLabel.pack(fill="x", padx=10, pady=(0, 10))

    def _onOpenImage(self) -> None:
        selectedPath = filedialog.askopenfilename(filetypes=OPEN_IMAGE_FILE_TYPES)
        if selectedPath:
            self._loadFromPath(Path(selectedPath))

    def _onOpenMatrix(self) -> None:
        selectedPath = filedialog.askopenfilename(filetypes=OPEN_MATRIX_FILE_TYPES)
        if selectedPath:
            self._loadFromPath(Path(selectedPath))

    def _onSaveAsMatrix(self) -> None:
        if self.currentImage is None:
            messagebox.showwarning("No image", "Load an image before saving.")
            return

        selectedPath = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=SAVE_MATRIX_FILE_TYPES
        )
        if not selectedPath:
            return

        destinationPath = Path(selectedPath)
        try:
            handler = getHandlerForFile(destinationPath)
            handler.saveFile(self.currentImage, destinationPath)
        except Exception as error:
            messagebox.showerror("Failed to save matrix", str(error))
            return

        self.statusLabel.config(text=f"Saved matrix to {destinationPath.name}")

    def _loadFromPath(self, filePath: Path) -> None:
        try:
            handler = getHandlerForFile(filePath)
            image = handler.loadFile(filePath)
        except Exception as error:
            messagebox.showerror("Failed to load file", str(error))
            return

        self.currentImage = image
        self.imageCanvas.showImage(image)
        self.statusLabel.config(
            text=f"{filePath.name} — {image.width}x{image.height}, "
            f"{'grayscale' if image.isGrayscale else 'RGB'}"
        )
