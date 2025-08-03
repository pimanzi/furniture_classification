#!/bin/bash

# Railway startup script for Furniture Classification App
echo "Starting Furniture Classification App on Railway..."

# Check Python version
echo "Python version:"
python --version

# Check if TensorFlow can be imported
echo "Checking TensorFlow availability..."
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} loaded successfully')" || {
    echo "TensorFlow import failed"
    exit 1
}

# Check if model files exist
echo "Checking model files..."
if [ ! -f "models/best_furniture_model.h5" ]; then
    echo "H5 model file not found!"
    ls -la models/ || echo "Models directory not found"
    exit 1
fi

echo "H5 model file found"

# Check if label encoder exists
if [ ! -f "models/label_encoder.pkl" ]; then
    echo "Label encoder not found!"
    ls -la models/ || echo "Models directory listing failed"
    exit 1
fi

echo "Label encoder found"

# Test model loading
echo "Testing model loading..."
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
    print(f'TensorFlow {tf.__version__} available')
except Exception as e:
    print(f'TensorFlow import failed: {e}')
    sys.exit(1)

print('Testing label encoder...')
try:
    import pickle
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    print(f'Label encoder loaded: {list(label_encoder.classes_)}')
except Exception as e:
    print(f'Label encoder loading failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('Testing FurniturePredictor...')
try:
    from src.utils.model_utils import FurniturePredictor
    predictor = FurniturePredictor()
    success = predictor.load_model()
    if success:
        print('FurniturePredictor works!')
    else:
        print('FurniturePredictor failed to load model')
        sys.exit(1)
except Exception as e:
    print(f'FurniturePredictor import/init failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('All tests passed!')
" || {
    echo "Model loading test failed!"
    exit 1
}

echo "All checks passed. Starting Streamlit app..."

# Start the Streamlit app
exec streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
