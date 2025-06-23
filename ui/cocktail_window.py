import os
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from utils.style_manager import get_table_stylesheet
from ui.cocktail_details import CocktailDetailWindow

class CocktailsWindow(QWidget):
    def __init__(self, csv_path: str, theme="light"):
        super().__init__()
        self.current_theme = theme
        self.setWindowTitle("Cocktail List")
        self.resize(1000, 800)

        # load all data once
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        self.df_all = pd.read_csv(csv_path)
        self.df_current = self.df_all.copy()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- SEARCH BAR ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name…")
        self.search_input.textChanged.connect(self.apply_search)
        search_layout.addWidget(self.search_input, stretch=1)
        layout.addLayout(search_layout)

        # 3-column list: Category, Name, Ingredients
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Drink Type", "Name", "Ingredients"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        # initial population
        self.apply_search()  # will populate self.df_current

        # Style & hook up double-click
        self.apply_table_stylesheet()
        self.table.cellDoubleClicked.connect(self.open_detail)

    def apply_search(self):
        term = self.search_input.text().strip().lower()
        if term:
            mask = self.df_all["strDrink"] \
                          .str.contains(term, case=False, regex=False)
            df = self.df_all[mask]
        else:
            df = self.df_all

        self.df_current = df
        self._populate_table(df)

    def _populate_table(self, df: pd.DataFrame):
        """Fill the table with Category, Name, and comma-separated Ingredients."""
        self.table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            # Category
            cat_item = QTableWidgetItem(str(row.get("strCategory", "")))
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, cat_item)

            # Name
            self.table.setItem(i, 1, QTableWidgetItem(row.get("strDrink", "")))

            # Ingredients (comma-list, full list on hover)
            ingredients = []
            for j in range(1, 16):
                ing = row.get(f"strIngredient{j}")
                meas = row.get(f"strMeasure{j}")
                if pd.notna(ing) and ing:
                    if pd.notna(meas) and meas:
                        ingredients.append(f"{meas.strip()} {ing.strip()}")
                    else:
                        ingredients.append(ing.strip())
            ing_text = ", ".join(ingredients)
            ing_item = QTableWidgetItem(ing_text)
            ing_item.setToolTip("\n".join(ingredients))
            self.table.setItem(i, 2, ing_item)

    def apply_table_stylesheet(self):
        """Apply light/dark theme CSS to our table."""
        self.table.setStyleSheet(get_table_stylesheet(self.current_theme))

    def open_detail(self, row, _col):
        """On double-click, open a detail window for that cocktail."""
        data = self.df_current.iloc[row]
        self.detail_window = CocktailDetailWindow(data, self.current_theme)
        self.detail_window.show()
