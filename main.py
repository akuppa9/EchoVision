from buffer import Buffer
import multiprocessing as mp
import cv2
import time
import re
import os
import json
from reasoning import reasoning
import threading
#import speech_recognition as sr
import base64

# Mock API functions (in a real app, these would make actual API calls)
def get_current_location():
    print("API CALL: Getting current location...")
    # Mock return value - in real app this would be from GPS
    return "37.7749,-122.4194"

def get_nearby_places(location, place_type, radius=5000):
    print(f"API CALL: Finding nearby {place_type} within {radius}m of {location}...")
    # Mock return values - in real app this would call Google Maps API
    mock_results = {
        "restaurant": "Chipotle Mexican Grill, 235 Main St, San Francisco, CA",
        "gas_station": "Shell Gas Station, 401 Market St, San Francisco, CA",
        "hospital": "SF General Hospital, 1001 Potrero Ave, San Francisco, CA"
    }
    return mock_results.get(place_type, f"No {place_type} found nearby")

def get_route_to_destination(origin, destination, mode="walking"):
    print(f"API CALL: Getting {mode} directions from {origin} to {destination}...")
    # Mock return value - in real app this would call routing API
    return f"Route: Head north for 2 blocks, then turn right onto Market St. Destination will be on your left in 500 feet."

# Function to parse the reasoning response
def parse_reasoning_response(response):
    try:
        lines = response.strip().split('\n')
        action_chain = ""
        next_action = ""
        parameter_to_save = ""
        
        for line in lines:
            if line.startswith("Action Chain:"):
                action_chain = line.replace("Action Chain:", "").strip()
            elif line.startswith("Next Action:"):
                next_action = line.replace("Next Action:", "").strip()
            elif line.startswith("Parameter to Save:"):
                parameter_to_save = line.replace("Parameter to Save:", "").strip()
        
        # Extract function name and parameters from next_action
        # Simple parsing for function calls like: function_name(param1="value1", param2="value2")
        if "image analysis" in next_action.lower():
            return {
                "action_type": "image_analysis",
                "action_chain": action_chain,
                "analysis": next_action,
                "parameter_to_save": parameter_to_save
            }
            
        function_match = re.match(r'(\w+)\((.*)\)', next_action)
        if not function_match:
            return None
            
        function_name = function_match.group(1)
        params_str = function_match.group(2)
        
        # Parse parameters
        params = {}
        if params_str:
            # Match key-value pairs like key="value" or key=value
            param_matches = re.findall(r'(\w+)=(?:"([^"]*)"|([\w\d\.\-\,]+))', params_str)
            for match in param_matches:
                key = match[0]
                # The value is either in group 1 (quoted) or group 2 (unquoted)
                value = match[1] if match[1] else match[2]
                params[key] = value
                
        return {
            "action_type": "api_call",
            "function": function_name,
            "parameters": params,
            "action_chain": action_chain,
            "parameter_to_save": parameter_to_save
        }
    except Exception as e:
        print(f"Error parsing reasoning response: {e}")
        print(f"Response was: {response}")
        return None

# Function to execute the API call based on the action
def execute_action(action_info):
    if action_info["action_type"] == "image_analysis":
        # No API call needed, just return the analysis
        return action_info["analysis"]
        
    function_name = action_info["function"]
    params = action_info["parameters"]
    
    if function_name == "get_current_location":
        return get_current_location()
    elif function_name == "get_nearby_places":
        location = params.get("location", "")
        place_type = params.get("type", "")
        radius = int(params.get("radius", 5000))
        return get_nearby_places(location, place_type, radius)
    elif function_name == "get_route_to_destination":
        origin = params.get("origin", "")
        destination = params.get("destination", "")
        mode = params.get("mode", "walking")
        return get_route_to_destination(origin, destination, mode)
    else:
        return f"Unknown function: {function_name}"

