from PyQt6.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow
from utils.dark_theme import create_dark_palette
from utils.light_theme import create_light_palette
import darkdetect

def main():
    app = QApplication(sys.argv)

    if darkdetect.isDark():
        app.setPalette(create_dark_palette())
        initial_theme = "dark"
    else:
        app.setPalette(create_light_palette())
        initial_theme = "light"

    window = MainWindow(initial_theme)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
