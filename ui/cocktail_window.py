import os
import json
from pathlib import Path
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QLabel, QHBoxLayout, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from utils.style_manager import get_table_stylesheet, get_search_input_stylesheet
from ui.cocktail_details import CocktailDetailWindow
from ui.barshelf_window import BarShelfWindow
from utils.ingredients_mapper import normalize_ingredient, FAMILY_OF

CONFIG_PATH = Path.home() / ".alko_app_shelf.json"

class CocktailsWindow(QWidget):
    def __init__(self, csv_path: str, theme="light"):
        super().__init__()
        self.current_theme = theme
        # Window title and size
        self.setWindowTitle("Cocktail List")
        self.resize(1100, 900)

        # Load data
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        self.df_all = pd.read_csv(csv_path) # Read CSV into pandas

        # Build ingredient list for each row
        def make_ing_list(row):
            out = []
            for i in range(1, 16):
                raw = row.get(f"strIngredient{i}")
                if pd.notna(raw) and raw.strip():   # Normalize
                    out.append(normalize_ingredient(raw))
            return out

        self.df_all["ingredients_list"] = self.df_all.apply(make_ing_list, axis=1)
        # df_current holds whatever subset we are showing
        self.df_current = self.df_all.copy()

        # LAYOUT SETUP
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # search + buttons row
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        # Search-by-name
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by name…")
        self.search_input.textChanged.connect(self.apply_filters)
        self.search_input.setStyleSheet(    # Apply styling to the line edit
            get_search_input_stylesheet(self.current_theme)
        )
        search_layout.addWidget(self.search_input, stretch=1)

        # Manage My Bar button
        self.btn_manage_bar = QPushButton("Manage My Bar")
        self.btn_manage_bar.clicked.connect(self.open_barshelf)
        search_layout.addWidget(self.btn_manage_bar)

        # What Can I Make button
        self.btn_show_mine = QPushButton("What Can I Make?")
        self.btn_show_mine.clicked.connect(self.show_makeable)
        search_layout.addWidget(self.btn_show_mine)

        layout.addLayout(search_layout)

        # 3-column list: Category, Name, Ingredients
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Drink Type", "Name", "Ingredients"])
        # Stretch columns to fill width
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        # INGREDIENT FILTER DROPDOWN
        self.ing_combo = QComboBox()
        self.ing_combo.setMinimumWidth(200)
        self.ing_combo.setEditable(False)
        self.ing_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.ing_combo.setPlaceholderText("Filter by ingredients…")
        search_layout.addWidget(self.ing_combo)

        # Group all ingredients by their “family”
        all_ings = sorted({ing for lst in self.df_all["ingredients_list"] for ing in lst})
        groups = {}
        for ing in all_ings:
            fam = FAMILY_OF.get(ing, "Other")
            groups.setdefault(fam, []).append(ing)

        # define the order in which families appear
        family_order = ["Spirits", "Liqueurs", "Wines and Vermouths", "Mixers", "Garnishes", "Fruits and Vegetables", "Sweeteners", "Other"]

        model = QStandardItemModel()

        # Invisible “placeholder” so the box shows fixed text (needed for filter button text)
        placeholder = QStandardItem("Ingredient Filters")
        placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
        model.appendRow(placeholder)

        # For each "family", add a non-selectable header, then its ingredients
        for fam in family_order:
            if fam in groups:
                # header (non‐selectable divider)
                header = QStandardItem(f"— {fam} —")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                model.appendRow(header)
                # then each ingredient under that family
                for ing in sorted(groups[fam]):
                    item = QStandardItem(ing)
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
                    model.appendRow(item)
        self.ing_combo.setModel(model)
        self.ing_combo.setCurrentIndex(0) # Needed for displaying "Filter Ingredients" on the dropdown
        self.ing_combo.view().setRowHidden(0, True) # For hiding "Filter Ingredients"
        model.itemChanged.connect(self.apply_filters) # Re-apply filter each time a checkbox changes


        # Populate Table
        self.apply_filters()  # will populate self.df_current

        # Double-click a row to open details
        self.apply_table_stylesheet()
        self.table.cellDoubleClicked.connect(self.open_detail)


    def apply_filters(self):
        term = self.search_input.text().strip().lower()

        # 1) Name filter (case-insensitive substring match)
        if term:
            df = self.df_all[self.df_all["strDrink"]
            .str.contains(term, case=False, regex=False)]
        else:
            df = self.df_all

        # 2) Ingredient filter (must contain all checked ingredients)
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
        """Fill the table with Category, Name, and Ingredients."""
        self.table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            # Column 0: Category, centered
            cat_item = QTableWidgetItem(str(row.get("strCategory", "")))
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, cat_item)

            # Column 1: Cocktail name
            self.table.setItem(i, 1, QTableWidgetItem(row.get("strDrink", "")))

            # Column 2: ingredients
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
        """Apply light/dark theme CSS to table."""
        self.table.setStyleSheet(get_table_stylesheet(self.current_theme))
        self.search_input.setStyleSheet(get_search_input_stylesheet(self.current_theme))

    def open_detail(self, row, _col):
        """On double-click, open a detail window for cocktail."""
        data = self.df_current.iloc[row]
        self.detail_window = CocktailDetailWindow(data, self.current_theme)
        self.detail_window.show()

    def open_barshelf(self):
        """Open the BarShelfWindow, passing in all ingredients."""
        all_ing = sorted({ing for lst in self.df_all["ingredients_list"] for ing in lst})
        self.barshelf = BarShelfWindow(all_ing, CONFIG_PATH)
        self.barshelf.saved.connect(self.apply_filters)
        self.barshelf.show()


    def show_makeable(self):
        """Show cocktails whose ingredients are all in the user’s saved bar."""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r") as f:
                have = set(json.load(f))
        else:
            have = set()

        df = self.df_all[
            self.df_all["ingredients_list"]
                .apply(lambda ings: all(i in have for i in ings))
        ]
        self.df_current = df
        self._populate_table(df)