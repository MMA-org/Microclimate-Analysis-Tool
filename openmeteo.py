import requests

def fetch_hourly_features(latitude, longitude, years):
    """
    Fetch hourly averages of key features (temperature, humidity, precipitation, etc.) using Open-Meteo API.
    """
    base_url = "https://archive-api.open-meteo.com/v1/era5"
    features = {}

    # List of hourly parameters to fetch
    hourly_fields = [
        "temperature_2m_mean"
    ]

    for year in years:
        try:
            # Define start and end dates for the year
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"

            # API request parameters
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "daily": ",".join(hourly_fields),
                "timezone": "auto",
            }

            # Send GET request to Open-Meteo API
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response
            data = response.json()
            hourly_data = data["daily"]

            # Safely handle None values in the response
            def safe_mean(values):
                valid_values = [v for v in values if v is not None]
                return sum(valid_values) / len(valid_values) if valid_values else None

            def safe_sum(values):
                return sum(v for v in values if v is not None)

            features[year] = {
                "avg_temp": safe_mean(hourly_data["temperature_2m_mean"]),
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for year {year}: {e}")
            features[year] = {key: None for key in hourly_fields}

    return features

# Main script
if __name__ == "__main__":
    # Define location and years
    latitude = 31.980499
    longitude = 34.821086
    years = range(2010, 2021)

    # Fetch hourly features
    yearly_features = fetch_hourly_features(latitude, longitude, years)

    # Print results
    print("\nYearly Hourly Feature Averages:")
    for year, feature in yearly_features.items():
        print(f"\nYear: {year}, Avg. Temperature: {feature['avg_temp']:.2f}°C")



# import requests
# import json

# def fetch_climate_data(latitude, longitude, years):
#     base_url = "https://archive-api.open-meteo.com/v1/archive"
#     climate_data = {}

#     # ✅ Daily Parameters
#     daily_params = [
#         "temperature_2m_max",
#         "temperature_2m_min",
#         "temperature_2m_mean",
#         "apparent_temperature_max",
#         "apparent_temperature_min",
#         "apparent_temperature_mean",
#         "wind_speed_10m_max",
#         "wind_gusts_10m_max",
#         "shortwave_radiation_sum",
#         "et0_fao_evapotranspiration"
#     ]

#     # ✅ Hourly Parameters
#     hourly_params = [
#         "relative_humidity_2m",
#         "dew_point_2m",
#         "surface_pressure",
#         "vapour_pressure_deficit",
#         "soil_temperature_100_to_255cm",
#         "soil_moisture_100_to_255cm",
#         "wet_bulb_temperature_2m",
#         "total_column_integrated_water_vapour",
#         "shortwave_radiation",
#         "direct_radiation",
#         "diffuse_radiation",
#         "direct_normal_irradiance"
#     ]

#     for year in years:
#         try:
#             # 🌍 Daily Request
#             daily_response = requests.get(base_url, params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "start_date": f"{year}-01-01",
#                 "end_date": f"{year}-12-31",
#                 "daily": ",".join(daily_params),
#                 "timezone": "auto",
#                 "temporal_resolution": "native"
#             })
#             daily_response.raise_for_status()
#             daily_data = daily_response.json().get("daily", {})

#             # ⏱️ Hourly Request
#             hourly_response = requests.get(base_url, params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "start_date": f"{year}-01-01",
#                 "end_date": f"{year}-12-31",
#                 "hourly": ",".join(hourly_params),
#                 "timezone": "auto",
#                 "temporal_resolution": "native"
#             })
#             hourly_response.raise_for_status()
#             hourly_data = hourly_response.json().get("hourly", {})

#             # 🧮 Aggregation Functions
#             def safe_mean(values):
#                 valid = [v for v in values if v is not None]
#                 return sum(valid) / len(valid) if valid else None

#             def safe_sum(values):
#                 return sum(v for v in values if v is not None)

#             # 📊 Merging Daily and Hourly Data
#             climate_data[year] = {
#                 # Daily Data
#                 "temperature_max": safe_mean(daily_data.get("temperature_2m_max", [])),
#                 "wind_speed_10m": safe_mean(hourly_data.get("wind_speed_10m", [])),
#                 "wind_speed_100m": safe_mean(hourly_data.get("wind_speed_100m", [])),
#                 "wind_direction_10m": safe_mean(hourly_data.get("wind_direction_10m", [])),
#                 "wind_direction_100m": safe_mean(hourly_data.get("wind_direction_100m", [])),
#                 "wind_gusts_10m": safe_mean(hourly_data.get("wind_gusts_10m", [])),

#                 "temperature_min": safe_mean(daily_data.get("temperature_2m_min", [])),
#                 "temperature_mean": safe_mean(daily_data.get("temperature_2m_mean", [])),
#                 "apparent_temp_max": safe_mean(daily_data.get("apparent_temperature_max", [])),
#                 "apparent_temp_min": safe_mean(daily_data.get("apparent_temperature_min", [])),
#                 "apparent_temp_mean": safe_mean(daily_data.get("apparent_temperature_mean", [])),
#                 "precipitation_sum": safe_sum(daily_data.get("precipitation_sum", [])),
#                 "wind_speed_max": safe_mean(daily_data.get("wind_speed_10m_max", [])),
#                 "wind_gusts_max": safe_mean(daily_data.get("wind_gusts_10m_max", [])),
#                 "wind_direction_dominant": safe_mean(daily_data.get("wind_direction_10m_dominant", [])),
#                 "shortwave_radiation_sum": safe_sum(daily_data.get("shortwave_radiation_sum", [])),
#                 "evapotranspiration": safe_sum(daily_data.get("et0_fao_evapotranspiration", [])),

#                 # Hourly Data
#                 "relative_humidity": safe_mean(hourly_data.get("relative_humidity_2m", [])),
#                 "dew_point": safe_mean(hourly_data.get("dew_point_2m", [])),
#                 "surface_pressure": safe_mean(hourly_data.get("surface_pressure", [])),
#                 "cloud_cover": safe_mean(hourly_data.get("cloud_cover", [])),
#                 "cloud_cover_low": safe_mean(hourly_data.get("cloud_cover_low", [])),
#                 "cloud_cover_high": safe_mean(hourly_data.get("cloud_cover_high", [])),
#                 "vapour_pressure_deficit": safe_mean(hourly_data.get("vapour_pressure_deficit", [])),
#                 "soil_temp_0_7cm": safe_mean(hourly_data.get("soil_temperature_0_to_7cm", [])),
#                 "soil_temp_7_28cm": safe_mean(hourly_data.get("soil_temperature_7_to_28cm", [])),
#                 "soil_temp_28_100cm": safe_mean(hourly_data.get("soil_temperature_28_to_100cm", [])),
#                 "soil_temp_100_255cm": safe_mean(hourly_data.get("soil_temperature_100_to_255cm", [])),
#                 "soil_moisture_0_7cm": safe_mean(hourly_data.get("soil_moisture_0_to_7cm", [])),
#                 "soil_moisture_7_28cm": safe_mean(hourly_data.get("soil_moisture_7_to_28cm", [])),
#                 "soil_moisture_28_100cm": safe_mean(hourly_data.get("soil_moisture_28_to_100cm", [])),
#                 "soil_moisture_100_255cm": safe_mean(hourly_data.get("soil_moisture_100_to_255cm", [])),
#                 "wet_bulb_temp": safe_mean(hourly_data.get("wet_bulb_temperature_2m", [])),
#                 "integrated_water_vapour": safe_mean(hourly_data.get("total_column_integrated_water_vapour", [])),
#                 "shortwave_radiation": safe_sum(hourly_data.get("shortwave_radiation", [])),
#                 "direct_radiation": safe_sum(hourly_data.get("direct_radiation", [])),
#                 "diffuse_radiation": safe_sum(hourly_data.get("diffuse_radiation", [])),
#                 "direct_normal_irradiance": safe_sum(hourly_data.get("direct_normal_irradiance", [])),
#             }

#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching data for year {year}: {e}")
#             # Fill the entry with None values for consistency
#             climate_data[year] = {}
#             for param in (daily_params + hourly_params):
#                 climate_data[year][param] = None

#     return climate_data

# # Example usage
# latitude = 40.7128  # Example coordinates (New York)
# longitude = -74.0060
# years = [2000, 2010, 2020]  # Example years

# climate_data = fetch_climate_data(latitude, longitude, years)

# # --------------------
# # PRINTING EACH PARAM FOR ALL YEARS IN ONE LINE
# # --------------------
# # Collect all parameter names from any given year (assuming they are consistent across years).
# # We can just look at the first year in the `years` list if we are sure it has the full set.
# all_params = list(climate_data[years[0]].keys())

# print("PARAMETER," + ",".join(str(y) for y in years))  # Header row

# for param in all_params:
#     # Build a row: parameter + each year's value for that parameter
#     values = [str(climate_data[year].get(param, None)) for year in years]
#     print(f"{param}," + ",".join(values))
