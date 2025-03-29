# EchoVision

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
