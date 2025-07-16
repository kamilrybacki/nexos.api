# Mock nexos.ai API

This project provides a mock implementation of the `nexos.ai` API, designed for testing and development purposes. It allows developers to simulate interactions with the `nexos.ai` API without requiring access to the actual production environment. This mock API replicates the behavior of various endpoints, enabling seamless integration testing and debugging.

## Features

- **Endpoint Simulation**: Implements multiple `nexos.ai` API endpoints, including chat completions, embeddings, audio processing, image generation, and more.
- **Customizable Responses**: Predefined request-response pairs are stored in `data.json`, allowing easy modification of mock responses.
- **Authentication**: Simulates API key-based authentication using the `Authorization` header.
- **Dynamic Route Setup**: Automatically configures routes based on the contents of `data.json`.
- **FastAPI Framework**: Built using FastAPI, providing high performance and easy extensibility.
- **Hot Reloading**: Supports live reloading during development when changes are made to `main.py` or `data.json`.

## Use Cases

- **Integration Testing**: Test your application’s integration with the `nexos.ai` API without relying on external services.
- **Development Environment**: Develop and debug features that interact with the API in a controlled, local environment.
- **Simulating Edge Cases**: Modify `data.json` to simulate various scenarios, such as errors or unusual responses.

## Project Structure

- `main.py`: Contains the FastAPI application and logic for dynamically setting up routes.
- `data.json`: Defines the mock API endpoints, requests, and responses.
- `Dockerfile`: Builds a containerized version of the mock API.
- `docker-compose.yaml`: Simplifies running the mock API with Docker, including environment variable configuration.
- `README.md`: Documentation for the mock API.

## Getting Started

### Prerequisites

- Python 3.10 or later
- Docker (optional, for containerized deployment)

### Running Locally

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Start the API:
   ```bash
   uvicorn main:mock_nexos --host 0.0.0.0 --port 5000 --reload
   ```

3. Access the API at `http://localhost:5000`.

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t mock-nexos-api .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 -e MOCK_NEXOS__API_KEY=let-me-in mock-nexos-api
   ```

3. Access the API at `http://localhost:5000`.

### Using Docker Compose

1. Start the service:
   ```bash
   docker-compose up
   ```

2. Access the API at `http://localhost:5000`.

## Configuration

- **Environment Variables**:
  - `MOCK_NEXOS__API_KEY`: Sets the expected API key for authentication.

- **Customizing Responses**:
  Modify `data.json` to add or update endpoints, requests, and responses.

## Example Endpoints

- `POST /v1/chat/completions`: Simulates chat completions.
- `POST /v1/embeddings`: Returns mock embeddings.
- `POST /v1/audio/transcriptions`: Simulates audio transcription responses.
- `GET /v1/models`: Lists available models.

## License

This project is intended for internal testing and development purposes only. It is not affiliated with or endorsed by `nexos.ai`.
