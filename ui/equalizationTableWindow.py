from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from processing.histogramEqualization import INTENSITY_LEVELS, ClassTableRow, bandWidthFor

TABLE_COLUMNS = (
    ("Classes", 60),
    ("Faixa Int Inicial", 105),
    ("Faixa Int Final", 95),
    ("nk", 70),
    ("pr(rk)", 70),
    ("sk", 70),
    ("rk(R)", 70),
    ("new (sk)", 70),
    ("Diferença", 75),
    ("FxD", 60),
)
MAX_VISIBLE_ROWS = 16


def formatDecimal(value: float) -> str:
    return f"{value:.4f}"


class EqualizationTableWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, table: list[ClassTableRow]) -> None:
        super().__init__(parent)
        self.title(f"Equalização de Histograma — {len(table)} classes")
        self.transient(parent)

        self._buildSummary(table)
        self._buildTable(table)
        self._placeBesideParent(parent)

    def _placeBesideParent(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        left = parent.winfo_rootx() + parent.winfo_width() + 10
        left = max(0, min(left, self.winfo_screenwidth() - self.winfo_reqwidth()))
        self.geometry(f"+{left}+{parent.winfo_rooty()}")

    def _buildSummary(self, table: list[ClassTableRow]) -> None:
        classCount = len(table)
        totalPixels = sum(row.pixelCount for row in table)
        summary = (
            f"L = {classCount} classes   |   Faixa = {INTENSITY_LEVELS} / L = "
            f"{bandWidthFor(classCount)} tons   |   Σnk = {totalPixels} pixels   |   "
            f"passo de rk(R) = 1/(L−1) = {formatDecimal(1 / (classCount - 1))}\n"
            "new (sk) = classe cujo rk(R) é o mais próximo de sk   |   "
            "Novo Pixel = Pixel + FxD, onde FxD = Faixa × Diferença"
        )
        tk.Label(self, text=summary, anchor="w", justify="left").pack(
            fill="x", padx=10, pady=(10, 0)
        )

    def _buildTable(self, table: list[ClassTableRow]) -> None:
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnIds = [f"column{index}" for index in range(len(TABLE_COLUMNS))]
        treeview = ttk.Treeview(
            frame,
            columns=columnIds,
            show="headings",
            height=min(len(table) + 1, MAX_VISIBLE_ROWS),
        )
        for columnId, (heading, width) in zip(columnIds, TABLE_COLUMNS):
            treeview.heading(columnId, text=heading)
            treeview.column(columnId, width=width, anchor="center")

        for row in table:
            treeview.insert(
                "",
                "end",
                values=(
                    row.classNumber,
                    row.rangeStart,
                    row.rangeEnd,
                    row.pixelCount,
                    formatDecimal(row.probability),
                    formatDecimal(row.cumulativeProbability),
                    formatDecimal(row.referenceLevel),
                    row.newClassNumber,
                    row.difference,
                    row.shift,
                ),
            )
        treeview.insert(
            "",
            "end",
            values=(
                "Σ",
                "",
                "",
                sum(row.pixelCount for row in table),
                formatDecimal(sum(row.probability for row in table)),
                "", "", "", "", "",
            ),
        )

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
        treeview.configure(yscrollcommand=scrollbar.set)
        treeview.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
