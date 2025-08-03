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
echo "📁 Checking model files..."
if [ ! -d "models/furniture_savedmodel" ]; then
    echo "❌ SavedModel directory not found!"
    ls -la models/ || echo "Models directory not found"
    exit 1
fi

# Check SavedModel directory contents
echo "✅ SavedModel directory found"
ls -la models/furniture_savedmodel/ || echo "Could not list SavedModel contents"

# Check if label encoder exists (after our fix)
if [ ! -f "models/label_encoder.pkl" ]; then
    echo "❌ Label encoder not found!"
    ls -la models/ || echo "Models directory listing failed"
    exit 1
fi

echo "✅ Label encoder found"

# Test model loading with Python
echo "🧠 Testing model loading..."
python -c "
import os
import sys
print('Current working directory:', os.getcwd())
print('Models directory contents:')
try:
    import os
    for f in os.listdir('models/'):
        if os.path.isdir(f'models/{f}'):
            print(f'  {f}/ (directory)')
        else:
            size = os.path.getsize(f'models/{f}')
            print(f'  {f}: {size} bytes')
except Exception as e:
    print(f'Error listing models: {e}')

print('Testing TensorFlow availability...')
try:
    import tensorflow as tf
    print(f'✅ TensorFlow {tf.__version__} available')
except Exception as e:
    print(f'❌ TensorFlow import failed: {e}')
    sys.exit(1)

print('Testing label encoder...')
try:
    import pickle
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    print(f'✅ Label encoder loaded: {list(label_encoder.classes_)}')
except Exception as e:
    print(f'❌ Label encoder loading failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('Testing memory-optimized predictor with SavedModel...')
try:
    from src.utils.memory_optimized_model import get_global_predictor
    predictor = get_global_predictor()
    health = predictor.health_check()
    if health['status'] == 'healthy':
        print('✅ Memory-optimized predictor works with SavedModel!')
        print(f'Model output shape: {health.get("output_shape", "Unknown")}')
    else:
        print(f'❌ Memory-optimized predictor health check failed: {health["message"]}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Memory-optimized predictor import/init failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('🎉 All SavedModel tests passed!')
" || {
    echo "❌ Model loading test failed!"
    exit 1
}

echo "✅ All checks passed. Starting Streamlit app..."

# Start the Streamlit app with Render's PORT environment variable
exec streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
