#!/bin/bash

# Create necessary directories
mkdir -p database
mkdir -p models

# Initialize database if it doesn't exist
python -c "
import os
if not os.path.exists('database/furniture_classification.db'):
    from src.utils.database import FurnitureDB
    db = FurnitureDB()
    print('Database initialized successfully')
else:
    print('Database already exists')
"

# Start the Streamlit app
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
