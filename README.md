# skywalking-background-tasks-demo

A demonstration of Apache SkyWalking Python agent integration with FastAPI background tasks.

## Overview

This project demonstrates how to:
- Create a FastAPI application with background tasks
- Integrate SkyWalking Python agent for distributed tracing
- Handle asynchronous background coroutines that don't block the response

## Features

- FastAPI endpoint `/test` that creates a background task
- Background coroutine sleeps for 10 seconds
- Returns "ok" immediately without waiting for the background task
- Full SkyWalking tracing integration

## Prerequisites

- Python 3.8 or higher
- SkyWalking OAP server (optional, for tracing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tsonglew/skywalking-background-tasks-demo.git
cd skywalking-background-tasks-demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running without SkyWalking (for local testing)

```bash
chmod +x run_without_skywalking.sh
./run_without_skywalking.sh
```

Or directly with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Running with SkyWalking agent

1. Make sure SkyWalking OAP server is running (default: `127.0.0.1:11800`)

2. Run the application with the agent:
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
export SW_AGENT_NAME=fastapi-background-tasks-demo
export SW_AGENT_COLLECTOR_BACKEND_SERVICES=127.0.0.1:11800
sw-python run -p main:app uvicorn main:app --host 0.0.0.0 --port 8000
```

## Quick Start with Docker

The easiest way to run the complete demo (including SkyWalking OAP and UI):

```bash
docker-compose up
```

This will start:
- FastAPI application on port 8000
- SkyWalking OAP server on ports 11800 (gRPC) and 12800 (HTTP)
- SkyWalking UI on port 8080

Access the SkyWalking UI at http://localhost:8080 to view traces.

To run just the application:
```bash
docker build -t fastapi-skywalking-demo .
docker run -p 8000:8000 fastapi-skywalking-demo
```

## Testing

### Test the /test endpoint

```bash
# Send a request to create a background task
curl http://localhost:8000/test
```

Expected response: `"ok"` (returns immediately)

The background task will log its execution:
```
INFO:__main__:[task-20240101-120000-123456] Endpoint returning immediately
INFO:__main__:[task-20240101-120000-123456] Background task started at 2024-01-01 12:00:00.123456
INFO:__main__:[task-20240101-120000-123456] Background task completed at 2024-01-01 12:00:10.123456 (duration: 10.0s)
```

### Test the root endpoint

```bash
curl http://localhost:8000/
```

### Run the standalone test script

You can also run the test script to verify the background task logic without starting the server:

```bash
python test_app.py
```

This will demonstrate the async behavior where:
1. A background task is created
2. The main coroutine returns immediately with "ok"
3. The background task continues running for 10 seconds
4. Both operations happen concurrently

## API Endpoints

### `GET /`
Health check endpoint that returns information about available endpoints.

### `GET /test`
Creates a background coroutine that sleeps for 10 seconds and returns "ok" immediately.

## SkyWalking Configuration

The SkyWalking agent can be configured using environment variables:

- `SW_AGENT_NAME`: Service name (default: `fastapi-background-tasks-demo`)
- `SW_AGENT_COLLECTOR_BACKEND_SERVICES`: OAP server address (default: `127.0.0.1:11800`)
- `SW_AGENT_PROTOCOL`: Protocol to use (default: `grpc`)
- `SW_AGENT_LOGGING_LEVEL`: Logging level (default: `INFO`)

## Project Structure

```
.
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── skywalking.ini                 # SkyWalking configuration file
├── run.sh                         # Script to run with SkyWalking
├── run_without_skywalking.sh     # Script to run without SkyWalking
└── README.md                      # This file
```

## Dependencies

- `fastapi`: Modern web framework for building APIs
- `uvicorn`: ASGI server for FastAPI
- `apache-skywalking`: SkyWalking Python agent for distributed tracing

## License

MIT