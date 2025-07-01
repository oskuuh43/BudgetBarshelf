import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton, QHBoxLayout, QLabel, QLineEdit
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from utils.style_manager import get_search_input_stylesheet


"""
userRumRatingWindow.py

Popup window that allows users to input their own ratings for rums.
Results are saved in a local JSON file and reloaded in the main app.
"""

class UserRumRatingWindow(QWidget):
    saved = pyqtSignal() # Saving ratings between startups

    def __init__(self, product_names: list[str], config_path: Path, theme="light"):
        super().__init__()
        self.setWindowTitle("Rate Rums Yourself")
        self.resize(500, 600)

        self.config_path = config_path  # Path to save user ratings to JSON file
        self.current_theme = theme      # Light/dark theme identifier
        self.all_product_names = sorted(product_names)  # Full sorted list of rum names

        # Load existing user ratings from file if it exists
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.saved_ratings = json.load(f)
        else:
            self.saved_ratings = {}

        self.fields = {}    # Dict to map product name -> QLineEdit
        self.layout = QVBoxLayout(self) # Main layout for this window

        #  Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search rums...")
        self.search_bar.textChanged.connect(self.filter_products)   # Refilter on typing
        self.layout.addWidget(self.search_bar)

        #  Scrollable Area for Rum Inputs
        self.scroll = QScrollArea()
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll.setWidget(self.scroll_container)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        # Add all rum name inputs initially
        self.populate_fields(self.all_product_names)

        #  Save/Cancel Buttons
        btns = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.clicked.connect(self._save_and_close)  # Save + emit signal
        btn_cancel.clicked.connect(self.close)          # Close
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        self.layout.addLayout(btns)

    def populate_fields(self, filtered_names: list[str]):
        """
        Rebuilds the scrollable input list using only `filtered_names`.
        Clears old inputs and replaces with matching ones.
        """
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.fields.clear()

        # Add a label and input field for each product
        for name in filtered_names:
            label = QLabel(name)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            field = QLineEdit()
            field.setPlaceholderText("Enter rating (0–100)")
            if name in self.saved_ratings:
                field.setText(str(self.saved_ratings[name]))    # Pre-fill if already rated
            self.scroll_layout.addWidget(label)
            self.scroll_layout.addWidget(field)
            self.fields[name] = field
        self.apply_table_stylesheet()     # Apply correct theme styling to new fields

    def filter_products(self, text: str):
        """
        Filters the rum list based on the search bar text
        """
        query = text.strip().lower()
        if not query:
            filtered = self.all_product_names
        else:
            filtered = [name for name in self.all_product_names if query in name.lower()]
        self.populate_fields(filtered)

    def apply_table_stylesheet(self):
        """
        Applies styling based on the current theme dark/light.
        """
        self.search_bar.setStyleSheet(get_search_input_stylesheet(self.current_theme))
        for field in self.fields.values():
            field.setStyleSheet(get_search_input_stylesheet(self.current_theme))

    def _save_and_close(self):
        """
        Saves all user ratings to the JSON file and closes the window.
        Also emits `saved` signal to notify other windows.
        """
        updated_ratings = self.saved_ratings.copy()

        for name, field in self.fields.items():
            text = field.text().strip()
            if text.isdigit() and 0 <= int(text) <= 100:    # Accept only digits between 0–100
                updated_ratings[name] = int(text)
            elif name in updated_ratings:
                del updated_ratings[name]   # If field is empty, remove old rating

        os.makedirs(self.config_path.parent, exist_ok=True) # Save to file
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(updated_ratings, f, indent=2, ensure_ascii=False)

        self.saved.emit()
        self.close()