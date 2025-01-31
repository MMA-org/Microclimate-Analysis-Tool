"""
Utility functions for handling locations in the GUI application.
"""
import requests
import pycountry

CN_URL = "https://countriesnow.space/api/v0.1/countries/cities"
OSM_URL = "https://nominatim.openstreetmap.org/search.php"

def get_countries():
    "Fetch a list of all country names."

    return [country.name for country in pycountry.countries]

def get_cities_by_country(country_name):
    "Fetch cities for a given country using Countries Now API."

    payload = {"country": country_name}
    headers = {"Content-Type": "application/json"}
    response = requests.post(CN_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return []
        
    data = response.json()
    if not data.get("error", True):
        return data.get("data", [])

def get_coordinates(country, city):
    "Fetch coordinates (latitude, longitude) for a given city using OpenStreetMap API."

    query = f"{city}, {country}" if country else city
    params = {"q": query, "format": "jsonv2"}
    headers = {"User-Agent": "MyApp/1.0"}
    
    response = requests.get(OSM_URL, params=params, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()
    return None if not data else {
        "latitude": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"])
    }
        
def setup_country_combobox(combo):
    "Set up the country ComboBox with placeholder and items."

    combo.addItems(["Select a country"])
    combo.addItems(sorted(get_countries()))

def setup_city_combobox(country_combo, city_combo):
    "Fetch and set up the city ComboBox based on selected country."

    country = country_combo.currentText().strip()
    city_combo.clear()

    if not country or country == "Select a country":
        return
    
    cities = get_cities_by_country(country)
    city_combo.addItems(sorted(cities) if cities else [])
