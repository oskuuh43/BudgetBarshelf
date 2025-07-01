from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pandas as pd
import requests


class CocktailDetailWindow(QWidget):
    def __init__(self, cocktail_data: pd.Series):
        super().__init__()
        self.setWindowTitle(cocktail_data.get("strDrink", "Cocktail"))  # Set the window title to the cocktail’s name
        self.resize(600, 800)   # Window Size

        # Main layout for image + ingredients + instructions
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # IMAGE AT TOP OF PAGE
        thumb = cocktail_data.get("strDrinkThumb", "")
        if isinstance(thumb, str) and thumb.startswith("http"):
            try:
                # Fetch the Image
                resp = requests.get(thumb, timeout=5)
                resp.raise_for_status()
                pix = QPixmap()
                pix.loadFromData(resp.content)
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # Scale to width 300px
                img_label.setPixmap(
                    pix.scaledToWidth(
                        300,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                layout.addWidget(img_label)
            except Exception:
                # On fetch/render error, show “No image available”
                no_img = QLabel("No image available")
                no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_img)
        else:
            # No valid URL -> Same Result
            no_img = QLabel("No image available")
            no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_img)

        # INGREDIENTS FIELD
        ingredients = []
        # Build a list of measures and ingredients
        for i in range(1, 16):
            ing = cocktail_data.get(f"strIngredient{i}")
            meas = cocktail_data.get(f"strMeasure{i}")
            if pd.notna(ing) and ing:
                if pd.notna(meas) and meas:
                    ingredients.append(f"{meas.strip()} {ing.strip()}")
                else:
                    ingredients.append(ing.strip())

        layout.addWidget(QLabel("Ingredients:"))
        # Use QTextEdit to show info
        ing_text = QTextEdit("\n".join(ingredients))
        ing_text.setReadOnly(True)
        ing_text.setFixedHeight(min(len(ingredients) * 24 + 10, 200))
        layout.addWidget(ing_text)

        # INSTRUCTIONS FIELD
        layout.addWidget(QLabel("Instructions:"))
        instr = cocktail_data.get("strInstructions", "")
        instr_edit = QTextEdit(instr)
        instr_edit.setReadOnly(True)

        # Wrap the instructions in a scroll area.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(instr_edit)
        layout.addWidget(scroll, stretch=1)
