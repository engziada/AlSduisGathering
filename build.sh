#!/bin/bash

# Exit on error
set -e

# Install Python dependencies
pip install -r requirements.txt

# Initialize database and run migrations
python update_db.py

# Make deploy script executable
chmod +x deploy.sh
