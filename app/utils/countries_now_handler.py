import requests
import pycountry

BASE_URL = "https://countriesnow.space/api/v0.1/countries/cities"

def get_countries():
    """Fetch a list of all country names."""
    return [country.name for country in pycountry.countries]

def get_cities_by_country(country_name):
    """Fetch cities for a given country using Countries Now API."""
    payload = {"country": country_name}
    headers = {"Content-Type": "application/json"}
    response = requests.post(BASE_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data.get("error", True):
            return data.get("data", [])
        else:
            print(f"Error fetching cities: {data.get('msg')}")
            return []
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
