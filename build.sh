#!/bin/bash

# Exit on error
set -e

# Install Python dependencies
pip install -r requirements.txt

# Initialize database and run migrations
python -c "
from app import app, db
from flask_migrate import upgrade

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Run all migrations
    upgrade()
"
