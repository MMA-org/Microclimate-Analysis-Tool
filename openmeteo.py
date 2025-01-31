import requests
from datetime import datetime, timedelta

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
