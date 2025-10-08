#!/bin/bash

# Run the FastAPI application WITHOUT SkyWalking agent
# Useful for local development and testing

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
