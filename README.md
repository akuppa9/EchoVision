# EchoVision: Vision-Based AI Assistant with Action Chaining

This system combines computer vision, speech recognition, and OpenAI's vision models to create an AI assistant that can see, understand, and take actions based on user queries.

## Overview

EchoVision uses a chain-of-thought reasoning approach with action chaining to perform complex tasks. The system:

1. Captures images from a camera
2. Listens for user queries (voice or text)
3. Performs reasoning to determine necessary actions
4. Executes actions in sequence (API calls)
5. Provides final responses

## System Components

- **Camera Process**: Captures frames from a camera stream and stores them in a buffer
- **Buffer**: Holds recent frames in memory for processing
- **Agent Process**: Handles user queries, processes images, and manages the action chain
- **Reasoning Module**: Uses OpenAI's vision model to determine what actions to take
- **API Functions**: Simulated functions for location, navigation, and nearby place searches

## Action Chain Workflow

The system implements a multi-step reasoning and action process:

1. User provides a query (e.g., "give me directions to the nearest chipotle")
2. Vision model analyzes images and determines necessary action sequence
3. First action is executed (e.g., get current location)
4. Result from first action is fed back to the vision model
5. Vision model determines next action using previous result
6. Process continues until final result is achieved
7. Final response is presented to the user

## Functions

The system supports several action types:

- `get_current_location()`: Returns current GPS coordinates
- `get_nearby_places(location, type, radius)`: Finds places of interest near a location
- `get_route_to_destination(origin, destination, mode)`: Gets directions between two points
- Image analysis: Directly analyzes visual content without API calls

## Usage

1. Install required packages:

   ```
   pip install openai python-dotenv opencv-python SpeechRecognition
   ```

2. Create a `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application:

   ```
   python main.py
   ```

4. Speak or type commands. For example:
   - "Give me directions to the nearest restaurant"
   - "What does the sign say?"
   - "Find the closest gas station"

## Configuration

You can adjust several parameters in the code:

- Camera URL in `camera_process()`
- Buffer size in `main()`
- Vision model parameters in `reasoning.py`

## Docker Setup

This project is containerized using Docker. To run the application using Docker:

### Prerequisites

- Docker
- Docker Compose
- Python 3.11 (for local development)

### Development

To run the application in development mode:

```bash
docker-compose up
```

### Production

To build and run the application in production mode:

```bash
docker-compose -f docker-compose.yml up --build
```

### Stopping the Application

To stop the application:

```bash
docker-compose down
```

## Development

The application runs on port 8000 by default. You can access it at `http://localhost:8000`.

## Building the Docker Image

To build the Docker image manually:

```bash
docker build -t echovision .
```

## Running the Container

To run the container manually:

```bash
docker run -p 8000:8000 echovision
```

## Local Development Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application locally:

```bash
python app.py
```
