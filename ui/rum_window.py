from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QApplication, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from utils.dark_theme import create_dark_palette
from utils.light_theme import create_light_palette
from utils.style_manager import get_table_stylesheet
import pandas as pd
import os
from rapidfuzz import process, fuzz
from ui.userRumRatingWindow import UserRumRatingWindow  # adjust path if needed
from pathlib import Path
import json

# Path to ratings (stored in user's home directory)
USER_RUM_RATING_FILE = Path.home() / ".alko_user_rum_ratings.json"

def get_assets_path():
    # Return correct path to 'assets' directory
    # - In .exe mode: use the unpacked PyInstaller directory
    # - In dev: return absolute path to project-local folder
    import sys
    import os
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets')
    return os.path.abspath('assets')


class RumRatingsWindow(QWidget):
    """Window for displaying rum products with review data and user ratings."""
    def __init__(self, alko_df: pd.DataFrame, theme="light"):
        super().__init__()
        self.setWindowTitle("Rum Ratings Window")
        self.resize(1400, 800)
        self.current_theme = theme
        self.layout = QVBoxLayout(self)
        self.alko_df = alko_df


        # Title label + info
        title_label = QLabel("Rum Ratings Window")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        # Info Text
        info_label = QLabel(
            "Browse and compare the Alko.fi websites rum products by value and product ratings. \n"
            "You can also add your own ratings to the rum products below."
        )
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Arial", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(info_label)

        # Buttons row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Theme Toggle Button
        self.theme_button = QPushButton(
            "Switch to Dark Mode" if self.current_theme == "light" else "Switch to Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)

        # Open user rating input window
        self.btn_user_rating = QPushButton("Rate Rums Yourself")
        self.btn_user_rating.clicked.connect(self.open_user_rating_window)
        button_layout.addWidget(self.btn_user_rating)

        self.layout.addLayout(button_layout)

        # Product Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.layout.addWidget(self.table)

        self.load_data(alko_df)     # Populate table with alko dataframe
        QTimer.singleShot(0, self.adjust_column_widths) # delay resize
        self.apply_table_stylesheet()

    def apply_table_stylesheet(self):
        """Apply theme-based stylesheet to the table."""
        self.table.setStyleSheet(get_table_stylesheet(self.current_theme))


    def toggle_theme(self):
        """
        - For choosing Darkmode/lightmode
        - Update darkmode button text
        - Restyle table and controls according to theme (darkmode etc.)
        - Broadcast theme to other open windows (so whiskey_window and main_window also gets darkmode upon activation)
        """
        if self.current_theme == "light":
            QApplication.instance().setPalette(create_dark_palette())
            self.current_theme = "dark"
            self.theme_button.setText("Switch to Light Mode")
        else:
            QApplication.instance().setPalette(create_light_palette())
            self.current_theme = "light"
            self.theme_button.setText("Switch to Dark Mode")

        self.apply_table_stylesheet()

        # Update all open windows with the new theme
        for w in QApplication.instance().topLevelWidgets():
            if w is self:
                continue
            if hasattr(w, "current_theme") and hasattr(w, "apply_table_stylesheet"):
                w.current_theme = self.current_theme
                w.apply_table_stylesheet()
                if hasattr(w, "theme_button"):
                    if w.current_theme == "dark":
                        w.theme_button.setText("Switch to Light Mode")
                    else:
                        w.theme_button.setText("Switch to Dark Mode")


    def load_data(self, alko_df):
        # Load RumHowler ratings
        ratings_path = os.path.join(get_assets_path(), "rumhowler_data.xlsx")
        if not os.path.exists(ratings_path):
            return

        ratings_df = pd.read_excel(ratings_path)
        ratings_df["Rum_clean"] = ratings_df["Rum"].str.lower().str.strip()     # Strip and standardize items

        # Filter rums from Alko data
        rums_df = alko_df[alko_df["Tyyppi"].str.contains("rommi", case=False, na=False)].copy()     # Filter by rums

        # Match & assign ratings using Fuzzymatch
        scores, review_counts, sources = [], [], []
        for product_name in rums_df["Tuotenimi"]:
            name_clean = product_name.lower().strip()
            match = process.extractOne(name_clean, ratings_df["Rum_clean"], scorer=fuzz.token_sort_ratio)
            if match and match[1] >= 90:    # match treshhold 90
                matched_row = ratings_df[ratings_df["Rum_clean"] == match[0]]
                score = matched_row["Score"].values[0]
                count = matched_row["ReviewCount"].values[0] if "ReviewCount" in matched_row.columns else None
                source = matched_row["Source"].values[0] if "Source" in matched_row.columns else ""
            else:
                score = None
                count = None
                source = ""
            scores.append(score)
            review_counts.append(count)
            sources.append(source)

        # Append review info to Alko DataFrame
        rums_df["Rating"] = scores
        rums_df["ReviewCount"] = review_counts
        rums_df["Source"] = sources

        # Load users own ratings
        if USER_RUM_RATING_FILE.exists():
            with open(USER_RUM_RATING_FILE, "r", encoding="utf-8") as f:
                user_ratings = json.load(f)
        else:
            user_ratings = {}

        rums_df["MyRating"] = rums_df["Tuotenimi"].apply(lambda name: user_ratings.get(name, ""))

        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Product Name", "Price (€)", "Alcohol (%)", "Size (L)", "Alcohol per €", "Rating (0–100)", "Review Count", "My Rating", "Source"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Populate table
        self.table.setRowCount(len(rums_df))
        for row, (_, product) in enumerate(rums_df.iterrows()):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["Tuotenimi"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{product['Hinta']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['Alkoholi%']:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['Pullokoko (l)']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product['AlcoholPerEuro']:.4f}"))
            self.table.setItem(row, 5, QTableWidgetItem("" if pd.isna(product["Rating"]) else str(product["Rating"])))
            self.table.setItem(row, 6, QTableWidgetItem("" if pd.isna(product["ReviewCount"]) else str(product["ReviewCount"])))
            self.table.setItem(row, 7, QTableWidgetItem(str(product["MyRating"])))
            self.table.setItem(row, 8, QTableWidgetItem("" if pd.isna(product["Source"]) else str(product["Source"])))


            for col in range(9):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def open_user_rating_window(self):
        """Open a window for entering personal rum ratings."""
        product_names = [self.table.item(row, 0).text() for row in range(self.table.rowCount())]
        unique_names = sorted(set(product_names))
        self.rating_window = UserRumRatingWindow(unique_names, USER_RUM_RATING_FILE, self.current_theme)
        self.rating_window.saved.connect(lambda: (self.load_data(self.alko_df), QTimer.singleShot(0, self.adjust_column_widths)))
        self.rating_window.show()

    def resizeEvent(self, event):
        """Ensure columns are resized"""
        super().resizeEvent(event)
        self.adjust_column_widths()

    def adjust_column_widths(self):
        """Resize columns proportionally based on weights. (name column wider than price etc.)"""
        column_weights = [20, 10, 10, 10, 10.5, 10, 10, 10, 15]
        total_weight = sum(column_weights)
        table_width = self.table.viewport().width()
        for i, weight in enumerate(column_weights):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(i, int((weight / total_weight) * table_width))
