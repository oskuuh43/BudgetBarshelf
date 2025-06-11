from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QLabel, QLineEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from data.data_handler import fetch_and_process_data
from datetime import datetime
from ui.rum_window import RumRatingsWindow



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alcohol per Euro Calculator")    # Main Window Title
        self.resize(1100, 700)      # Initial size of main window

        # Global layout for main window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Padding around window edges
        self.layout.setSpacing(15)  # Spacing between elements

        # Title Label Settings
        self.title_label = QLabel("Alcohol per Euro Calculator")
        self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))     # Font size and style
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)         # Centerd Title
        self.layout.addWidget(self.title_label)     # Add title to the layout

        self.updated_label = QLabel("Data not fetched yet")
        self.updated_label.setFont(QFont("Arial", 10))
        self.updated_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.updated_label)

        # Controls layout (Filter, search, buttons)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)

        # Category filter (dropdown)
        self.category_dropdown = QComboBox()
        self.category_dropdown.setEnabled(False)    # Disabled until data loaded
        self.category_dropdown.setMinimumWidth(200) # Min width for dropdown
        self.category_dropdown.currentIndexChanged.connect(self.on_category_change) # Handle selection change

        # Label for dropdown
        self.dropdown_label = QLabel("Filter by Category:")
        self.dropdown_label.setFont(QFont("Arial", 10))
        controls_layout.addWidget(self.dropdown_label)
        controls_layout.addWidget(self.category_dropdown)

        # Search field setup
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.setEnabled(False) # Disabled until data loaded
        self.search_input.textChanged.connect(self.apply_filters) # Handle text input changes

        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input)

        # Fetch button to fetch alkos product data
        self.fetch_button = QPushButton("Fetch Latest Alko Data")
        self.fetch_button.clicked.connect(self.on_fetch_data)
        controls_layout.addWidget(self.fetch_button)

        self.layout.addLayout(controls_layout) # add control row to main layout

        # Button to open Rum Ratings window
        self.rum_ratings_button = QPushButton("View Rum Ratings")
        self.rum_ratings_button.setEnabled(False)
        self.rum_ratings_button.clicked.connect(self.open_rum_window)
        controls_layout.addWidget(self.rum_ratings_button)

        # Table to display product data
        self.table = QTableWidget()
        self.table.setColumnCount(5) # number of columns
        self.table.setHorizontalHeaderLabels([
            "Product name", "Price (€)", "Alcohol (%)", "Size (L)", "Alcohol per €"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # for resizing
        self.table.setAlternatingRowColors(True)    # alternate row colors
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                selection-background-color: #d0e7ff;  /* Light blue highlight on click */
                selection-color: black;
                gridline-color: #ccc;
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #ddd;
            }
            QTableWidget::item:hover:!selected {
                background-color: transparent;  /* No hover highlight unless selected */
}
        """)

        self.layout.addWidget(self.table)   # add table to main layout

    def on_fetch_data(self):
        try:
            df = fetch_and_process_data()   # Download and process the data
            self.df_all = df    # Save dataset to memory

            self.updated_label.setText(
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )

            # Extract categories and add to dropdown
            categories = ["All"] + sorted(df["Tyyppi"].dropna().unique().tolist())
            self.category_dropdown.clear()
            self.category_dropdown.addItems(categories)
            self.category_dropdown.setEnabled(True)
            self.search_input.setEnabled(True)
            self.rum_ratings_button.setEnabled(True)

            self.apply_filters()    # initially populate table with full data
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Data fetch failed:\n{str(e)}")    # error if failed datafetch

    def on_category_change(self):
        self.apply_filters()

    def apply_filters(self):
        if not hasattr(self, "df_all"):
            return

        selected_category = self.category_dropdown.currentText()    # Current selected category
        search_term = self.search_input.text().strip().lower()      # Current Search text

        filtered_df = self.df_all

        # Filter by category if not all products
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["Tyyppi"] == selected_category]

        # Filter by keyword if searchterm written
        if search_term:
            filtered_df = filtered_df[filtered_df["Tuotenimi"].str.lower().str.contains(search_term)]

        self.populate_table(filtered_df)    # Update with filterd data

    def populate_table(self, df):
        self.table.setRowCount(len(df))     # set number of rows
        for row, (_, product) in enumerate(df.iterrows()):
            # Populate cells with relevant data
            self.table.setItem(row, 0, QTableWidgetItem(str(product["Tuotenimi"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{product['Hinta']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['Alkoholi%']:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['Pullokoko (l)']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product['AlcoholPerEuro']:.4f}"))


            # Center alignment in all cells
            for col in range(5):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def open_rum_window(self):
        if hasattr(self, "df_all"):
            self.rum_window = RumRatingsWindow(self.df_all)
            self.rum_window.show()
