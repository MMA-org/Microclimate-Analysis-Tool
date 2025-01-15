import os
import shutil
import json


class SaveHandler:
    BASE_DIR = "Microclimate analysis data"

    @staticmethod
    def ensure_base_directory_exists():
        """Ensure the centralized directory exists."""
        if not os.path.exists(SaveHandler.BASE_DIR):
            os.makedirs(SaveHandler.BASE_DIR)

    @staticmethod
    def create_session_directory(session_name):
        """Create a session directory with the given name."""
        SaveHandler.ensure_base_directory_exists()
        session_path = os.path.join(SaveHandler.BASE_DIR, session_name)
        if not os.path.exists(session_path):
            os.makedirs(session_path)
            os.makedirs(os.path.join(session_path, "images"))
            os.makedirs(os.path.join(session_path, "segmentation"))
            os.makedirs(os.path.join(session_path, "analysis/plots"))
        return session_path

    @staticmethod
    def save_images(image_paths, session_name):
        """Save uploaded images into the session directory."""
        session_path = SaveHandler.create_session_directory(session_name)
        images_path = os.path.join(session_path, "images")

        for image_path in image_paths:
            if os.path.isfile(image_path):
                dest_path = os.path.join(images_path, os.path.basename(image_path))
                shutil.copy(image_path, dest_path)

    @staticmethod
    def save_metadata(metadata, session_name):
        """Save metadata as JSON in the session directory."""
        session_path = SaveHandler.create_session_directory(session_name)
        metadata_path = os.path.join(session_path, "metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)