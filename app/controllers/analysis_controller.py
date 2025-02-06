import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from app.controllers.page_controller import PageController
from app.utils.dataset_handler import DatasetHandler
from app.utils.image_display import ImageDisplayHandler
from app.utils.alert_handler import AlertHandler, LoadingDialog
from app.utils.climate_data_handler import ClimateDataHandler

class AnalysisPageController(PageController):
    """
    Controller for handling analysis page functionality including data visualization,
    climate data processing, and analysis generation.
    """
    # Land cover definitions
    LAND_COVER_NAMES = [
        'Bareland\n', 'Rangeland\n', 'Developed\nSpace', 'Road',
        'Tree', 'Water', 'Agriculture\nLand', 'Building'
    ]
    LAND_COVER_COLS = [f'class_{i+1}' for i in range(8)]
    LAND_COVER_COLORS = [
        '#FF0000', '#FFFF00', '#C0C0C0', '#FFFFFF',
        '#00FF00', '#0000FF', '#800080', '#FFA500'
    ]
    
    # Unified climate parameters with unit, color, and display name (for table headers)
    CLIMATE_PARAMS = {
        'temperature_2m_max': {'unit': 'Temperature (°C)', 'color': '#FF4444', 'display_name': 'Temp 2m\nMax (°C)'},
        'temperature_2m_min': {'unit': 'Temperature (°C)', 'color': '#FF8888', 'display_name': 'Temp 2m\nMin (°C)'},
        'temperature_2m_mean': {'unit': 'Temperature (°C)', 'color': '#FF6B6B', 'display_name': 'Temp 2m\nMean (°C)'},
        'wind_speed_10m_max': {'unit': 'Wind Speed (m/s)', 'color': '#96CEB4', 'display_name': 'Wind Speed\n10m Max \n(m/s)'},
        'wind_gusts_10m_max': {'unit': 'Wind Speed (m/s)', 'color': '#FFEEAD', 'display_name': 'Wind Gusts\n10m Max \n(m/s)'},
        'relative_humidity_2m': {'unit': 'Humidity (%)', 'color': '#0000FF', 'display_name': 'Relative \nHumidity\n2m (%)'},
        'dew_point_2m': {'unit': 'Temperature (°C)', 'color': '#FFA07A', 'display_name': 'Dew Point\n2m (°C)'},
        'surface_pressure': {'unit': 'Pressure (hPa)', 'color': '#D4A5A5', 'display_name': 'Surface\nPressure \n(hPa)'},
        'vapour_pressure_deficit': {'unit': 'Pressure (hPa)', 'color': '#DDA0DD', 'display_name': 'Vapour\nPressure \n(hPa)'},
        'soil_temperature_100_to_255cm': {'unit': 'Temperature (°C)', 'color': '#4ECDC4', 'display_name': 'Soil Temp\n100-255cm \n(°C)'},
        'soil_moisture_100_to_255cm': {'unit': 'Soil Moisture', 'color': '#20B2AA', 'display_name': 'Soil Moisture\n100-255cm \n(°C)'},
        'wet_bulb_temperature_2m': {'unit': 'Temperature (°C)', 'color': '#45B7D1', 'display_name': 'Wet Bulb\n2m (°C)'},
        'total_column_integrated_water_vapour': {'unit': 'Water Vapour (kPa)', 'color': '#8FBC8F', 'display_name': 'Water\nVapour (kPa)'},
        'direct_radiation': {'unit': 'Radiation (W/m$^2$)', 'color': '#FFB6C1', 'display_name': 'Direct\nRadiation \n(W/m$^2$)'},
    }
    CLIMATE_NAME_MAP = {key: value['display_name'] for key, value in CLIMATE_PARAMS.items()}

    def __init__(self, main_window):
        super().__init__()
        self.ui = main_window
        self.dataset_handler = DatasetHandler()
        self.image_display_handler = ImageDisplayHandler()
        # Assume that climate_data_handler is already implemented and available
        self.climate_data_handler = ClimateDataHandler()
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components and connect signals."""
        self.dataset_handler.populate_dataset_combo(self.ui.analysisChooseCombo)
        self.ui.viewAnalysisButton.clicked.connect(self.generate_analysis)

        self.ui.analysisChooseCombo.showPopup = self.create_show_popup_handler(self.ui.analysisChooseCombo.showPopup)

    def create_show_popup_handler(self, original_show_popup):
        "Create a custom handler for the dataset combo box popup."

        def handler():
            self.refresh_datasets()
            original_show_popup()
        return handler

    def refresh_datasets(self):
        "Refresh the dataset combo box with the latest datasets."
        self.dataset_handler.populate_dataset_combo(self.ui.analysisChooseCombo)

    def load_and_process_data(self, metadata):
        """Process metadata JSON into a pandas DataFrame."""
        processed_data = []
        for image_name, image_data in metadata.get('images', {}).items():
            row = {
                'year': image_data['year'],
                **{f'class_{i+1}': freq for i, freq in enumerate(image_data['freq'])},
                **image_data['climate']
            }
            processed_data.append(row)
        return pd.DataFrame(processed_data).sort_values('year')

    def process_climate_data(self):
        """
        Fetch and update climate data based on the dataset's metadata.
        Returns the updated metadata or None on error.
        """
        dataset_name = self.ui.analysisChooseCombo.currentText()
        if not dataset_name:
            AlertHandler.show_warning("Please select a dataset.")
            return None

        dataset_path = os.path.join("Microclimate Analysis Data", dataset_name)
        metadata_path = os.path.join(dataset_path, "metadata.json")

        if not os.path.exists(metadata_path):
            AlertHandler.show_error("metadata.json not found.")
            return None

        try:
            with open(metadata_path, "r") as file:
                metadata = json.load(file)

            latitude = metadata.get("coordinates", {}).get("latitude")
            longitude = metadata.get("coordinates", {}).get("longitude")
            years = {details["year"] for details in metadata.get("images", {}).values()}

            # Fetch and update climate data
            climate_data = self.climate_data_handler.fetch_climate_data(latitude, longitude, years)
            self.climate_data_handler.update_metadata(dataset_path, climate_data)

            # Reload and return the updated metadata
            with open(metadata_path, "r") as updated_file:
                updated_metadata = json.load(updated_file)
            return updated_metadata

        except Exception as e:
            AlertHandler.show_error(f"An error occurred while processing climate data: {e}")
            return None

    def plot_land_cover_changes(self, df, save_path):
        """Create and save a bar plot showing land cover changes."""
        plt.figure(figsize=(15, 8))
        ax = plt.gca()
        ax.grid(True, alpha=0.3, color='#cccccc')
        
        x = np.arange(len(df['year']))
        width = 0.1
        for i, (col, name, color) in enumerate(zip(self.LAND_COVER_COLS,
                                                    self.LAND_COVER_NAMES,
                                                    self.LAND_COVER_COLORS)):
            values = df[col] * 100  # Convert to percentage
            plt.bar(x + i * width, values, width, label=name, color=color)
        
        plt.ylabel('Percentage', fontsize=16)
        plt.xlabel('Year', fontsize=16)
        plt.title('Land Cover Changes by Year', fontsize=14)
        plt.xticks(x + width * 3.5, df['year'])
        plt.legend(title='Land Cover Classes', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.close()

    def plot_land_cover_climate(self, df, save_path):
        """Create and save a combined plot for land cover changes and climate parameters."""
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = '#cccccc'
        plt.rcParams['legend.fontsize'] = 16

        fig = plt.figure(figsize=(30, 12))
        plt.subplots_adjust(left=0.25)
        
        # Compute urban vs. rural percentages using specified urban classes
        urban_classes = ['class_3', 'class_4', 'class_8']
        df['urban'] = df[urban_classes].sum(axis=1) * 100
        df['rural'] = (1 - df[urban_classes].sum(axis=1)) * 100
        
        ax_cover = plt.gca()
        ax_cover.fill_between(df['year'], 0, df['rural'], alpha=0.3, label='Rural', color='#228B22')
        ax_cover.fill_between(df['year'], df['rural'], 100, alpha=0.3, label='Urban', color='#404040')
        ax_cover.set_ylabel('Land Cover (%)', fontsize=16)
        ax_cover.set_xlabel('Year', fontsize=16)
        
        # Group climate parameters by unit using the unified CLIMATE_PARAMS
        unit_groups = {}
        for param, details in self.CLIMATE_PARAMS.items():
            unit_groups.setdefault(details['unit'], []).append(param)
        
        axes = [ax_cover]
        offset = 0
        # Create twin axes for each climate unit group
        for i, (unit, unit_params) in enumerate(unit_groups.items()):
            ax = ax_cover.twinx()
            if i > 0:
                offset += 60
                ax.spines['right'].set_position(('outward', offset))
            unit_data = df[unit_params].values.flatten()
            data_range = np.ptp(unit_data)
            data_min = np.min(unit_data)
            margin = data_range * 0.1
            ax.set_ylim(data_min - margin, np.max(unit_data) + margin)
            
            for param in unit_params:
                if param in df.columns:
                    ax.plot(df['year'], df[param],
                            label=f'{param} ({unit})',
                            color=self.CLIMATE_PARAMS[param]['color'],
                            linewidth=3, marker='o')
            ax.set_xticks(df['year'])
            ax.set_xticklabels(df['year'])
            ax.set_ylabel(unit, fontsize=14)
            axes.append(ax)
        
        # Combine legends from all axes
        lines, labels = [], []
        for ax in axes:
            ax_lines, ax_labels = ax.get_legend_handles_labels()
            lines.extend(ax_lines)
            labels.extend(ax_labels)
        plt.legend(lines, labels, bbox_to_anchor=(-0.1, 0.5),
                   loc='center right', frameon=True, fancybox=True, shadow=True)
        
        plt.title('Land Cover Change Over Time with Climate Trends', fontsize=32)
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.close()

    def create_tables(self, df, table_save_path):
        """Create and save both land cover and climate parameter tables as images."""
        # Build land cover table data
        land_cover_df = df.copy()
        for col, name in zip(self.LAND_COVER_COLS, self.LAND_COVER_NAMES):
            land_cover_df[f'{name} (%)'] = (land_cover_df[col] * 100).round(2)
        land_cover_data = land_cover_df[['year'] + [f'{name} (%)' for name in self.LAND_COVER_NAMES]]
        
        # Build climate table data by excluding land cover and extra columns
        exclude_cols = set(self.LAND_COVER_COLS + ['year', 'urban', 'rural'])
        climate_cols = [col for col in df.columns if col not in exclude_cols]
        climate_data = df[['year'] + climate_cols].round(2)
        
        # Save tables using helper with appropriate name mappings
        self._create_table_image(
            land_cover_data, 
            'Land Cover Data\n\n',
            os.path.join(table_save_path, 'land_cover_table.png'),
            {**dict(zip(self.LAND_COVER_COLS, self.LAND_COVER_NAMES)), 'year': 'Year'}
        )
        self._create_table_image(
            climate_data, 
            'Climate Parameters\n\n',
            os.path.join(table_save_path, 'climate_table.png'),
            self.CLIMATE_NAME_MAP
        )

    def _create_table_image(self, df, title, save_path, name_map):
        """Create and save a table visualization with consistent row heights."""
        df = df.copy()
        df.columns = [name_map.get(col, col) for col in df.columns]
        
        n_rows, n_cols = df.shape
        row_height = 0.4
        fig_height = max(2, (n_rows + 1) * row_height + 0.6)
        fig_width = max(6, n_cols * 1.2)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')
        
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            cellColours=[['#f9f9f9'] * n_cols for _ in range(n_rows)]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 1.2)
        
        for col in range(n_cols):
            table[(0, col)].set_height(row_height)
            table[(0, col)].set_facecolor('#4CAF50')
            table[(0, col)].set_text_props(color='white', weight='bold', wrap=True)
            for row in range(n_rows):
                table[(row + 1, col)].set_height(row_height)
        
        plt.title(title, pad=10, fontsize=12, fontweight='bold')
        plt.savefig(save_path, bbox_inches='tight', dpi=300,
                    facecolor='white', edgecolor='none', pad_inches=0.2)
        plt.close()

    def display_analysis_results(self, analysis_path):
        """Display all analysis images in the scroll area with full-width scaling."""
        scroll_width = self.ui.analysisScrollAreaContents.width()
        original_create_image_widget = self.image_display_handler.create_image_widget

        def create_full_width_image_widget(image_path, show_year_input=False, remove_callback=None):
            widget = original_create_image_widget(image_path, show_year_input, remove_callback)
            for child in widget.children():
                if isinstance(child, QLabel) and child.pixmap() is not None:
                    pixmap = QPixmap(image_path)
                    scaled_pixmap = pixmap.scaled(scroll_width - 40, scroll_width - 40,
                                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    child.setPixmap(scaled_pixmap)
            return widget

        self.image_display_handler.create_image_widget = create_full_width_image_widget

        image_paths = [
            os.path.join(analysis_path, 'land_cover_changes.png'),
            os.path.join(analysis_path, 'land_cover_climate.png'),
            os.path.join(analysis_path, 'land_cover_table.png'),
            os.path.join(analysis_path, 'climate_table.png')
        ]
        self.image_display_handler.populate_scroll_area(
            self.ui.analysisScrollAreaContents,
            image_paths,
            show_year_input=False,
            images_per_row=1
        )
        self.image_display_handler.create_image_widget = original_create_image_widget

    def generate_analysis(self):
        """
        When the 'View Analysis' button is clicked, this method first fetches and updates
        the climate data (updating the metadata file) and then generates the graphs, tables,
        and CSV output based on the updated metadata.
        """
        try:
            dataset_name = self.ui.analysisChooseCombo.currentText()
            if not dataset_name:
                raise ValueError("Please select a dataset")

            base_path = os.path.join("Microclimate Analysis Data", dataset_name)
            metadata_path = os.path.join(base_path, "metadata.json")
            analysis_path = os.path.join(base_path, "analysis")

            if not os.path.exists(metadata_path):
                raise FileNotFoundError("metadata.json not found")

            os.makedirs(analysis_path, exist_ok=True)

            self.loading_dialog = LoadingDialog("Fetching climate data and generating analysis...")
            self.loading_dialog.show()
            try:
                # Fetch and update climate data; use the updated metadata for analysis
                updated_metadata = self.process_climate_data()
                if updated_metadata is None:
                    return

                df = self.load_and_process_data(updated_metadata)

                # Generate analysis graphs and tables
                self.plot_land_cover_changes(df, os.path.join(analysis_path, 'land_cover_changes.png'))
                self.plot_land_cover_climate(df, os.path.join(analysis_path, 'land_cover_climate.png'))
                self.create_tables(df, analysis_path)

                # Save the analysis data as CSV
                df.to_csv(os.path.join(analysis_path, "analysis_table.csv"), index=False)

                self.display_analysis_results(analysis_path)
                AlertHandler.show_info("Analysis completed successfully!")

            finally:
                self.loading_dialog.close()

        except Exception as e:
            AlertHandler.show_error(f"Error generating analysis: {str(e)}")
