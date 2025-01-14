#!/bin/bash

# Exit on error
set -e

# Install Python dependencies
pip install -r requirements.txt

# Make deploy script executable
chmod +x deploy.sh