def process_query(images, query):
    print(f"Processing query: {query}")
    param_for_next_action = ""
    action_history = []
    final_result = ""
    
    # First call to reasoning to start the chain
    response = reasoning(images, query, param_for_next_action)
    print(f"Reasoning response:\n{response}")
    
    # Continue processing actions until we reach a final result
    while True:
        # Parse the reasoning response
        action_info = parse_reasoning_response(response)
        
        if not action_info:
            print("Could not parse reasoning response")
            break
            
        # Store action in history
        action_history.append(action_info)
        
        # If this is an image analysis, we're done
        if action_info["action_type"] == "image_analysis":
            final_result = action_info["analysis"]
            break
            
        # Execute the action
        action_result = execute_action(action_info)
        print(f"Action result: {action_result}")
        
        # Check if we need another action in the chain
        if not action_info["parameter_to_save"] or action_info["parameter_to_save"].lower() == "none":
            # This is the last action in the chain
            final_result = action_result
            break
            
        # Call reasoning again with the result as the parameter for the next action
        param_for_next_action = action_result
        response = reasoning(images, query, param_for_next_action)
        print(f"Next reasoning response:\n{response}")
    
    return {
        "final_result": final_result,
        "action_history": action_history
    }

def speech_recognition_thread(command_queue):
    """Thread function to listen for voice commands"""
    recognizer = sr.Recognizer()
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for commands...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                
            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            
            # Put the recognized text into the queue
            command_queue.put(text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
        except Exception as e:
            print(f"Unexpected error in speech recognition: {e}")
        
        time.sleep(0.1)  # Small delay to prevent CPU thrashing

# Commented out real camera process
"""
def camera_process(buffer):
    print("Camera process started")
    cap = cv2.VideoCapture('http://172.20.10.10:81/stream')  # Adjust URL to your MJPEG endpoint

    if not cap.isOpened():
        print("Error: Unable to open MJPEG stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            # If reading a frame failed, skip
            continue
        
        # Add the new frame to the buffer
        buffer.add(frame)
        print("Frame added")
"""

# Mock camera process that just adds the test image to the buffer
def camera_process(buffer):
    print("Mock camera process started - using Codesignal_Score.png")
    
    # Check if the test image exists
    test_image_path = "Codesignal_Score.png"
    if not os.path.exists(test_image_path):
        print(f"WARNING: Test image {test_image_path} not found. Please ensure it exists in the current directory.")
        return
    
    # Read the test image
    test_frame = cv2.imread(test_image_path)
    if test_frame is None:
        print(f"ERROR: Could not read test image {test_image_path}")
        return
    
    # Add test image to buffer once
    buffer.add(test_frame)
    print("Added test frame to buffer")
    
    # Sleep to keep the process alive
    while True:
        time.sleep(10)

def agent_process(buffer, command_queue):
    print("Agent process started")
    
    # Create a directory to save processed frames if it doesn't exist
    os.makedirs("processed_frames", exist_ok=True)
    
    while True:
        # Check if there's a command in the queue
        if not command_queue.empty():
            query = command_queue.get()
            print(f"Agent received query: {query}")
            
            # Instead of using buffer images, directly use Codesignal_Score.png
            images = ["Codesignal_Score.png"]
            
            # Check if the test image exists
            if not os.path.exists(images[0]):
                print(f"WARNING: Test image {images[0]} not found. Please ensure it exists.")
                continue
                
            # Process the query with the test image
            result = process_query(images, query)
            
            # Display the result
            print("\n" + "="*50)
            print("FINAL RESULT:")
            print(result["final_result"])
            print("="*50 + "\n")
            
            # You could add code here to speak the result using text-to-speech
            
        time.sleep(0.5)  # Short delay to prevent CPU thrashing

def main():
    # Create shared resources
    buffer = Buffer(capacity=5)
    command_queue = mp.Queue()

    # Start the camera process (commented out, but kept for process structure)
    camera = mp.Process(target=camera_process, args=(buffer,))
    
    # Start the agent process
    agent = mp.Process(target=agent_process, args=(buffer, command_queue))
    
    # Start speech recognition in a separate thread (optional - can comment out if not using speech)
    # speech_thread = threading.Thread(target=speech_recognition_thread, args=(command_queue,))
    # speech_thread.daemon = True  # Thread will exit when main program exits
    
    camera.start()
    agent.start()
    # speech_thread.start()

    try:
        print("System ready. Type your queries below (or 'quit' to exit):")
        
        # Allow manual text input for testing
        while True:
            text_input = input()
            if text_input.lower() == 'quit':
                break
                
            # Put manual text input into the command queue
            command_queue.put(text_input)
            
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping processes...")
    finally:
        camera.terminate()
        agent.terminate()
        camera.join()
        agent.join()

if __name__ == "__main__":
    main()
