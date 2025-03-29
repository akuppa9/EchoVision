import os
import requests
from dotenv import load_dotenv

load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
class Actions:
    
    def __init__(self):
        pass
        
    def get_current_location():
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={google_maps_api_key}"
        payload = {"considerIp": "true"}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("location")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_route_to_destination(origin, destination):
        mode = "walking"
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": google_maps_api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Maps API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")
