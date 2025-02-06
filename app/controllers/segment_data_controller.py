"""
Controller for managing the 'Segment Data' page in the GUI application.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from app.controllers.page_controller import PageController
from app.utils.alert_handler import AlertHandler, LoadingDialog
from app.utils.dataset_handler import DatasetHandler
from app.utils.image_display import ImageDisplayHandler
from app.model import generate_segmentation_maps
import os

class SegmentationThread(QThread):
    """
    Thread class to handle segmentation processing in the background.

    Args:
        dataset_path (str): Path to the dataset directory.
    """
    finished = pyqtSignal()

    def __init__(self, dataset_path):
        super().__init__()
        self.dataset_path = dataset_path

    def run(self):
        """Run the segmentation model on the specified dataset."""
        generate_segmentation_maps(self.dataset_path)
        self.finished.emit()

class SegmentDataController(PageController):
    """
    Controller for managing the 'Segment Data' page functionalities.

    Handles image uploads, dataset selection, segmentation execution, and displaying results.

    Args:
        main_window (QMainWindow): The main application window containing the UI components.

    Attributes:
        ui (QMainWindow): Reference to the main window's UI.
    """

    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window
        self.dataset_handler = DatasetHandler()
        self.image_display_handler = ImageDisplayHandler()
        self.image_paths = []

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
        """Enable or disable input fields based on the selected radio button."""

        widget_groups = {
            "group1": [self.ui.segmentBrowseButton, self.ui.segmentBrowseInput, self.ui.segmentUploadButton],
            "group2": [self.ui.segmentChooseCombo, self.ui.segmentAddButton],
        }
        self.handle_toggle_inputs(self.ui.segmentBrowseRadio, self.ui.segmentChooseRadio, widget_groups)

    def add_images_from_dataset(self):
        """
        Add images from the selected dataset to the scroll area.
        Validates dataset selection and displays corresponding images.
        """

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
        "Display images in the provided scroll area."

        self.image_display_handler.clear_layout(scroll_area.layout())

        self.image_paths = image_paths
        images_per_row = 1

        self.image_display_handler.populate_scroll_area(scroll_area, self.image_paths, show_year_input, images_per_row)

    def start_segmentation(self):
        """
        Start the segmentation process.
        Validates inputs, triggers background processing, and handles UI updates during segmentation.
        """

        if not self.image_paths:
            return AlertHandler.show_error("No images have been uploaded. Please upload images before starting segmentation.")

        if self.ui.segmentChooseRadio.isChecked():
            dataset_name = self.ui.segmentChooseCombo.currentText()
            dataset_path = self.dataset_handler.get_dataset_path(dataset_name)
        else:
            dataset_path = os.path.dirname(self.image_paths[0])

        if not os.path.exists(dataset_path):
            return AlertHandler.show_error(f"Dataset directory '{dataset_path}' does not exist.")

        self.loading_dialog = LoadingDialog("Running Segmentation... This may take a while.")
        self.loading_dialog.show()

        self.segmentation_thread = SegmentationThread(dataset_path)
        self.segmentation_thread.finished.connect(lambda: self.on_segmentation_complete(dataset_path))
        self.segmentation_thread.start()

    def on_segmentation_complete(self, dataset_path):
        " Handle post-segmentation processing."

        self.loading_dialog.close()
        self.ui.startSegmentButton.setEnabled(True)

        segmentation_dir = os.path.join(dataset_path, "segmentations")
        if not os.path.exists(segmentation_dir):
            return AlertHandler.show_error("Segmentation folder not found.")

        segmentation_maps = {
            os.path.splitext(f)[0].replace("_seg", ""): os.path.join(segmentation_dir, f)
            for f in os.listdir(segmentation_dir) if f.endswith("_seg.png")
        }

        if not segmentation_maps:
            return AlertHandler.show_error("No segmentation maps generated.")

        layout = self.ui.segmentScrollAreaContents.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.segmentScrollAreaContents)
            self.ui.segmentScrollAreaContents.setLayout(layout)
        else:
            self.image_display_handler.clear_layout(layout)

        for image_path in self.image_paths:
            container_widget = QWidget()
            hbox_layout = QHBoxLayout(container_widget)

            original_widget = self.image_display_handler.create_image_widget(image_path)
            hbox_layout.addWidget(original_widget)

            image_name = os.path.splitext(os.path.basename(image_path))[0]
            if image_name in segmentation_maps:
                seg_map_path = segmentation_maps[image_name]
                segmentation_widget = self.image_display_handler.create_image_widget(seg_map_path)
                hbox_layout.addWidget(segmentation_widget)

            layout.addWidget(container_widget)

        AlertHandler.show_info("Segmentation completed successfully.")
