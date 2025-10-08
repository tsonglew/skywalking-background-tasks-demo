#!/bin/bash

# Run the FastAPI application with SkyWalking agent
# Make sure SkyWalking OAP server is running before starting this application

# Set environment variables for SkyWalking
export SW_AGENT_NAME=fastapi-background-tasks-demo
export SW_AGENT_COLLECTOR_BACKEND_SERVICES=127.0.0.1:11800
export SW_AGENT_PROTOCOL=grpc
export SW_AGENT_LOGGING_LEVEL=INFO

# Start the application with SkyWalking agent
sw-python run -p main:app uvicorn main:app --host 0.0.0.0 --port 8000
