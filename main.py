"""
Main application file for initializing and running the GUI application.
"""

import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from app.controllers.sidebar_controller import SidebarController
from app.controllers.create_data_controller import CreateDataController
from app.controllers.segment_data_controller import SegmentDataController

class MainApp(QMainWindow):
    """
    Main window for the application.

    This class initializes the main UI, integrates controllers for handling user interactions,
    and loads application-wide styles.

    Args:
        None

    Attributes:
        ui (QMainWindow): The loaded UI for the main application window.
        sidebar_controller (SidebarController): Controller for managing sidebar interactions.
        create_data_controller (CreateDataController): Controller for managing 'Create Data' page interactions.
    """

    def __init__(self):
        super().__init__()
        # Load UI
        self.ui = loadUi("./app/ui_main.ui", self)

        # Load Controller
        self.sidebar_controller = SidebarController(self)
        self.create_data_controller = CreateDataController(self)
        self.segment_data_controller = SegmentDataController(self)

        # Load styles
        self.load_styles()

    def load_styles(self):
        """
        Load and apply styles from a JSON file.

        This method reads the `styles.json` file located in the `utils` directory and
        applies the styles to the application's widgets.

        Raises:
            FileNotFoundError: If the `styles.json` file does not exist.
            Exception: For any other error encountered while reading the file or applying styles.
        """
        try:
            with open("./app/utils/styles.json", "r") as file:
                styles = json.load(file)

            stylesheet = ""

            for widget, properties in styles.items():
                style_string = "; ".join(f"{key}: {value}" for key, value in properties.items())
                stylesheet += f"{widget} {{ {style_string} }}\n"

            self.setStyleSheet(stylesheet)

        except Exception as e:
            print(f"Error loading styles: {e}")


if __name__ == "__main__":
    """
    Entry point for the application.
    Initializes the QApplication, creates the main window, and starts the event loop.
    """
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
