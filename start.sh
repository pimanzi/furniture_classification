#!/bin/bash

echo "Starting Furniture Classification App Deployment..."

# Run deployment initialization
echo "Running deployment initialization..."
python deploy_init.py

if [ $? -ne 0 ]; then
    echo "Deployment initialization failed!"
    exit 1
fi

echo "Deployment initialization completed successfully!"

# Start the Streamlit app
echo "Starting Streamlit application..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
