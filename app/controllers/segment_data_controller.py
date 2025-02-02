"""
Controller for managing the 'Segment Data' page in the GUI application.
"""

from app.controllers.page_controller import PageController
from app.utils.alert_handler import AlertHandler
from app.utils.dataset_handler import DatasetHandler


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
        self.dataset_handler = DatasetHandler()

        self._setup_ui()
        self.toggle_inputs()

    def _setup_ui(self):
        "Initialize UI components and connect signals."
        self.ui.segmentBrowseButton.clicked.connect(
            lambda: self.handle_browse_files(self.ui.segmentBrowseInput)
        )
        self.ui.segmentUploadButton.clicked.connect(
            lambda: self.handle_upload_files(
                self.ui.segmentBrowseInput, 
                self.ui.segmentScrollAreaContents, 
                show_year_input=False
            )
        )
        self.ui.startSegmentButton.clicked.connect(self.start_segmentation)
        self.ui.segmentBrowseRadio.toggled.connect(lambda: self.toggle_inputs())
        self.ui.segmentChooseRadio.toggled.connect(lambda: self.toggle_inputs())
        self.ui.segmentChooseRadio.toggled.connect(
            lambda checked: self.dataset_handler.populate_dataset_combo(self.ui.segmentChooseCombo) if checked else None
        )
        self.ui.segmentAddButton.clicked.connect(self.add_images_from_dataset)

    def toggle_inputs(self):
        "Enable or disable input fields based on the selected radio button."

        widget_groups = {
            "group1": [self.ui.segmentBrowseButton, self.ui.segmentBrowseInput, self.ui.segmentUploadButton],
            "group2": [self.ui.segmentChooseCombo],
        }
        self.handle_toggle_inputs(self.ui.segmentBrowseRadio, self.ui.segmentChooseRadio, widget_groups)

    def add_images_from_dataset(self):
        "Adds images from the selected dataset to the scroll area."

        dataset_name = self.ui.segmentChooseCombo.currentText()
        if dataset_name == "No datasets found" or not dataset_name:
            AlertHandler.show_error("Please select a valid dataset.")
            return

        image_paths = self.dataset_handler.get_images_from_dataset(dataset_name)
        
        if not image_paths:
            AlertHandler.show_error(f"No images found in the dataset '{dataset_name}'.")
            return

        self.handle_display_images(image_paths, self.ui.segmentScrollAreaContents, show_year_input=False)

    def handle_display_images(self, image_paths, scroll_area, show_year_input=False):
        "Directly displays a list of image paths in the scroll area."

        self.image_display_handler.clear_layout(scroll_area.layout())

        image_paths_str = "\n".join(image_paths)

        new_paths = self.file_handler.validate_file_paths(image_paths_str)

        if not new_paths:
            return AlertHandler.show_error("No valid image files found in the dataset.")

        self.image_paths = list(set(self.image_paths + new_paths))
        images_per_row = 2 if show_year_input else 1

        self.image_display_handler.populate_scroll_area(scroll_area, self.image_paths, show_year_input, images_per_row)

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
