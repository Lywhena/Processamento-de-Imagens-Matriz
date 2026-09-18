from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from core.fileFormats.formatRegistry import getHandlerForFile
from core.imageModel import ImageModel
from processing.edgeDetection import (
    BoieCoxFilter,
    CannyFilter,
    FreiChenFilter,
    GaborFilter,
    GaussianGradientFilter,
    HoughLinesFilter,
    KirschFilter,
    LaplacianFilter,
    LaplacianOfGaussianFilter,
    PrewittFilter,
    RobertsFilter,
    ScharrFilter,
    SobelFilter,
)
from processing.geometryFilters import (
    FlipHorizontalFilter,
    FlipVerticalFilter,
    RotateLeft90Filter,
    RotateRight90Filter,
)
from processing.imageFilter import ImageFilter
from processing.noiseReductionFilters import (
    VALID_MASK_SIZES,
    MeanFilter,
    MedianFilter,
    WeightedMeanFilter,
)
from ui.imageCanvas import ImageCanvas

MANUAL_EDGE_FILTERS = (
    ("c) Sobel", SobelFilter),
    ("k) LoG (Laplaciano da Gaussiana)", LaplacianOfGaussianFilter),
)
LIBRARY_EDGE_FILTERS = (
    ("a) Roberts", RobertsFilter),
    ("b) Prewitt", PrewittFilter),
    ("d) Kirsch", KirschFilter),
    ("e) Frei-Chen", FreiChenFilter),
    ("f) Laplaciano", LaplacianFilter),
    ("g) Gaussiano", GaussianGradientFilter),
    ("h) Canny", CannyFilter),
    ("i) Boie-Cox", BoieCoxFilter),
    ("j) Scharr", ScharrFilter),
    ("l) Gabor", GaborFilter),
)

OPEN_IMAGE_FILE_TYPES = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
OPEN_MATRIX_FILE_TYPES = [("Matrix files", "*.txt"), ("All files", "*.*")]
SAVE_MATRIX_FILE_TYPES = [("Matrix files", "*.txt")]


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Image Editor")
        self.currentImage: ImageModel | None = None

        self._buildMenuBar()
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

    def _buildMenuBar(self) -> None:
        menuBar = tk.Menu(self)
        self.config(menu=menuBar)

        transformMenu = tk.Menu(menuBar, tearoff=False)
        transformMenu.add_command(
            label="Rotacionar 90° à Esquerda",
            command=lambda: self._applyFilter(RotateLeft90Filter()),
        )
        transformMenu.add_command(
            label="Rotacionar 90° à Direita",
            command=lambda: self._applyFilter(RotateRight90Filter()),
        )
        transformMenu.add_separator()
        transformMenu.add_command(
            label="Espelhar Verticalmente",
            command=lambda: self._applyFilter(FlipVerticalFilter()),
        )
        transformMenu.add_command(
            label="Espelhar Horizontalmente",
            command=lambda: self._applyFilter(FlipHorizontalFilter()),
        )
        menuBar.add_cascade(label="Transformar", menu=transformMenu)

        filtersMenu = tk.Menu(menuBar, tearoff=False)
        filtersMenu.add_cascade(
            label="Média", menu=self._buildMaskSizeMenu(filtersMenu, MeanFilter)
        )
        filtersMenu.add_cascade(
            label="Mediana", menu=self._buildMaskSizeMenu(filtersMenu, MedianFilter)
        )
        filtersMenu.add_cascade(
            label="Média Ponderada",
            menu=self._buildMaskSizeMenu(filtersMenu, WeightedMeanFilter),
        )
        menuBar.add_cascade(label="Redução de Ruído", menu=filtersMenu)

        menuBar.add_cascade(label="Detecção de Bordas", menu=self._buildEdgeDetectionMenu(menuBar))

    def _buildEdgeDetectionMenu(self, menuBar: tk.Menu) -> tk.Menu:
        self.invertEdges = tk.BooleanVar(master=self, value=True)

        edgeMenu = tk.Menu(menuBar, tearoff=False)
        edgeMenu.add_checkbutton(label="Bordas pretas sobre fundo branco", variable=self.invertEdges)
        edgeMenu.add_separator()

        manualMenu = tk.Menu(edgeMenu, tearoff=False)
        self._addEdgeFilterCommands(manualMenu, MANUAL_EDGE_FILTERS)
        manualMenu.add_command(
            label="m) Transformada de Hough",
            command=lambda: self._applyFilter(HoughLinesFilter()),
        )
        edgeMenu.add_cascade(label="Implementação Manual", menu=manualMenu)

        libraryMenu = tk.Menu(edgeMenu, tearoff=False)
        self._addEdgeFilterCommands(libraryMenu, LIBRARY_EDGE_FILTERS)
        edgeMenu.add_cascade(label="OpenCV", menu=libraryMenu)
        return edgeMenu

    def _addEdgeFilterCommands(self, menu: tk.Menu, filters) -> None:
        for label, filterClass in filters:
            menu.add_command(
                label=label,
                command=lambda cls=filterClass: self._applyFilter(
                    cls(invert=self.invertEdges.get())
                ),
            )

    def _buildMaskSizeMenu(self, parentMenu: tk.Menu, filterClass: type[ImageFilter]) -> tk.Menu:
        maskSizeMenu = tk.Menu(parentMenu, tearoff=False)
        for maskSize in VALID_MASK_SIZES:
            maskSizeMenu.add_command(
                label=f"{maskSize}x{maskSize}",
                command=lambda size=maskSize: self._applyFilter(filterClass(size)),
            )
        return maskSizeMenu

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

    def _applyFilter(self, imageFilter: ImageFilter) -> None:
        if self.currentImage is None:
            messagebox.showwarning("No image", "Load an image before applying a filter.")
            return

        try:
            filteredImage = imageFilter.apply(self.currentImage)
        except Exception as error:
            messagebox.showerror("Failed to apply filter", str(error))
            return

        self.currentImage = filteredImage
        self.imageCanvas.showImage(filteredImage)
        self.statusLabel.config(
            text=f"Applied {type(imageFilter).__name__} — "
            f"{filteredImage.width}x{filteredImage.height}, "
            f"{'grayscale' if filteredImage.isGrayscale else 'RGB'}"
        )

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
