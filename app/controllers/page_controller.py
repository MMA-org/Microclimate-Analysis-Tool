"""
Base controller for shared functionalities across GUI pages.
"""

from app.utils.file_handler import FileHandler
from app.utils.image_display import ImageDisplayHandler
from app.utils.alert_handler import AlertHandler


class PageController:
    """
    Base controller providing common functionalities for file browsing, uploading,
    and managing UI components in different pages.

    Attributes:
        file_handler (FileHandler): Handles file browsing and validation.
        image_display_handler (ImageDisplayHandler): Manages image display in the scroll area.
        image_paths (list): Stores the paths of uploaded images.
    """

    def __init__(self):
        self.file_handler = FileHandler()
        self.image_display_handler = ImageDisplayHandler()
        self.image_paths = []

    def handle_browse_files(self, input_field):
        """
        Browse and select image files.

        Args:
            input_field (QLineEdit): Input field to display the first selected file path.
        """
        file_paths = self.file_handler.browse_files()
        if file_paths:
            self.image_paths = list(set(self.image_paths + file_paths))
            input_field.setText(file_paths[0])

    def handle_upload_files(self, input_field, scroll_area, show_year_input=False):
        """
        Validate and upload image files, and display them in a scroll area.

        Args:
            input_field (QLineEdit): Input field containing file paths.
            scroll_area (QWidget): Scroll area container for displaying images.
            show_year_input (bool): Whether to include year input fields for images.
        """
        input_text = input_field.text().strip()
        if not input_text:
            return AlertHandler.show_error("No file path provided. Please browse and select files to upload.")

        new_paths = self.file_handler.validate_file_paths(input_text)
        if not new_paths:
            return AlertHandler.show_error("No valid files found in the provided path. Ensure the file paths are correct.")

        self.image_paths = list(set(self.image_paths + new_paths))
        input_field.clear()
        images_per_row = 2 if show_year_input else 1
        self.image_display_handler.populate_scroll_area(scroll_area, self.image_paths, show_year_input, images_per_row)

    def handle_toggle_inputs(self, radio_button1, radio_button2, widget_groups):
        """
        Handle toggling the enabled state of widgets and radio buttons based on selection.

        Args:
            radio_button1 (QRadioButton): The first radio button (activates one group).
            radio_button2 (QRadioButton): The second radio button (activates the other group).
            widget_groups (dict): A dictionary with keys "group1" and "group2", containing
                                lists of widgets to enable or disable based on the selected radio button.
        """
        if radio_button1.isChecked():
            for widget in widget_groups["group1"]:
                widget.setEnabled(True)
            for widget in widget_groups["group2"]:
                widget.setEnabled(False)
            radio_button2.setEnabled(True)
        elif radio_button2.isChecked():
            for widget in widget_groups["group1"]:
                widget.setEnabled(False)
            for widget in widget_groups["group2"]:
                widget.setEnabled(True)
            radio_button1.setEnabled(True)
