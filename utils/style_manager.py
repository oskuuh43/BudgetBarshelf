def get_table_stylesheet(theme: str) -> str:
    if theme == "dark":
        return """
            QTableWidget {
                background-color: palette(base);
                alternate-background-color: palette(alternate-base);
                color: palette(text);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
                gridline-color: palette(dark);
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:!selected:hover {
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: palette(alternate-base);
                color: palette(text);
                font-weight: bold;
                padding: 4px;
                border: 1px solid palette(dark);
            }
        """
    else:
        return """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                color: black;
                selection-background-color: #d0e7ff;
                selection-color: black;
                gridline-color: #ccc;
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:!selected:hover {
                background-color: #f2f2f2;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                color: black;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #ddd;
            }
        """

def get_dropdown_stylesheet(theme: str) -> str:
    if theme == "dark":
        return ""
    else:
        return """
            QComboBox {
                border: 1px solid gray;
                padding: 4px;
                background-color: white;
                color: black;
            }
        """

def get_search_input_stylesheet(theme: str) -> str:
    if theme == "dark":
        return ""
    else:
        return """
            QLineEdit {
                border: 1px solid gray;
                padding: 4px;
                background-color: white;
                color: black;
            }
        """
