from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.dark_theme import create_dark_palette
from utils.light_theme import create_light_palette
from utils.style_manager import get_table_stylesheet
import pandas as pd
import os
from rapidfuzz import process, fuzz

class WhiskeyRatingsWindow(QWidget):
    def __init__(self, alko_df: pd.DataFrame, theme="light"):
        super().__init__()
        self.setWindowTitle("Whiskey Ratings from WhiskyScores")
        self.resize(1300, 800)
        self.current_theme = theme

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Theme toggle button
        self.theme_button = QPushButton(
            "Switch to Dark Mode" if self.current_theme == "light" else "Switch to Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_button)

        title_label = QLabel("Whiskey Ratings from WhiskyScores")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        info_label = QLabel(
            "The whiskey ratings below are primarily scraped from WhiskyScores.com.\n"
            "Additional ratings have been manually gathered from other whiskey rating sites.\n"
            "Product names have been manually adjusted to better match Alko's naming conventions."
        )
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Arial", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(info_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Product Name", "Price (€)", "Alcohol (%)", "Size (L)", "Alcohol per €", "Rating (0-100)", "Review Count", "Source"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)



        self.apply_table_stylesheet()
        self.load_data(alko_df)

    def apply_table_stylesheet(self):
        self.table.setStyleSheet(get_table_stylesheet(self.current_theme))

    def toggle_theme(self):
        """
        - For choosing Darkmode/lightmode
        - Update darkmode button text
        - Restyle table and controls according to theme (darkmode etc.)
        - Broadcast theme to other open windows (so rum_window and main_window also gets darkmode upon activation)
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
        ratings_path = os.path.join("assets", "whiskey_scores_data.xlsx")
        if not os.path.exists(ratings_path):
            return

        ratings_df = pd.read_excel(ratings_path)

        # Clean and simplify whiskey names
        ratings_df["Whiskey_clean"] = (
            ratings_df["Whiskey"]
            .astype(str)
            .str.lower()
            .str.replace(r"[^a-z0-9\s]", "", regex=True)  # remove punctuation
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Filter Alko whiskey products
        whiskey_df = alko_df[alko_df["Tyyppi"].str.contains("viski", case=False, na=False)].copy()
        whiskey_df["Tuotenimi_clean"] = (
            whiskey_df["Tuotenimi"]
            .astype(str)
            .str.lower()
            .str.replace(r"[^a-z0-9\s]", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Match and assign scores using Fuzzymatch
        scores = []
        review_counts = []
        sources = []
        for name in whiskey_df["Tuotenimi_clean"]:
            match = process.extractOne(name, ratings_df["Whiskey_clean"], scorer=fuzz.token_sort_ratio)
            if match and match[1] >= 75:
                matched_row = ratings_df[ratings_df["Whiskey_clean"] == match[0]]
                score = matched_row["Score"].values[0]
                count = matched_row["ReviewCount"].values[0]
                # FIXED: Reliable fallback to check for actual column name
                if "Website" in matched_row.columns:
                    source = matched_row["Website"].values[0]
                elif "Source" in matched_row.columns:
                    source = matched_row["Source"].values[0]
                else:
                    source = ""
            else:
                score = None
                count = None
                source = ""
            scores.append(score)
            review_counts.append(count)
            sources.append(source)

        whiskey_df["Rating"] = scores
        whiskey_df["ReviewCount"] = review_counts
        whiskey_df["Source"] = sources

        # Populate the table
        self.table.setRowCount(len(whiskey_df))
        for row, (_, product) in enumerate(whiskey_df.iterrows()):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["Tuotenimi"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{product['Hinta']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['Alkoholi%']:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['Pullokoko (l)']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product['AlcoholPerEuro']:.4f}"))
            self.table.setItem(row, 5, QTableWidgetItem("" if pd.isna(product["Rating"]) else str(product["Rating"])))
            self.table.setItem(row, 6, QTableWidgetItem("" if pd.isna(product["ReviewCount"]) else str(product["ReviewCount"])))
            self.table.setItem(row, 7, QTableWidgetItem("" if pd.isna(product["Source"]) else str(product["Source"])))

            for col in range(8):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)