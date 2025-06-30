import json
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QPushButton, QHBoxLayout, QLabel, QLineEdit
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class UserWhiskeyRatingsWindow(QWidget):
    saved = pyqtSignal()

    def __init__(self, product_names: list[str], config_path: Path):
        super().__init__()
        self.setWindowTitle("Rate Whiskeys Yourself")
        self.resize(500, 600)
        self.config_path = config_path
        self.all_product_names = sorted(product_names)

        # Load existing user ratings
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.saved_ratings = json.load(f)
        else:
            self.saved_ratings = {}

        self.fields = {}
        self.layout = QVBoxLayout(self)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search whiskeys...")
        self.search_bar.textChanged.connect(self.filter_products)
        self.layout.addWidget(self.search_bar)

        # Scrollable area
        self.scroll = QScrollArea()
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll.setWidget(self.scroll_container)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.populate_fields(self.all_product_names)

        # Buttons
        btns = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.clicked.connect(self._save_and_close)
        btn_cancel.clicked.connect(self.close)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        self.layout.addLayout(btns)

    def populate_fields(self, filtered_names: list[str]):
        # Clear layout
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.fields.clear()

        for name in filtered_names:
            label = QLabel(name)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            field = QLineEdit()
            field.setPlaceholderText("Enter rating (0–100)")
            if name in self.saved_ratings:
                field.setText(str(self.saved_ratings[name]))
            self.scroll_layout.addWidget(label)
            self.scroll_layout.addWidget(field)
            self.fields[name] = field

    def filter_products(self, text: str):
        query = text.strip().lower()
        if not query:
            filtered = self.all_product_names
        else:
            filtered = [name for name in self.all_product_names if query in name.lower()]
        self.populate_fields(filtered)

    def _save_and_close(self):
        # Start with existing ratings
        updated_ratings = self.saved_ratings.copy()

        # Update only the visible ratings
        for name, field in self.fields.items():
            text = field.text().strip()
            if text.isdigit() and 0 <= int(text) <= 100:
                updated_ratings[name] = int(text)
            elif name in updated_ratings:
                # If user cleared the field, remove rating
                del updated_ratings[name]

        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(updated_ratings, f, indent=2, ensure_ascii=False)

        self.saved.emit()
        self.close()

