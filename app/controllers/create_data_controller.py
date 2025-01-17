"""
Controller for managing the 'Create Data' page in the GUI application.
"""

import os
from app.utils.countries_cities_handler import setup_country_combobox, setup_city_combobox
from app.utils.save_handler import SaveHandler
from app.utils.alert_handler import AlertHandler
from app.controllers.page_controller import PageController
from PyQt5.QtWidgets import QLineEdit

class CreateDataController(PageController):
    """
    Controller for managing the 'Create Data' page.

    This class handles functionalities such as file browsing and uploading,
    validating inputs, saving session data, and dynamically updating the UI.

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
        """
        Initialize UI components and connect signals.
        Connects comboboxes, radio buttons, and action buttons to their respective methods.
        """
        setup_country_combobox(self.ui.appCountryCombo)
        self.ui.appCountryCombo.currentIndexChanged.connect(self.update_cities)
        self.ui.appSelectRadio.toggled.connect(lambda: self.toggle_inputs())
        self.ui.insertRadio.toggled.connect(lambda: self.toggle_inputs())
        self.ui.createBrowseButton.clicked.connect(
            lambda: self.handle_browse_files(self.ui.createBrowseInput)
        )
        self.ui.createUploadButton.clicked.connect(
            lambda: self.handle_upload_files(self.ui.createBrowseInput, self.ui.createScrollAreaContents, show_year_input=True)
        )
        self.ui.saveButton.clicked.connect(self.handle_save)

    def toggle_inputs(self):
        """
        Enable or disable input fields based on the selected radio button.
        """
        widget_groups = {
            "group1": [self.ui.appCountryCombo, self.ui.appCityCombo],
            "group2": [self.ui.userLatitudeInput, self.ui.userLongitudeInput],
        }
        self.handle_toggle_inputs(self.ui.appSelectRadio, self.ui.insertRadio, widget_groups)

    def update_cities(self):
        """
        Update the city combobox based on the selected country.
        Calls the utility function to populate the city combobox dynamically.
        """
        setup_city_combobox(
            country_combo=self.ui.appCountryCombo,
            city_combo=self.ui.appCityCombo,
        )

    def handle_save(self):
        """
        Save session data, including images and metadata.
        Performs necessary validations and saves image files, metadata, and coordinates to the appropriate directory.
        """
        if not self._validate_save():
            return

        session_name = self.ui.saveNameInput.text().strip()
        SaveHandler.save_images(self.image_paths, session_name)

        metadata = {
            "coordinates": self._get_coordinates(),
            "images": self.image_display_handler.get_images_with_years(self.ui.createScrollAreaContents),
        }
        SaveHandler.save_metadata(metadata, session_name)
        AlertHandler.show_info("Data saved successfully!")
        self.clear_page()

    def clear_page(self):
        """
        Clear all inputs and reset the page to its initial state.
        """
        self.ui.saveNameInput.clear()
        self.ui.createBrowseInput.clear()

        self.ui.userLatitudeInput.clear()
        self.ui.userLongitudeInput.clear()

        self.image_display_handler.clear_layout(self.ui.createScrollAreaContents.layout())
        self.image_paths = []

    def _validate_save(self):
        """
        Perform all necessary validations before saving session data.

        Validates session name, image uploads, location inputs, and image years.

        Returns:
            bool: True if all validations pass, False otherwise.
        """
        session_name = self.ui.saveNameInput.text().strip()
        if not session_name:
            return AlertHandler.show_error("Please enter a name for this data.")

        if os.path.exists(os.path.join(SaveHandler.BASE_DIR, session_name)):
            return AlertHandler.show_error(f"A folder with the name '{session_name}' already exists. Please choose a different name.")

        if not self.image_paths:
            return AlertHandler.show_error("No images have been uploaded. Please upload images before saving.")

        if self.ui.appSelectRadio.isChecked():
            if not self._validate_combobox(self.ui.appCountryCombo, "Select a country", "country"):
                return False
            if not self._validate_combobox(self.ui.appCityCombo, "Select a city", "city"):
                return False
        elif not self._validate_coordinates():
            return False

        if not self._validate_image_years():
            return False

        return True

    def _validate_combobox(self, combo, placeholder, field_name):
        """
        Check if a combobox has a valid selection.

        Args:
            combo (QComboBox): The combobox to validate.
            placeholder (str): Placeholder text to check against.
            field_name (str): Name of the field for error messages.

        Returns:
            bool: True if the combobox has a valid selection, False otherwise.
        """
        value = combo.currentText().strip()
        if not value or value == placeholder:
            AlertHandler.show_error(f"Please select a valid {field_name}.")
            return False
        return True

    def _validate_coordinates(self):
        """
        Validate latitude and longitude inputs.

        Ensures that latitude and longitude values are provided and are valid numbers.

        Returns:
            bool: True if inputs are valid, False otherwise.
        """
        lat = self.ui.userLatitudeInput.text().strip()
        lon = self.ui.userLongitudeInput.text().strip()
        if not lat or not lon:
            AlertHandler.show_error("Latitude and longitude must be provided.")
            return False
        if not lat.replace(".", "", 1).isdigit() or not lon.replace(".", "", 1).isdigit():
            AlertHandler.show_error("Latitude and longitude must be valid numbers.")
            return False
        return True
    
    def _validate_image_years(self):
        """Ensure all images in the scroll area have valid years."""
        layout = self.ui.createScrollAreaContents.layout()
        if not layout:
            return True

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                year_input = widget.findChild(QLineEdit, "yearInput")
                if not year_input or not year_input.text().strip().isdigit():
                    AlertHandler.show_error("Each image must have a valid year specified. Please fill in all year inputs.")
                    return False
        return True

    def _get_coordinates(self):
        """
        Retrieve coordinates from inputs or API.

        If 'Select Mode' is enabled, retrieves coordinates from an API (placeholder for now).
        Otherwise, retrieves latitude and longitude from user inputs.

        Returns:
            dict: A dictionary containing latitude and longitude values.
        """
        if self.ui.appSelectRadio.isChecked():
            return {"latitude": None, "longitude": None}  # Replace with API call
        return {
            "latitude": self.ui.userLatitudeInput.text().strip(),
            "longitude": self.ui.userLongitudeInput.text().strip(),
        }
    
