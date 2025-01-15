from PyQt5.QtWidgets import QGridLayout, QCompleter
from PyQt5.QtCore import Qt
from app.utils.countries_now_handler import get_countries, get_cities_by_country
from app.utils.file_handler import FileHandler
from app.utils.image_display import ImageDisplayHandler


class CreateDataController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.file_handler = FileHandler()
        self.image_display_handler = ImageDisplayHandler()
        self.image_paths = []

        # Country and city data
        self.countries = get_countries()
        self.cities = []

        # Configure ComboBoxes and connect signals
        self.setup_country_combobox()
        self.main_window.appCountryCombo.currentIndexChanged.connect(self.update_cities)
        self._connect_signals()
        self.toggle_inputs()

    def setup_country_combobox(self):
        """Set up the country ComboBox with autocomplete and placeholder."""
        self.main_window.appCountryCombo.setEditable(True)
        self.main_window.appCountryCombo.addItems(["Select a country"])
        self.main_window.appCountryCombo.addItems(sorted(self.countries))
        country_completer = QCompleter(self.countries, self.main_window.appCountryCombo)
        country_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.main_window.appCountryCombo.setCompleter(country_completer)

    def update_cities(self, index):
        """Fetch and update cities for the selected country."""
        country_name = self.main_window.appCountryCombo.currentText().strip()
        if not country_name or country_name == "Select a country":
            self.main_window.appCityCombo.clear()
            return
        self.cities = get_cities_by_country(country_name)
        if self.cities:
            self.setup_city_combobox()
        else:
            self.main_window.appCityCombo.addItem("No cities found")

    def setup_city_combobox(self):
        """Set up the city ComboBox with autocomplete."""
        self.main_window.appCityCombo.clear()
        self.main_window.appCityCombo.addItems(sorted(self.cities))
        city_completer = QCompleter(self.cities, self.main_window.appCityCombo)
        city_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.main_window.appCityCombo.setCompleter(city_completer)

    def toggle_inputs(self):
        """Enable or disable inputs based on the selected radio button."""
        app_mode = self.main_window.appSelectRadio.isChecked()
        self.main_window.appCountryCombo.setEnabled(app_mode)
        self.main_window.appCityCombo.setEnabled(app_mode)
        self.main_window.userLatitudeInput.setEnabled(not app_mode)
        self.main_window.userLongitudeInput.setEnabled(not app_mode)

    def _connect_signals(self):
        """Connect buttons and inputs to their respective handlers."""
        self.main_window.createBrowseButton.clicked.connect(self.handle_browse_files)
        self.main_window.createUploadButton.clicked.connect(self.handle_upload_files)
        self.main_window.appSelectRadio.toggled.connect(self.toggle_inputs)
        self.main_window.insertRadio.toggled.connect(self.toggle_inputs)

    def handle_browse_files(self):
        """Handle the Browse button click."""
        file_paths = self.file_handler.browse_files()
        if file_paths:
            self.image_paths = list(set(self.image_paths + file_paths))
            self.main_window.createBrowseInput.setText(", ".join(self.image_paths))

    def handle_upload_files(self):
        """Handle the Upload button click."""
        input_text = self.main_window.createBrowseInput.text().strip()
        new_paths = self.file_handler.validate_file_paths(input_text)
        self.image_paths = list(set(self.image_paths + new_paths))
        self.main_window.createBrowseInput.clear()
        self._populate_scroll_area()

    def _populate_scroll_area(self):
        """Add image widgets to the scroll area (2 per row)."""
        container = self.main_window.createScrollAreaContents

        # Reuse the existing layout if it exists, otherwise create a new one
        layout = container.layout()
        if layout is None:
            layout = QGridLayout()
            container.setLayout(layout)

        # Clear existing widgets in the layout
        self.image_display_handler.clear_layout(layout)

        for index, image_path in enumerate(self.image_paths):
            widget = self.image_display_handler.create_image_widget(
                image_path, show_year_input=True,
                remove_callback=lambda widget, path=image_path: self.image_display_handler.remove_image(
                    widget, path, self.image_paths, layout
                )
            )
            row, col = divmod(index, 2)
            layout.addWidget(widget, row, col)
