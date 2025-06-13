from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def create_light_palette():
    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(30, 120, 200))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)

    return palette
