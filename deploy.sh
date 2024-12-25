#!/bin/bash

# Make the script executable
chmod a+x deploy.sh

# Initialize and upgrade the database
python -c "
from app import app, db
from flask_migrate import upgrade

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Run all migrations
    upgrade()
"

# Start the application
gunicorn app:app
