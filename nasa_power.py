import requests

def fetch_daily_features(latitude, longitude, years):
    """
    Fetch daily temperature (T2M) data and compute the annual average using NASA POWER API.
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    features = {}

    # Parameter to fetch
    parameter = "T2M"

    for year in years:
        try:
            # Define start and end dates for the year
            start_date = f"{year}0101"
            end_date = f"{year}1231"

            # API request parameters
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start": start_date,
                "end": end_date,
                "parameters": parameter,
                "community": "AG",
                "format": "JSON",
            }

            # Send GET request to NASA POWER API
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response
            data = response.json()
            daily_data = data["properties"]["parameter"]

            # Compute the annual average temperature
            temperatures = daily_data[parameter].values()
            valid_temps = [temp for temp in temperatures if temp is not None]

            avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else None

            features[year] = {
                "avg_temp": avg_temp,
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for year {year}: {e}")
            features[year] = {"avg_temp": None}

    return features

# Main script
if __name__ == "__main__":
    # Define location and years
    latitude = 31.980499
    longitude = 34.821086
    years = range(2010, 2021)

    # Fetch daily features
    yearly_features = fetch_daily_features(latitude, longitude, years)

    # Print results
    print("\nYearly Daily Feature Averages (NASA POWER):")
    for year, feature in yearly_features.items():
        if feature["avg_temp"] is not None:
            print(f"Year: {year}, Avg. Temperature: {feature['avg_temp']:.2f}°C")
        else:
            print(f"Year: {year}, Avg. Temperature: No data available")
