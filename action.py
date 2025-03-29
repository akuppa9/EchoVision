import os
import requests
from dotenv import load_dotenv

load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
class Action:
    
    def __init__(self):
        pass
        
    def get_current_location(self):
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={google_maps_api_key}"
        payload = {"considerIp": "true"}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("location")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_route_to_destination(self,origin, destination):
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
        
    def get_nearby_places(self, location, place_type, radius=1000):

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        # Convert tuple to string if necessary
        if isinstance(location, tuple):
            location = f"{location[0]},{location[1]}"
        params = {
            "location": location,
            "radius": radius,
            "type": place_type,
            "key": google_maps_api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Places API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")
        
        
if __name__ == "__main__":
    actions = Action()

    # Test get_current_location
    try:
        current_location = actions.get_current_location()
        print("Current location:", current_location)
    except Exception as e:
        print("Error getting current location:", e)

    # Test get_route_to_destination
    try:
        origin = "1600 Amphitheatre Parkway, Mountain View, CA"
        destination = "1 Infinite Loop, Cupertino, CA"
        route = actions.get_route_to_destination(origin, destination)
        print("Route obtained from origin to destination:")
        # For brevity, print only the first step of the first leg
        first_leg = route["routes"][0]["legs"][0]
        first_step = first_leg["steps"][0]
        print(f"Step: {first_step['html_instructions']} (Distance: {first_step['distance']['text']}, Duration: {first_step['duration']['text']})")
    except Exception as e:
        print("Error getting route:", e)

    # Test get_nearby_places
    try:
        # Use current location if available, else use a default location (Mountain View, CA)
        if current_location:
            location_str = f"{current_location['lat']},{current_location['lng']}"
        else:
            location_str = "37.4220,-122.0841"
        
        # Test for nearby gas stations
        nearby_gas_stations = actions.get_nearby_places(location_str, "gas_station")
        print("Nearby Gas Stations:")
        for place in nearby_gas_stations.get("results", []):
            print(f"- {place.get('name')} at {place.get('vicinity')}")

        # Test for nearby restaurants
        nearby_restaurants = actions.get_nearby_places(location_str, "restaurant")
        print("\nNearby Restaurants:")
        for place in nearby_restaurants.get("results", []):
            print(f"- {place.get('name')} at {place.get('vicinity')}")
    except Exception as e:
        print("Error getting nearby places:", e)