#!/bin/bash
# ABOUTME: Quick start script for the MediaMTX control plane
# ABOUTME: Ensures DATABASE_URL is unset and starts the Flask development server

# Unset DATABASE_URL to use the config.py default
unset DATABASE_URL

# Activate virtual environment
source venv/bin/activate

# Run the Flask app
python app.py
