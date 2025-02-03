"""
Controller for managing the 'View Analysis' page in the GUI application.
"""
from app.controllers.page_controller import PageController
from app.utils.dataset_handler import DatasetHandler
from app.utils.climate_data_handler import ClimateDataHandler
from app.utils.alert_handler import AlertHandler, LoadingDialog
import os
import json

class AnalysisPageController(PageController):
    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window
        self.dataset_handler = DatasetHandler()
        self.climate_data_handler = ClimateDataHandler()
        self.alert_handler = AlertHandler()

        self._setup_ui()

    def _setup_ui(self):
        self.dataset_handler.populate_dataset_combo(self.ui.analysisChooseCombo)
        self.ui.viewAnalysisButton.clicked.connect(self.process_climate_data)

    def process_climate_data(self):
        dataset_name = self.ui.analysisChooseCombo.currentText()
        if not dataset_name:
            self.alert_handler.show_warning("Please select a dataset.")
            return

        dataset_path = os.path.join("Microclimate Analysis Data", dataset_name)
        metadata_path = os.path.join(dataset_path, "metadata.json")

        if not os.path.exists(metadata_path):
            self.alert_handler.show_error("metadata.json not found.")
            return

        # Show loading dialog
        loading_dialog = LoadingDialog("Fetching climate data...")
        loading_dialog.show()

        try:
            with open(metadata_path, "r") as file:
                metadata = json.load(file)

            latitude = metadata.get("coordinates", {}).get("latitude")
            longitude = metadata.get("coordinates", {}).get("longitude")
            years = {details["year"] for details in metadata.get("images", {}).values()}

            # Fetch and update climate data
            climate_data = self.climate_data_handler.fetch_climate_data(latitude, longitude, years)
            self.climate_data_handler.update_metadata(dataset_path, climate_data)

            self.alert_handler.show_info("Climate data updated successfully.")

        except Exception as e:
            self.alert_handler.show_error(f"An error occurred: {e}")

        finally:
            loading_dialog.close()
