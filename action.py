import os
import time
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import re
import multiprocessing

load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
ELEVENLABS_API_KEY = "sk_d7df5f33f81a50ff1e55513a56afbf681a59d8a96bc2587c"
#ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
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

    def get_route_to_destination(self, origin, destination):
        process = multiprocessing.Process(
            target=self.get_route_to_destination, 
            args=(origin, destination)
        )
        process.start()

    def get_route_to_destination_async(self,origin, destination):
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
                route = data["routes"][0]
                leg = route["legs"][0]
                steps = leg["steps"]
                
                instructions_list = []
                for step in steps:
                    # Get the HTML instructions and convert to plain text.
                    html_instruction = step.get("html_instructions", "")
                    instruction = re.sub('<.*?>', '', html_instruction)
                    
                    # Collect distance and duration for clarity.
                    #distance = step["distance"]["text"]
                    #duration = step["duration"]["text"]
                    
                    print(instruction)
                    
                    #call audio function
                    instructions_list.append(instruction)
                    duration_seconds = step["duration"]["value"]
                    time.sleep(duration_seconds)
                
                return instructions_list
                
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Maps API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")
        
    def get_nearby_places(self, location, place_type, radius=1000, audio=True):

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
                for place in data.get("results", []): 
                    print(f"- {place.get('name')} , {place.get('vicinity')}")
                    if audio:
                        #call audio
                        pass
                return data
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Places API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")
        
    def surrounding (self, text):
        #add audio call
        pass
    
        


if __name__ == "__main__":
    actions = Action()

    # Test get_current_location
    """
    try:
        current_location = actions.get_current_location()
        print("Current location:", current_location)
    except Exception as e:
        print("Error getting current location:", e)
"""
    # Test get_route_to_destination
    actions = Action()
    origin = "1600 Amphitheatre Parkway, Mountain View, CA"
    destination = "GOCO, 2187 Neil Avenue, Columbus"
    try:
        directions = actions.get_route_to_destination(origin, destination)
  
    except Exception as e:
        print("Error:", e)

"""
    # Test get_nearby_places
    try:
        current_location = actions.get_current_location()
        # Use current location if available, else use a default location (Mountain View, CA)
        if current_location:
            location_str = f"{current_location['lat']},{current_location['lng']}"
        else:
            location_str = "37.4220,-122.0841"
        
        # Test for nearby gas stations
        nearby_gas_stations = actions.get_nearby_places(location_str, "gas_station")
        
        first_place = nearby_gas_stations[0]
        destination = f"{first_place.get('name')}, {first_place.get('vicinity')}"
        actions.get_route_to_destination(location_str, destination)
        

    except Exception as e:
        print("Error getting nearby places:", e)
        
"""