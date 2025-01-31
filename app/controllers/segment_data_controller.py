"""
Controller for managing the 'Segment Data' page in the GUI application.
"""

from app.controllers.page_controller import PageController
from app.utils.alert_handler import AlertHandler


class SegmentDataController(PageController):
    """
    Controller for managing interactions on the 'Segment Data' page.

    This class handles functionalities such as file browsing, uploading,
    and starting the segmentation process.

    Args:
        main_window (QMainWindow): The main application window containing the UI components.

    Attributes:
        ui (QMainWindow): Reference to the main window's UI.
    """

    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window

        self._setup_ui()
        self.toggle_inputs()

    def _setup_ui(self):
        "Initialize UI components and connect signals."

        self.ui.segmentBrowseButton.clicked.connect(
            lambda: self.handle_browse_files(self.ui.segmentBrowseInput)
        )
        self.ui.segmentUploadButton.clicked.connect(
            lambda: self.handle_upload_files(self.ui.segmentBrowseInput, self.ui.segmentScrollAreaContents, show_year_input=False)
        )
        self.ui.startSegmentButton.clicked.connect(self.start_segmentation)
        self.ui.segmentBrowseRadio.toggled.connect(lambda: self.toggle_inputs())
        self.ui.segmentChooseRadio.toggled.connect(lambda: self.toggle_inputs())

    def toggle_inputs(self):
        "Enable or disable input fields based on the selected radio button."

        widget_groups = {
            "group1": [self.ui.segmentBrowseButton, self.ui.segmentBrowseInput, self.ui.segmentUploadButton],
            "group2": [self.ui.segmentChooseCombo],
        }
        self.handle_toggle_inputs(self.ui.segmentBrowseRadio, self.ui.segmentChooseRadio, widget_groups)

    def start_segmentation(self):
        """
        Start the segmentation process.
        Performs validation to ensure images are uploaded before proceeding with segmentation.
        """
        if not self.image_paths:
            return AlertHandler.show_error("No images have been uploaded. Please upload images before starting segmentation.")

        # Placeholder for segmentation logic
        # Integrate your segmentation model or API call here
        AlertHandler.show_info("Segmentation started. Processing images...")
