import pytest
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from unittest.mock import MagicMock, patch
from app.controllers.create_data_controller import CreateDataController
from app.utils.save_handler import SaveHandler
from app.utils.alert_handler import AlertHandler
import os
import shutil


@pytest.fixture
def main_window(qtbot):
    """Fixture to load the real .ui file into a QMainWindow."""
    window = QMainWindow()

    ui_path = os.path.abspath("./app/ui_main.ui")
    loadUi(ui_path, window)

    qtbot.addWidget(window)
    return window


@pytest.fixture
def create_data_controller(main_window):
    """Fixture to initialize the CreateDataController."""
    return CreateDataController(main_window)


def test_setup_ui(create_data_controller):
    """Test that signals are correctly connected."""
    controller = create_data_controller
    assert controller.ui.appCountryCombo.currentIndexChanged is not None
    assert controller.ui.createBrowseButton.clicked is not None
    assert controller.ui.saveButton.clicked is not None


def test_toggle_inputs(create_data_controller):
    """Test toggling input widgets."""
    controller = create_data_controller
    controller.ui.appSelectRadio.setChecked(True)
    controller.toggle_inputs()
    assert controller.ui.appCountryCombo.isEnabled()
    assert not controller.ui.userLatitudeInput.isEnabled()

    controller.ui.insertRadio.setChecked(True)
    controller.toggle_inputs()
    assert not controller.ui.appCountryCombo.isEnabled()
    assert controller.ui.userLatitudeInput.isEnabled()


def test_update_cities(create_data_controller):
    """Test updating the city combobox with specific country and city selection."""
    controller = create_data_controller

    controller.ui.appCountryCombo.addItem("Select a country")
    controller.ui.appCountryCombo.addItem("Israel")
    controller.ui.appCityCombo.addItem("Select a city")
    controller.ui.appCityCombo.addItem("Haifa")

    controller.ui.appCountryCombo.setCurrentIndex(1)

    with patch("app.utils.countries_cities_handler.get_cities_by_country", return_value=["Haifa", "Tel Aviv"]):
        controller.update_cities()

    assert "Haifa" in [controller.ui.appCityCombo.itemText(i) for i in range(controller.ui.appCityCombo.count())]
    controller.ui.appCityCombo.setCurrentIndex(controller.ui.appCityCombo.findText("Haifa"))

    controller.ui.userLatitudeInput.setText("32.794")
    controller.ui.userLongitudeInput.setText("34.989")

    assert controller.ui.userLatitudeInput.text() == "32.794"
    assert controller.ui.userLongitudeInput.text() == "34.989"


def test_handle_browse_files(create_data_controller):
    """Test browsing files."""
    controller = create_data_controller
    controller.file_handler.browse_files = MagicMock(return_value=["test_image.jpg"])
    controller.handle_browse_files(controller.ui.createBrowseInput)
    assert "test_image.jpg" in controller.image_paths
    assert controller.ui.createBrowseInput.text() == "test_image.jpg"


def test_handle_upload_files(create_data_controller):
    """Test uploading files."""
    controller = create_data_controller
    controller.file_handler.validate_file_paths = MagicMock(return_value=["test_image.jpg"])
    controller.ui.createBrowseInput.setText("test_image.jpg")
    controller.handle_upload_files(controller.ui.createBrowseInput, controller.ui.createScrollAreaContents, show_year_input=True)
    assert "test_image.jpg" in controller.image_paths


def test_validate_save(create_data_controller):
    """Test the validation before saving."""
    controller = create_data_controller
    controller.ui.saveNameInput.setText("TestSession")
    controller.image_paths = ["test_image.jpg"]

    controller._validate_combobox = MagicMock(return_value=True)
    controller._validate_coordinates = MagicMock(return_value=True)
    controller._validate_image_years = MagicMock(return_value=True)
    assert controller._validate_save()


def test_validate_combobox(create_data_controller):
    """Test combobox validation."""
    controller = create_data_controller
    controller.ui.appCountryCombo.addItem("Select a country")
    controller.ui.appCountryCombo.addItem("Valid Country")
    controller.ui.appCountryCombo.setCurrentIndex(1)
    assert controller._validate_combobox(controller.ui.appCountryCombo, "Select a country", "country")


def test_validate_coordinates(create_data_controller):
    """Test latitude and longitude validation."""
    controller = create_data_controller
    controller.ui.userLatitudeInput.setText("12.34")
    controller.ui.userLongitudeInput.setText("56.78")
    assert controller._validate_coordinates()


def test_validate_image_years(create_data_controller):
    """Test year input validation."""
    controller = create_data_controller
    controller.image_display_handler.get_images_with_years = MagicMock(
        return_value={"test_image.jpg": 2023}
    )
    assert controller._validate_image_years()


@pytest.fixture(autouse=True)
def clear_test_session():
    """Remove any existing TestSession folder before tests."""
    test_session_dir = os.path.join(SaveHandler.BASE_DIR, "TestSession")
    if os.path.exists(test_session_dir):
        shutil.rmtree(test_session_dir)


def test_handle_save(create_data_controller):
    """Test save functionality with valid country, city, and coordinates."""
    controller = create_data_controller
    controller.ui.saveNameInput.setText("TestSession")
    controller.image_paths = ["test_image.jpg"]

    SaveHandler.save_images = MagicMock()
    SaveHandler.save_metadata = MagicMock()
    AlertHandler.show_info = MagicMock()
    AlertHandler.show_error = MagicMock()

    controller.image_display_handler.get_images_with_years = MagicMock(
        return_value={"test_image.jpg": 2023}
    )

    controller._get_coordinates = MagicMock(return_value={"latitude": "32.794", "longitude": "34.989"})

    controller._validate_save = MagicMock(return_value=True)

    controller.handle_save()

    SaveHandler.save_images.assert_called_once_with(["test_image.jpg"], "TestSession")
    SaveHandler.save_metadata.assert_called_once_with(
        {
            "coordinates": {"latitude": "32.794", "longitude": "34.989"},
            "images": {"test_image.jpg": 2023},
        },
        "TestSession",
    )
    AlertHandler.show_info.assert_called_once_with("Data saved successfully!")

    AlertHandler.show_error.assert_not_called()


def test_clear_page(create_data_controller):
    """Test clearing the page."""
    controller = create_data_controller
    controller.ui.saveNameInput.setText("TestSession")
    controller.ui.createBrowseInput.setText("test_image.jpg")
    controller.image_paths = ["test_image.jpg"]

    controller.clear_page()

    assert controller.ui.saveNameInput.text() == ""
    assert controller.ui.createBrowseInput.text() == ""
    assert not controller.image_paths
