import os
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.style_manager import get_table_stylesheet
from ui.cocktail_details import CocktailDetailWindow


class CocktailsWindow(QWidget):
    def __init__(self, csv_path: str, theme="light"):
        super().__init__()
        print("CocktailsWindow.__init__() start")
        self.current_theme = theme
        self.setWindowTitle("Cocktail List")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Simple 3-column list
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Ingredients"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        print("Reading CSV…")
        self.df = pd.read_csv(csv_path)
        print(f"Loaded {len(self.df)} rows")

        # Populate now that df is loaded
        self._populate_table()
        print("Table populated")

        # Style & hook up double-click
        self.apply_table_stylesheet()
        self.table.cellDoubleClicked.connect(self.open_detail)
        print("CocktailsWindow.__init__() end")

    def _populate_table(self):
        """Fill the table with ID, Name, and comma-separated Ingredients."""
        self.table.setRowCount(len(self.df))
        for row_idx, row in self.df.iterrows():
            # ID
            id_val = row.get("Unnamed: 0", row_idx)
            item = QTableWidgetItem(str(id_val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item)

            # Name
            name = row.get("strDrink", "")
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))

            # Ingredients (comma-list, full list on hover)
            ingredients = []
            for i in range(1, 16):
                ing = row.get(f"strIngredient{i}")
                meas = row.get(f"strMeasure{i}")
                if pd.notna(ing) and ing:
                    text = (
                        f"{meas.strip()} {ing.strip()}"
                        if pd.notna(meas) and meas else ing.strip()
                    )
                    ingredients.append(text)
            ing_text = ", ".join(ingredients)
            ing_item = QTableWidgetItem(ing_text)
            ing_item.setToolTip("\n".join(ingredients))
            self.table.setItem(row_idx, 2, ing_item)

    def apply_table_stylesheet(self):
        """Apply light/dark theme CSS to our table."""
        self.table.setStyleSheet(get_table_stylesheet(self.current_theme))

    def open_detail(self, row, _col):
        """On double-click, open a detail window for that cocktail."""
        data = self.df.iloc[row]
        self.detail_window = CocktailDetailWindow(data, self.current_theme)
        self.detail_window.show()
