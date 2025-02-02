import os
import pytest
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel
from PyQt5.uic import loadUi
from unittest.mock import MagicMock
from app.controllers.segment_data_controller import SegmentDataController
from app.utils.alert_handler import AlertHandler


@pytest.fixture
def main_window(qtbot):
    "Fixture to load the real .ui file into a QMainWindow."

    window = QMainWindow()

    ui_path = os.path.abspath("./app/ui_main.ui")
    loadUi(ui_path, window)

    qtbot.addWidget(window)
    return window


@pytest.fixture
def segment_data_controller(main_window):
    "Fixture to initialize the SegmentDataController."

    return SegmentDataController(main_window)


def test_setup_ui(segment_data_controller):
    "Test that signals are correctly connected."

    controller = segment_data_controller

    assert controller.ui.segmentBrowseButton.clicked is not None
    assert controller.ui.segmentUploadButton.clicked is not None
    assert controller.ui.startSegmentButton.clicked is not None
    assert controller.ui.segmentBrowseRadio.toggled is not None
    assert controller.ui.segmentChooseRadio.toggled is not None


def test_toggle_inputs(segment_data_controller):
    "Test toggling input widgets."

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
    "Test browsing files."

    controller = segment_data_controller

    controller.file_handler.browse_files = MagicMock(return_value=["test_image.jpg"])
    controller.handle_browse_files(controller.ui.segmentBrowseInput)

    assert "test_image.jpg" in controller.image_paths
    assert controller.ui.segmentBrowseInput.text() == "test_image.jpg"


def test_handle_upload_files(segment_data_controller):
    "Test uploading files."

    controller = segment_data_controller

    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image.jpg"])
    controller.ui.segmentBrowseInput.setText("test_image.jpg")
    controller.handle_upload_files(controller.ui.segmentBrowseInput, controller.ui.segmentScrollAreaContents, show_year_input=False)

    assert "test_image.jpg" in controller.image_paths


def test_start_segmentation_no_images(segment_data_controller):
    "Test starting segmentation with no images uploaded."

    controller = segment_data_controller

    AlertHandler.show_error = MagicMock()
    AlertHandler.show_info = MagicMock()

    controller.start_segmentation()

    AlertHandler.show_error.assert_called_once_with("No images have been uploaded. Please upload images before starting segmentation.")
    AlertHandler.show_info.assert_not_called()


def test_start_segmentation_with_images(segment_data_controller):
    "Test starting segmentation with images uploaded."

    controller = segment_data_controller

    AlertHandler.show_error = MagicMock()
    AlertHandler.show_info = MagicMock()

    controller.image_paths = ["test_image.jpg"]
    controller.start_segmentation()

    AlertHandler.show_info.assert_called_once_with("Segmentation started. Processing images...")
    AlertHandler.show_error.assert_not_called()

def test_add_images_from_dataset(segment_data_controller):
    "Test adding images from an existing dataset to the scroll area."

    controller = segment_data_controller

    controller.dataset_handler.get_images_from_dataset = MagicMock(return_value=["test_image_1.jpg", "test_image_2.jpg"])
    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image_1.jpg", "test_image_2.jpg"])

    controller.ui.segmentChooseCombo.addItem("TestDataset")
    controller.ui.segmentChooseCombo.setCurrentText("TestDataset")

    controller.add_images_from_dataset()

    assert "test_image_1.jpg" in controller.image_paths
    assert "test_image_2.jpg" in controller.image_paths

def test_remove_images(segment_data_controller):
    "Test removing images from the scroll area."

    controller = segment_data_controller

    controller.image_paths = ["test_image_1.jpg", "test_image_2.jpg"]
    scroll_area = controller.ui.segmentScrollAreaContents

    if scroll_area.layout() is None:
        layout = QGridLayout(scroll_area)
        scroll_area.setLayout(layout)
    else:
        layout = scroll_area.layout()

    widget_1 = QWidget()
    widget_2 = QWidget()

    layout.addWidget(widget_1, 0, 0)
    layout.addWidget(widget_2, 1, 0)

    controller.image_display_handler.remove_image(widget_1, "test_image_1.jpg", controller.image_paths, layout, 1, False)

    assert "test_image_1.jpg" not in controller.image_paths
    assert "test_image_2.jpg" in controller.image_paths


def test_readd_images_after_removal(segment_data_controller):
    "Test re-adding images after all images have been removed."

    controller = segment_data_controller

    controller.dataset_handler.get_images_from_dataset = MagicMock(return_value=["test_image_1.jpg"])
    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image_1.jpg"])

    controller.ui.segmentChooseCombo.addItem("TestDataset")
    controller.ui.segmentChooseCombo.setCurrentText("TestDataset")

    controller.add_images_from_dataset()
    assert "test_image_1.jpg" in controller.image_paths

    scroll_area = controller.ui.segmentScrollAreaContents

    if scroll_area.layout() is None:
        layout = QVBoxLayout(scroll_area)
        scroll_area.setLayout(layout)
    else:
        layout = scroll_area.layout()

    widget = QWidget()
    layout.addWidget(widget)

    controller.image_display_handler.remove_image(widget, "test_image_1.jpg", controller.image_paths, layout, 1, False)
    assert "test_image_1.jpg" not in controller.image_paths

    controller.dataset_handler.get_images_from_dataset = MagicMock(return_value=["test_image_2.jpg"])
    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image_2.jpg"])

    controller.add_images_from_dataset()
    assert "test_image_2.jpg" in controller.image_paths

def test_add_remove_readd_images(segment_data_controller):
    "Test adding images, removing all images, and re-adding new images"

    controller = segment_data_controller
    scroll_area = controller.ui.segmentScrollAreaContents

    controller.dataset_handler.get_images_from_dataset = MagicMock(return_value=["image_1.jpg"])
    controller.file_handler.validate_file_paths = MagicMock(return_value=["image_1.jpg"])

    controller.ui.segmentChooseCombo.addItem("TestDataset")
    controller.ui.segmentChooseCombo.setCurrentText("TestDataset")

    controller.add_images_from_dataset()
    assert "image_1.jpg" in controller.image_paths

    layout = scroll_area.layout() or QVBoxLayout(scroll_area)
    scroll_area.setLayout(layout)

    widget = QLabel("Image 1")
    layout.addWidget(widget)
    controller.image_display_handler.remove_image(widget, "image_1.jpg", controller.image_paths, layout, 1, False)

    assert "image_1.jpg" not in controller.image_paths
    assert layout.count() == 0 

    controller.dataset_handler.get_images_from_dataset = MagicMock(return_value=["image_2.jpg"])
    controller.file_handler.validate_file_paths = MagicMock(return_value=["image_2.jpg"])

    controller.add_images_from_dataset()
    assert "image_2.jpg" in controller.image_paths
    assert scroll_area.layout().count() == 1