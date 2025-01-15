import os
from PyQt5.QtWidgets import QFileDialog


class FileHandler:
    def browse_files(self, dialog_title="Select Images", file_types="Images (*.png *.jpg *.jpeg *.tif);;All Files (*)"):
        """Open a file dialog to select files."""
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(None, dialog_title, "", file_types, options=options)
        return file_paths

    def validate_file_paths(self, input_text):
        """Validate and clean file paths from text input."""
        paths = [path.strip() for path in input_text.splitlines() if path.strip()]
        return [path for path in paths if os.path.isfile(path)]
