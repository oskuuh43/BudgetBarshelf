from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def create_dark_palette():
    palette = QPalette()

    # Backgrounds
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))

    # Text
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)

    # Buttons
    palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))

    # Highlights
    palette.setColor(QPalette.ColorRole.Highlight, QColor(90, 150, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    return palette
