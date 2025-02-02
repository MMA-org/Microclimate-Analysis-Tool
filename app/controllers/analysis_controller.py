"""
Controller for managing the 'View Analysis' page in the GUI application.
"""

from app.controllers.page_controller import PageController
from app.utils.dataset_handler import DatasetHandler

class AnalysisPageController(PageController):
    """
    This class handles functionalities such as displaying available datasets
    created in the 'Microclimate Analysis Data' directory.

    Args:
        main_window (QMainWindow): The main application window containing the UI components.

    Attributes:
        ui (QMainWindow): Reference to the main window's UI.
    """

    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window
        self.dataset_handler = DatasetHandler()

        self._setup_ui()

    def _setup_ui(self):
        "Initialize UI components and populate the dataset combo box."

        self.dataset_handler.populate_dataset_combo(self.ui.analysisChooseCombo)

