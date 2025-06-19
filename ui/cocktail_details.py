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
        self.resize(500, 700)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Image
        thumb = cocktail_data.get("strDrinkThumb", "")
        if isinstance(thumb, str) and thumb.startswith("http"):
            try:
                resp = requests.get(thumb, timeout=5)
                pix = QPixmap()
                pix.loadFromData(resp.content)
                lbl = QLabel()
                lbl.setPixmap(pix.scaledToWidth(300, Qt.SmoothTransformation))
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(lbl)
            except Exception:
                pass

        # Ingredients
        ingredients = []
        for i in range(1, 16):
            ing = cocktail_data.get(f"strIngredient{i}")
            meas = cocktail_data.get(f"strMeasure{i}")
            if pd.notna(ing) and ing:
                text = (
                    f"{meas.strip()} {ing.strip()}"
                    if pd.notna(meas) and meas else ing.strip()
                )
                ingredients.append(text)

        layout.addWidget(QLabel("Ingredients:"))
        ing_text = QTextEdit("\n".join(ingredients))
        ing_text.setReadOnly(True)
        ing_text.setFixedHeight(min(len(ingredients) * 24 + 10, 200))
        layout.addWidget(ing_text)

        # Instructions
        layout.addWidget(QLabel("Instructions:"))
        instr = cocktail_data.get("strInstructions", "")
        instr_text = QTextEdit(instr)
        instr_text.setReadOnly(True)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(instr_text)
        layout.addWidget(scroll)
