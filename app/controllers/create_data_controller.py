"""
Controller for managing the 'Create Data' page in the GUI application.
"""

import os
from app.utils.countries_cities_handler import setup_country_combobox, setup_city_combobox
from app.utils.file_handler import FileHandler
from app.utils.image_display import ImageDisplayHandler
from app.utils.save_handler import SaveHandler
from app.utils.alert_handler import AlertHandler


class CreateDataController:
    """
    Controller for managing the 'Create Data' page.

    This class handles functionalities such as file browsing and uploading, 
    validating inputs, saving session data, and dynamically updating the UI.

    Args:
        main_window (QMainWindow): The main application window containing the UI components.

    Attributes:
        ui (QMainWindow): Reference to the main window's UI.
        file_handler (FileHandler): Handles file browsing and validation.
        image_display_handler (ImageDisplayHandler): Manages image display in the scroll area.
        image_paths (list): Stores the paths of uploaded images.
    """

    def __init__(self, main_window):
        self.ui = main_window
        self.file_handler = FileHandler()
        self.image_display_handler = ImageDisplayHandler()
        self.image_paths = []

        self._setup_ui()
        self.toggle_inputs()

    def _setup_ui(self):
        """
        Initialize UI components and connect signals.

        Connects comboboxes, radio buttons, and action buttons to their respective methods.
        """
        setup_country_combobox(self.ui.appCountryCombo)
        self.ui.appCountryCombo.currentIndexChanged.connect(self.update_cities)
        self.ui.appSelectRadio.toggled.connect(self.toggle_inputs)
        self.ui.insertRadio.toggled.connect(self.toggle_inputs)
        self.ui.createBrowseButton.clicked.connect(self.handle_browse_files)
        self.ui.createUploadButton.clicked.connect(self.handle_upload_files)
        self.ui.saveButton.clicked.connect(self.handle_save)

    def toggle_inputs(self):
        """
        Enable or disable input fields based on the selected radio button.

        Enables comboboxes for selecting a country and city in 'Select Mode', 
        or latitude and longitude inputs in 'Insert Mode'.
        """
        is_select_mode = self.ui.appSelectRadio.isChecked()
        self.ui.appCountryCombo.setEnabled(is_select_mode)
        self.ui.appCityCombo.setEnabled(is_select_mode)
        self.ui.userLatitudeInput.setEnabled(not is_select_mode)
        self.ui.userLongitudeInput.setEnabled(not is_select_mode)

    def update_cities(self):
        """
        Update the city combobox based on the selected country.

        Calls the utility function to populate the city combobox dynamically.
        """
        setup_city_combobox(
            country_combo=self.ui.appCountryCombo,
            city_combo=self.ui.appCityCombo,
        )

    def handle_browse_files(self):
        """
        Browse and select image files.

        Opens a file dialog, allowing the user to select image files, 
        and updates the input field with the first selected file's path.
        """
        file_paths = self.file_handler.browse_files()
        if file_paths:
            self.image_paths = list(set(self.image_paths + file_paths))
            self.ui.createBrowseInput.setText(file_paths[0])

    def handle_upload_files(self):
        """
        Validate and upload image files.

        Reads the file paths from the input field, validates them, and populates 
        the scroll area with the uploaded images.
        """
        input_text = self.ui.createBrowseInput.text().strip()
        if not input_text:
            return AlertHandler.show_error("No file path provided. Please browse and select files to upload.")

        new_paths = self.file_handler.validate_file_paths(input_text)
        if not new_paths:
            return AlertHandler.show_error("No valid files found in the provided path. Ensure the file paths are correct.")

        self.image_paths = list(set(self.image_paths + new_paths))
        self.ui.createBrowseInput.clear()
        self._populate_scroll_area()

    def _populate_scroll_area(self):
        """
        Display uploaded images in the scroll area.

        Populates the scroll area with image widgets and includes a year input field 
        for each image.
        """
        self.image_display_handler.populate_scroll_area(
            container=self.ui.createScrollAreaContents,
            image_paths=self.image_paths,
            show_year_input=True,
        )

    def handle_save(self):
        """
        Save session data, including images and metadata.

        Performs necessary validations and saves image files, metadata, and coordinates 
        to the appropriate directory.
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
        """
        Ensure all images have valid year inputs.

        Returns:
            bool: True if all images have valid years, False otherwise.
        """
        return self.image_display_handler.validate_image_years(self.ui.createScrollAreaContents)

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
