from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pandas as pd
import requests


class CocktailDetailWindow(QWidget):
    def __init__(self, cocktail_data: pd.Series, theme="light"):
        super().__init__()
        self.current_theme = theme
        self.setWindowTitle(cocktail_data.get("strDrink", "Cocktail"))
        self.resize(600, 800)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # IMAGE AT TOP OF PAGE
        thumb = cocktail_data.get("strDrinkThumb", "")
        if isinstance(thumb, str) and thumb.startswith("http"):
            try:
                resp = requests.get(thumb, timeout=5)
                resp.raise_for_status()
                pix = QPixmap()
                pix.loadFromData(resp.content)
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label.setPixmap(
                    pix.scaledToWidth(
                        300,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
                layout.addWidget(img_label)
            except Exception:
                no_img = QLabel("No image available")
                no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_img)
        else:
            no_img = QLabel("No image available")
            no_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_img)

        # INGREDIENTS FIELD
        ingredients = []
        for i in range(1, 16):
            ing = cocktail_data.get(f"strIngredient{i}")
            meas = cocktail_data.get(f"strMeasure{i}")
            if pd.notna(ing) and ing:
                if pd.notna(meas) and meas:
                    ingredients.append(f"{meas.strip()} {ing.strip()}")
                else:
                    ingredients.append(ing.strip())

        layout.addWidget(QLabel("Ingredients:"))
        ing_text = QTextEdit("\n".join(ingredients))
        ing_text.setReadOnly(True)
        ing_text.setFixedHeight(min(len(ingredients) * 24 + 10, 200))
        layout.addWidget(ing_text)

        # INSTRUCTIONS FIELD
        layout.addWidget(QLabel("Instructions:"))
        instr = cocktail_data.get("strInstructions", "")
        instr_edit = QTextEdit(instr)
        instr_edit.setReadOnly(True)


        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(instr_edit)
        layout.addWidget(scroll, stretch=1)
