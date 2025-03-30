import os
import time
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os
import re
import multiprocessing

load_dotenv()

google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
class Action:
    
    def __init__(self):
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVEL_LABS_API_KEY"),
        )
        pass

    def tts(self, text):
        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        )

        play(audio)
        
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
        print("started")
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
                
                    print(instruction)

                    self.tts(instruction)
                    
                    #call audio function
                    instructions_list.append(instruction)
                    duration_seconds = step["duration"]["value"]
                    print(duration_seconds)
                    time.sleep(duration_seconds)
                
                return instructions_list
                
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Maps API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")
        
    def get_nearby_places(self, location, place_type, radius=1000):

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
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
                return data
            else:
                error_message = data.get("error_message", "Unknown error")
                raise Exception(f"Google Places API error: {data.get('status')} - {error_message}")
        else:
            raise Exception(f"HTTP error: {response.status_code} - {response.text}")