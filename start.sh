#!/bin/bash

# Render startup script for Furniture Classification App
echo "🚀 Starting Furniture Classification App on Render..."

# Check Python version
echo "🐍 Python version:"
python --version

# Verify we're using Python 3.10
python -c "import sys; print(f'Python version: {sys.version}'); assert sys.version_info[:2] == (3, 10), 'Must use Python 3.10 for TensorFlow compatibility'"

# Check if TensorFlow can be imported
echo "🔍 Checking TensorFlow availability..."
python -c "import tensorflow as tf; print(f'✅ TensorFlow {tf.__version__} loaded successfully')" || {
    echo "❌ TensorFlow import failed"
    echo "This is likely due to Python version incompatibility. Ensure Python 3.10 is being used."
    exit 1
}

# Check if model files exist
if [ ! -f "models/best_furniture_model.h5" ]; then
    echo "❌ Model file not found!"
    exit 1
fi

# Check if label encoder exists (after our fix)
if [ ! -f "models/label_encoder.pkl" ]; then
    echo "❌ Label encoder not found!"
    exit 1
fi

echo "✅ All checks passed. Starting Streamlit app..."

# Start the Streamlit app with Render's PORT environment variable
exec streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
