from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.dark_theme import create_dark_palette
from utils.light_theme import create_light_palette
import pandas as pd
import os
from rapidfuzz import process, fuzz

class RumRatingsWindow(QWidget):
    def __init__(self, alko_df: pd.DataFrame, theme="light"):
        super().__init__()
        self.setWindowTitle("Rum Ratings from the Rum Howler Blog")
        self.resize(1100, 700)
        self.current_theme = theme

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Theme toggle button
        self.theme_button = QPushButton(
            "Switch to Dark Mode" if self.current_theme == "light" else "Switch to Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_button)

        # Title label
        title_label = QLabel("Rum Ratings from the Rum Howler Blog")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        info_label = QLabel(
            "The rum ratings below are scraped from the Rum Howler Blog (therumhowlerblog.com).\n"
            "Product names have been manually adjusted after scraping to better match Alko's naming."
        )
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Arial", 10))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(info_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Product Name", "Price (€)", "Alcohol (%)", "Size (L)", "Alcohol per €", "Rating (0-100)"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                selection-background-color: #d0e7ff;
                selection-color: black;
                gridline-color: #ccc;
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #ddd;
            }
            QTableWidget::item:hover:!selected {
                background-color: transparent;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.load_data(alko_df)

    def apply_table_stylesheet(self):
        if self.current_theme == "dark":
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: palette(base);
                    alternate-background-color: palette(alternate-base);
                    color: palette(text);
                    selection-background-color: palette(highlight);
                    selection-color: palette(highlighted-text);
                    gridline-color: palette(dark);
                    font-size: 11pt;
                }
                QHeaderView::section {
                    background-color: palette(alternate-base);
                    color: palette(text);
                    font-weight: bold;
                    border: 1px solid palette(dark);
                }
            """)
        else:
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f2f2f2;
                    color: black;
                    selection-background-color: #d0e7ff;
                    selection-color: black;
                    gridline-color: #ccc;
                    font-size: 11pt;
                }
                QHeaderView::section {
                    background-color: #f2f2f2;
                    color: black;
                    font-weight: bold;
                    border: 1px solid #ddd;
                }
            """)


    def toggle_theme(self):
        if self.current_theme == "light":
            QApplication.instance().setPalette(create_dark_palette())
            self.current_theme = "dark"
            self.theme_button.setText("Switch to Light Mode")
        else:
            QApplication.instance().setPalette(create_light_palette())
            self.current_theme = "light"
            self.theme_button.setText("Switch to Dark Mode")

        self.apply_table_stylesheet()

    def load_data(self, alko_df):
        # Load RumHowler ratings
        ratings_path = os.path.join("assets", "rumhowler_data.xlsx")
        if not os.path.exists(ratings_path):
            return

        ratings_df = pd.read_excel(ratings_path)

        # Filter rums from Alko data
        rums_df = alko_df[alko_df["Tyyppi"].str.contains("rommi", case=False, na=False)].copy()

        ratings_df["Rum_clean"] = ratings_df["Rum"].str.lower().str.strip()

        # Match & assign ratings
        scores = []
        for product_name in rums_df["Tuotenimi"]:
            name_clean = product_name.lower().strip()
            match = process.extractOne(name_clean, ratings_df["Rum_clean"], scorer=fuzz.token_sort_ratio)
            if match and match[1] >= 90:
                score = ratings_df.loc[ratings_df["Rum_clean"] == match[0], "Score"].values[0]
            else:
                score = None
            scores.append(score)

        rums_df["Rating"] = scores

        # Populate table
        self.table.setRowCount(len(rums_df))
        for row, (_, product) in enumerate(rums_df.iterrows()):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["Tuotenimi"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{product['Hinta']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['Alkoholi%']:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['Pullokoko (l)']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product['AlcoholPerEuro']:.4f}"))
            self.table.setItem(row, 5, QTableWidgetItem("" if pd.isna(product["Rating"]) else str(product["Rating"])))

            for col in range(6):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
