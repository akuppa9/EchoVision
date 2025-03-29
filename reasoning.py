# access buffer to get base 64 encoded images (state)
# pass into gpt-4o-mini request
# pass user speech prompt as text in request (query)
# fetch long term info from vector store
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def reasoning(images, query, param_for_next_action=""):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create messages array with images and prompt
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": 
                            """You are an AI assistant helping a user navigate and understand their environment. Based on the provided images and user query, determine the next appropriate action to take in the action sequence.

                            Here are the possible actions you can use:

                            1. Get current location
                            - Function: get_current_location()
                            - Returns the current GPS coordinates
                            Use when you need the user's current position for other actions

                            2. Get route to destination
                            - Function: get_route_to_destination(origin, destination)
                            Parameters:
                              - origin: string (GPS coordinates or address)
                              - destination: string (address or place name)
                              - mode: string (defaults to 'walking')
                            Use when the user asks for directions or how to get somewhere specific

                            3. Get nearby places
                            - Function: get_nearby_places(location, type, radius=5000)
                            Parameters:
                              - location: string (GPS coordinates or address)
                              - type: string (place type, e.g., 'restaurant', 'gas_station', 'hospital')
                              - radius: integer (optional, search radius in meters, default 5000)
                            Use when the user asks about finding nearby locations of a specific type

                            For image analysis and understanding the surroundings, I will directly analyze the provided images and give detailed descriptions and contextual information without requiring any additional API calls.

                            - A prompt such as 'explain my surroundings' would require visual analysis of the images, and no API calls would be needed.
                            - A prompt such as 'read me the text on the whiteboard' would require visual analysis of the images, and no API calls would be needed.

                            If this is the start of a new query, determine the full action chain needed and specify the first action to take.
                            If this is a continuation (param_for_next_action is not empty), use that parameter for the next action in the chain.

                            Examples:
                            - For 'give me directions to chipotle', the chain would be:
                              1. get_current_location() -> returns coordinates
                              2. get_nearby_places(coordinates, 'restaurant') -> returns chipotle address, not coordinates
                              3. get_route_to_destination(coordinates, chipotle_address)

                            - For 'what is the closest gas station', the chain would be:
                              1. get_current_location() -> returns coordinates
                              2. get_nearby_places(coordinates, 'gas_station')

                            Provide your response in this format:
                            Action Chain: [List the full sequence of actions needed, or specify if only image analysis is needed]
                            Next Action: [Specify which action to take now and its parameters, or provide image analysis]
                            Parameter to Save: [Specify what parameter from the response needs to be saved for the next action]

                            Current parameter from previous action: """ + param_for_next_action + """
                            User Query: """ + query
                }
            ]
        }
    ]
    for image_path in images:
        base64_image = get_image_base64(image_path)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=messages,
    )
    
    # The full response body contains:
    # - id: The unique identifier for the completion
    # - object: The type of object (chat.completion)
    # - created: Unix timestamp of when the completion was created
    # - model: The model used for the completion
    # - choices: Array of completion choices, each containing:
    #   - index: The index of the choice
    #   - message: The message object containing:
    #     - role: The role of the message (assistant/user)
    #     - content: The content of the message
    #   - finish_reason: The reason why the completion finished
    # - usage: Object containing:
    #   - prompt_tokens: Number of tokens in the prompt
    #   - completion_tokens: Number of tokens in the completion
    #   - total_tokens: Total number of tokens used
    
    return response.choices[0].message.content

# Test with a local image
print(reasoning(["Codesignal_Score.png"], "tell me the nearest walmart store", "coordinates: 40.0061° N, 83.0283° W"))