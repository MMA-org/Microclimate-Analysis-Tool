import requests
from geopy.distance import geodesic
from collections import defaultdict

# OpenWeatherMap API key
OPENWEATHER_API_KEY = "9c21382cd9ba4fda32279034e331a809"  # Replace with your OpenWeatherMap API key

# NCDC CDO API token
NCDC_TOKEN = "WkqpDPQmPaoHFSkyiRvdeJHpFnQktiuQ"  # Replace with your NCDC token

# Function to get latitude and longitude of a city
def get_lat_long(city_name, country_code=None):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{city_name},{country_code}" if country_code else city_name,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        if results:
            latitude = results[0]["lat"]
            longitude = results[0]["lon"]
            return latitude, longitude
        else:
            print(f"City '{city_name}' not found.")
            return None, None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None, None

# Function to get nearby stations
def get_nearby_stations(latitude, longitude):
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/stations"
    headers = {"token": NCDC_TOKEN}
    
    params = {
        "datasetid": "GHCND",
        "extent": f"{latitude-1},{longitude-1},{latitude+1},{longitude+1}",  # Define bounding box
        "limit": 100,  # Fetch a larger number of stations
    }
    
    response = requests.get(base_url, headers=headers, params=params)
    print(f"Station Request URL: {response.url}")
    if response.status_code == 200:
        stations = response.json().get("results", [])
        if stations:
            city_coords = (latitude, longitude)
            for station in stations:
                print(f"Station ID: {station['id']}, Name: {station['name']}")
                station_coords = (station["latitude"], station["longitude"])
                station["distance"] = geodesic(city_coords, station_coords).kilometers
            
            # Sort stations by distance
            sorted_stations = sorted(stations, key=lambda x: x["distance"])
            return sorted_stations
        else:
            print("No nearby stations found.")
            return []
    else:
        print(f"Error fetching stations: {response.status_code}, {response.text}")
        return []

# Function to get temperature data by station
def get_temperature_data_by_station(station_id, year):
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": NCDC_TOKEN}
    
    params = {
        "datasetid": "GHCND",
        "datatypeid": "TAVG",
        "startdate": f"{year}-01-01",
        "enddate": f"{year}-12-31",
        "units": "metric",
        "limit": 1000,
        "stationid": station_id,
    }
    
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("results", [])
        return data
    else:
        print(f"Error fetching data for station {station_id}, year {year}: {response.status_code}, {response.text}")
        return []

# Function to calculate yearly average temperatures
def calculate_yearly_avg(temperature_data):
    temps = [record["value"] for record in temperature_data if record["value"] is not None]
    if temps:
        return sum(temps) / len(temps)
    return None

# Function to fetch data from multiple stations for a year
def get_temperature_data_from_stations(stations, year):
    for station in stations:
        station_id = station["id"]
        temperature_data = get_temperature_data_by_station(station_id, year)
        if temperature_data:
            return temperature_data, station_id
    print(f"No data found for year {year} in any nearby stations.")
    return None, None

# Combined function with station fallback
def get_city_temperature_data_with_station_fallback(city_name, country_code, years):
    latitude, longitude = get_lat_long(city_name, country_code)
    
    if latitude is not None and longitude is not None:
        stations = get_nearby_stations(latitude, longitude)
        if not stations:
            print(f"No stations found for {city_name}.")
            return {}
        
        # Use the closest station (first in sorted list)
        closest_station = stations[0]
        print(f"Closest Station ID: {closest_station['id']}")
        print(f"Station Name: {closest_station['name']}")
        print(f"Latitude: {closest_station['latitude']}")
        print(f"Longitude: {closest_station['longitude']}")
        
        yearly_avg_temps = {}
        for year in years:
            temperature_data, station_id = get_temperature_data_from_stations(stations, year)
            if temperature_data:
                yearly_avg = calculate_yearly_avg(temperature_data)
                if yearly_avg is not None:
                    print(f"Year: {year}, Picked Station: {station_id}, Average Temperature: {yearly_avg:.2f}°C")
                    yearly_avg_temps[year] = yearly_avg
                else:
                    print(f"No valid temperature data for year {year}.")
            else:
                print(f"No temperature data available for year {year}.")
        
        return yearly_avg_temps
    else:
        print(f"Unable to fetch temperature data for {city_name}, {country_code}.")
        return {}

# Example usage
city = "Haifa"
country = "IL"
years = [2020, 2021]

yearly_avg_temps = get_city_temperature_data_with_station_fallback(city, country, years)

# Print results
for year, avg_temp in yearly_avg_temps.items():
    print(f"{city}, Year: {year}, Average Temperature: {avg_temp:.2f}°C")

