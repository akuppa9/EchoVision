# access buffer to get base 64 encoded images (state)
# pass into gpt-4o-mini request
# pass user speech prompt as text in request (query)
# fetch long term info from vector store
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reasoning(state, query, long_term):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create messages array with images and prompt
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "query",
                }
            ]
        }
    ]
    
    # Add images to the content array
    images = state['images']
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
