"""
Utility for managing datasets created with app inside the 'Microclimate Analysis Data' directory.
"""

import os

class DatasetHandler:
    """
    Handles operations related to dataset folders in the 'Microclimate Analysis Data' directory.

    Attributes:
        base_directory (str): The base directory where dataset folders are stored. Defaults to 'Microclimate Analysis Data'.
    """

    def __init__(self, base_directory="Microclimate Analysis Data"):
        self.base_directory = base_directory

    def get_dataset_path(self, dataset_name):
            """
            Returns the full path of the dataset directory.
            """
            dataset_path = os.path.join(self.base_directory, dataset_name)
            if os.path.exists(dataset_path):
                return dataset_path
            else:
                raise FileNotFoundError(f"Dataset '{dataset_name}' not found at '{dataset_path}'.")

    def get_dataset_folders(self):
        "Retrieves all dataset folders in the base directory."

        if not os.path.exists(self.base_directory):
            return []

        return [folder for folder in os.listdir(self.base_directory)
                if os.path.isdir(os.path.join(self.base_directory, folder))]

    def populate_dataset_combo(self, combo_box):
        "Populates a QComboBox with the dataset folder names."

        combo_box.clear()
        datasets = self.get_dataset_folders()
        
        if datasets:
            combo_box.addItems(datasets)
        else:
            combo_box.addItem("No datasets found")

    def get_images_from_dataset(self, dataset_name):
        "Retrieves image file paths from the 'images' folder within the selected dataset."

        images_dir = os.path.join(self.base_directory, dataset_name, "images")
        
        if not os.path.exists(images_dir):
            return []

        image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
        return [os.path.join(images_dir, file) for file in os.listdir(images_dir)
                if file.lower().endswith(image_extensions)]