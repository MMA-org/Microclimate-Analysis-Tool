import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from app.controllers.sidebar_controller import SidebarController
from app.controllers.create_data_controller import CreateDataController

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load UI
        self.ui = loadUi("./app/ui_main.ui", self)

        # Sidebar Controller
        self.sidebar_controller = SidebarController(self)
        self.create_data_controller = CreateDataController(self)
        # Load styles
        self.load_styles()

    def load_styles(self):
        """Load and apply styles from JSON."""
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
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
