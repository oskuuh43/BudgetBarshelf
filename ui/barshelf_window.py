import json
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QCheckBox,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

class BarShelfWindow(QWidget):
    # signal emitted after the user saves their bar-shelf
    saved = pyqtSignal()

    def __init__(self, ingredients: list[str], config_path: Path):
        super().__init__()
        self.setWindowTitle("Manage My Bar Shelf")
        self.resize(400, 600)
        self.config_path = config_path

        # Load existing saved shelf (JSON)
        if config_path.exists():
            with open(config_path, "r") as f:
                have = set(json.load(f))
        else:
            have = set()

        layout = QVBoxLayout(self)

        # Scroll area to list all ingredients
        scroll = QScrollArea()
        container = QWidget()
        vbox = QVBoxLayout(container)

        # Dynamically create a checkbox per ingredient
        self.checks: dict[str, QCheckBox] = {}
        for ing in ingredients:
            cb = QCheckBox(ing)
            cb.setChecked(ing in have)  # pre-check if already owned
            vbox.addWidget(cb)
            self.checks[ing] = cb

        container.setLayout(vbox)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Save / Cancel buttons
        btns = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_save.clicked.connect(self._save_and_close)
        btn_cancel.clicked.connect(self.close)
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def _save_and_close(self):
        # Gather the checked ingredients
        picked = [ing for ing, cb in self.checks.items() if cb.isChecked()]

        # Ensure directory exists
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(picked, f, indent=2)

        self.saved.emit()  # let CocktailsWindow know to re-filter
        self.close()
