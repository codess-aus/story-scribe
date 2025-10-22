#!/bin/bash
# Azure App Service startup script for FastAPI

echo "Starting StoryScribe FastAPI backend..."

# Install dependencies if needed
if [ ! -d "/home/site/wwwroot/.venv" ]; then
    echo "Creating virtual environment..."
    python -m venv /home/site/wwwroot/.venv
fi

echo "Activating virtual environment..."
source /home/site/wwwroot/.venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting Gunicorn with Uvicorn workers..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 600
