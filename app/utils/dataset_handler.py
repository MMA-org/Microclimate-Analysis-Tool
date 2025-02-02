"""
Utility for managing datasets created with app inside the 'Microclimate Analysis Data' directory.
"""

import os

class DatasetHandler:
    """
    Handles operations related to dataset folders in the 'Microclimate Analysis Data' directory.

    Attributes:
        base_dir (str): The base directory where dataset folders are stored. Defaults to 'Microclimate Analysis Data'.
    """

    def __init__(self, base_dir="Microclimate Analysis Data"):
        self.base_dir = base_dir

    def get_dataset_folders(self):
        "Retrieves all dataset folders in the base directory."

        if not os.path.exists(self.base_dir):
            return []

        return [folder for folder in os.listdir(self.base_dir)
                if os.path.isdir(os.path.join(self.base_dir, folder))]

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

        images_dir = os.path.join(self.base_dir, dataset_name, "images")
        
        if not os.path.exists(images_dir):
            return []

        image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
        return [os.path.join(images_dir, file) for file in os.listdir(images_dir)
                if file.lower().endswith(image_extensions)]