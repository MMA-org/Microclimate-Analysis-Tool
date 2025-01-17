import pytest
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from unittest.mock import MagicMock, patch
from app.controllers.segment_data_controller import SegmentDataController
from app.utils.alert_handler import AlertHandler
import os


@pytest.fixture
def main_window(qtbot):
    """Fixture to load the real .ui file into a QMainWindow."""
    window = QMainWindow()

    ui_path = os.path.abspath("./app/ui_main.ui")
    loadUi(ui_path, window)

    qtbot.addWidget(window)
    return window


@pytest.fixture
def segment_data_controller(main_window):
    """Fixture to initialize the SegmentDataController."""
    return SegmentDataController(main_window)


def test_setup_ui(segment_data_controller):
    """Test that signals are correctly connected."""
    controller = segment_data_controller
    assert controller.ui.segmentBrowseButton.clicked is not None
    assert controller.ui.segmentUploadButton.clicked is not None
    assert controller.ui.startSegmentButton.clicked is not None
    assert controller.ui.segmentBrowseRadio.toggled is not None
    assert controller.ui.segmentChooseRadio.toggled is not None


def test_toggle_inputs(segment_data_controller):
    """Test toggling input widgets."""
    controller = segment_data_controller

    controller.ui.segmentBrowseRadio.setChecked(True)
    controller.toggle_inputs()
    assert all(widget.isEnabled() for widget in [
        controller.ui.segmentBrowseButton,
        controller.ui.segmentBrowseInput,
        controller.ui.segmentUploadButton
    ])
    assert not controller.ui.segmentChooseCombo.isEnabled()

    controller.ui.segmentChooseRadio.setChecked(True)
    controller.toggle_inputs()
    assert controller.ui.segmentChooseCombo.isEnabled()
    assert all(not widget.isEnabled() for widget in [
        controller.ui.segmentBrowseButton,
        controller.ui.segmentBrowseInput,
        controller.ui.segmentUploadButton
    ])


def test_handle_browse_files(segment_data_controller):
    """Test browsing files."""
    controller = segment_data_controller
    controller.file_handler.browse_files = MagicMock(return_value=["test_image.jpg"])
    controller.handle_browse_files(controller.ui.segmentBrowseInput)
    assert "test_image.jpg" in controller.image_paths
    assert controller.ui.segmentBrowseInput.text() == "test_image.jpg"


def test_handle_upload_files(segment_data_controller):
    """Test uploading files."""
    controller = segment_data_controller
    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image.jpg"])
    controller.ui.segmentBrowseInput.setText("test_image.jpg")
    controller.handle_upload_files(controller.ui.segmentBrowseInput, controller.ui.segmentScrollAreaContents, show_year_input=False)
    assert "test_image.jpg" in controller.image_paths


def test_start_segmentation_no_images(segment_data_controller):
    """Test starting segmentation with no images uploaded."""
    controller = segment_data_controller

    AlertHandler.show_error = MagicMock()
    AlertHandler.show_info = MagicMock()

    controller.start_segmentation()

    AlertHandler.show_error.assert_called_once_with("No images have been uploaded. Please upload images before starting segmentation.")
    AlertHandler.show_info.assert_not_called()


def test_start_segmentation_with_images(segment_data_controller):
    """Test starting segmentation with images uploaded."""
    controller = segment_data_controller

    AlertHandler.show_error = MagicMock()
    AlertHandler.show_info = MagicMock()

    controller.image_paths = ["test_image.jpg"]

    controller.start_segmentation()

    AlertHandler.show_info.assert_called_once_with("Segmentation started. Processing images...")
    AlertHandler.show_error.assert_not_called()
