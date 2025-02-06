"""
Main application file for initializing and running the GUI application.
"""

import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon

from app.controllers.sidebar_controller import SidebarController
from app.controllers.create_data_controller import CreateDataController
from app.controllers.segment_data_controller import SegmentDataController
from app.controllers.analysis_controller import AnalysisPageController

class MainApp(QMainWindow):
    """
    Main window for the application.

    This class initializes the main UI, integrates controllers for handling user interactions,
    and loads application-wide styles.

    Attributes:
        ui (QMainWindow): The loaded UI for the main application window.
        sidebar_controller (SidebarController): Controller for managing sidebar interactions.
        create_data_controller (CreateDataController): Controller for managing 'Create Data' page interactions.
    """
    def __init__(self):
        super().__init__()
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        
        # Correct paths for UI and Icon
        ui_path = os.path.join(base_path, "app", "ui_main.ui")
        icon_path = os.path.join(base_path, "assets", "icons", "main.ico")

        # Load UI
        self.ui = loadUi(ui_path, self)

        # Set Window Icon
        self.setWindowIcon(QIcon(icon_path))

        # Load Controllers
        self.sidebar_controller = SidebarController(self)
        self.create_data_controller = CreateDataController(self)
        self.segment_data_controller = SegmentDataController(self)
        self.analysis_controller = AnalysisPageController(self)

        # Load Styles
        self.load_styles(base_path)

    def load_styles(self, base_path):
        try:
            style_path = os.path.join(base_path, "app", "utils", "styles.json")
            with open(style_path, "r") as file:
                styles = json.load(file)

            stylesheet = ""
            for widget, properties in styles.items():
                style_string = "; ".join(f"{key}: {value}" for key, value in properties.items())
                stylesheet += f"{widget} {{ {style_string} }}\n"

            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error loading styles: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.showMaximized()
    sys.exit(app.exec_())
