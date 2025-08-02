#!/bin/bash

# Render startup script for Furniture Classification App
echo "🚀 Starting Furniture Classification App on Render..."

# Check Python version
python --version

# Check if TensorFlow can be imported
echo "🔍 Checking TensorFlow availability..."
python -c "import tensorflow as tf; print(f'✅ TensorFlow {tf.__version__} loaded successfully')" || {
    echo "❌ TensorFlow import failed"
    exit 1
}

# Check if model files exist
if [ ! -f "models/best_furniture_model.h5" ]; then
    echo "❌ Model file not found!"
    exit 1
fi

echo "✅ All checks passed. Starting Streamlit app..."

# Start the Streamlit app
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
