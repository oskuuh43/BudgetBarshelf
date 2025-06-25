import os
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QLabel, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from utils.style_manager import get_table_stylesheet
from ui.cocktail_details import CocktailDetailWindow
from utils.ingredients_mapper import normalize_ingredient

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

        def make_ing_list(row):
            out = []
            for i in range(1, 16):
                raw = row.get(f"strIngredient{i}")
                if pd.notna(raw) and raw.strip():
                    out.append(normalize_ingredient(raw))
            return out

        self.df_all["ingredients_list"] = self.df_all.apply(make_ing_list, axis=1)
        self.df_current = self.df_all.copy()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- SEARCH BAR ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name…")
        self.search_input.textChanged.connect(self.apply_filters)
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

        self.ing_combo = QComboBox()
        self.ing_combo.setMinimumWidth(200)
        self.ing_combo.setEditable(False)
        self.ing_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.ing_combo.setPlaceholderText("Filter by ingredients…")
        search_layout.addWidget(self.ing_combo)


        # populate all unique canonical ingredients:
        all_ings = sorted({ing for lst in self.df_all["ingredients_list"] for ing in lst})
        model = QStandardItemModel()
        for ing in all_ings:
            item = QStandardItem(ing)
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
            model.appendRow(item)
        self.ing_combo.setModel(model)
        model.itemChanged.connect(self.apply_filters)


        # initial population
        self.apply_filters()  # will populate self.df_current

        # Style & hook up double-click
        self.apply_table_stylesheet()
        self.table.cellDoubleClicked.connect(self.open_detail)

    def apply_filters(self):
        term = self.search_input.text().strip().lower()

        # 1) name filter
        if term:
            df = self.df_all[self.df_all["strDrink"]
            .str.contains(term, case=False, regex=False)]
        else:
            df = self.df_all

        # 2) ingredient filter
        checked = [
            self.ing_combo.model().item(row).text()
            for row in range(self.ing_combo.model().rowCount())
            if self.ing_combo.model().item(row).checkState() == Qt.CheckState.Checked
        ]
        if checked:
            df = df[df["ingredients_list"]
            .apply(lambda ings: all(chip in ings for chip in checked))]

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
