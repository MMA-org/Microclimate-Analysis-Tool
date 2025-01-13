import requests

class Geocoder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"

    def get_coordinates(self, location):
        """Fetch coordinates (latitude, longitude) for a given location."""
        params = {
            "q": location,
            "key": self.api_key,
            "limit": 1,
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                geometry = data["results"][0]["geometry"]
                return geometry["lat"], geometry["lng"]
        return None, None

    def get_cities_within_bounds(self, southwest, northeast):
        """Fetch a list of cities within the given bounding box."""
        params = {
            "bounds": f"{southwest['lat']},{southwest['lng']},{northeast['lat']},{northeast['lng']}",
            "key": self.api_key,
            "limit": 100,
        }
        response = requests.get(self.base_url, params=params)
        cities = []
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                for result in data["results"]:
                    city = result["components"].get("city") or result["components"].get("town")
                    if city and city not in cities:
                        cities.append(city)
        return cities

    def get_country_bounds(self, country_name):
        """Fetch the bounding box of a country by name."""
        params = {
            "q": country_name,
            "key": self.api_key,
            "limit": 1,
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                return data["results"][0].get("bounds")
        return None

