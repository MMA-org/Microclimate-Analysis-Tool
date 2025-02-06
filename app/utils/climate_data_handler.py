import requests
import json
import os

class ClimateDataHandler:
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    DAILY_PARAMS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
    ]

    HOURLY_PARAMS = [
        "relative_humidity_2m",
        "dew_point_2m",
        "surface_pressure",
        "vapour_pressure_deficit",
        "soil_temperature_100_to_255cm",
        "soil_moisture_100_to_255cm",
        "wet_bulb_temperature_2m",
        "total_column_integrated_water_vapour",
        "direct_radiation",
    ]

    def fetch_climate_data(self, latitude, longitude, years):
        climate_data = {}

        for year in years:
            year_data = {}

            try:
                # 🌍 Fetch Daily Data
                daily_response = requests.get(self.BASE_URL, params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": f"{year}-01-01",
                    "end_date": f"{year}-12-31",
                    "daily": ",".join(self.DAILY_PARAMS),
                    "timezone": "auto"
                })
                daily_response.raise_for_status()
                daily_data = daily_response.json().get("daily", {})

                # ⏱️ Fetch Hourly Data
                hourly_response = requests.get(self.BASE_URL, params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": f"{year}-01-01",
                    "end_date": f"{year}-12-31",
                    "hourly": ",".join(self.HOURLY_PARAMS),
                    "timezone": "auto"
                })
                hourly_response.raise_for_status()
                hourly_data = hourly_response.json().get("hourly", {})

                def safe_mean(values):
                    valid = [v for v in values if v is not None]
                    return sum(valid) / len(valid) if valid else None

                for param in self.DAILY_PARAMS:
                    year_data[param] = safe_mean(daily_data.get(param, []))

                # Aggregate Hourly Data
                for param in self.HOURLY_PARAMS:
                    year_data[param] = safe_mean(hourly_data.get(param, []))

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for year {year}: {e}")
                year_data = {param: None for param in (self.DAILY_PARAMS + self.HOURLY_PARAMS)}

            climate_data[year] = year_data

        return climate_data

    def update_metadata(self, dataset_path, climate_data):
        metadata_path = os.path.join(dataset_path, "metadata.json")
        with open(metadata_path, "r") as file:
            metadata = json.load(file)

        for image, details in metadata.get("images", {}).items():
            year = details.get("year")
            if year and year in climate_data:
                # Format float values to .4f
                details["climate"] = {
                    k: round(v, 4) if isinstance(v, float) else v
                    for k, v in climate_data[year].items()
                }

        with open(metadata_path, "w") as file:
            json.dump(metadata, file, indent=4)


