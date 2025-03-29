# access buffer to get base 64 encoded images (state)
# pass into gpt-4o-mini request
# pass user speech prompt as text in request (query)
# fetch long term info from vector store
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reasoning(images, query, long_term):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create messages array with images and prompt
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": 
                            """You are an AI assistant helping a user navigate and understand their environment. Based on the provided images, user query, and historical successful interactions, determine the most appropriate action sequence to take.

                            Here are the possible actions:
                            1. Get current location + Get route to destination: 
                            Use when the user asks for directions or how to get somewhere specific
                            2. Get current location + Get nearby places: 
                            Use when the user asks about finding nearby locations of a specific type (restaurants, gas stations, etc.)
                            3. Image analysis and description:
                            Use when the user asks about their surroundings or needs information from the visual context

                            Historical successful interactions:
                            """ + long_term + """

                            Analyze the user's query, image context, and historical successful interactions carefully. Use the historical data to inform your action sequence selection and ensure high-quality responses. If the query involves navigation or finding places, specify which API actions should be called and in what order. If the query requires visual analysis, provide a detailed response based on the image content.

                            Provide your response in this format:
                            Action Sequence: [List the specific API calls needed, if any]
                            Reasoning: [Explain why this action sequence was chosen, referencing relevant historical successes if applicable]
                            Response: [The information to relay to the user]

                            User Query: """ + query
                }
            ]
        }
    ]
    
    for image in images:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": image
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
