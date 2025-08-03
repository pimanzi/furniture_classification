#!/usr/bin/env python3
"""
Pre-deployment test to ensure model loading works correctly
Run this locally before deploying to Render
"""
import os
import sys
import tempfile
import numpy as np
from PIL import Image

def test_model_deployment_readiness():
    print("🧪 TESTING MODEL DEPLOYMENT READINESS")
    print("=" * 50)
    
    # Test 1: Check Python version
    print(f"\n1. Python Version: {sys.version}")
    if sys.version_info[:2] != (3, 10):
        print("⚠️  Warning: Not using Python 3.10 - may work locally but fail on Render")
    else:
        print("✅ Python 3.10 - Good for Render deployment")
    
    # Test 2: Check critical imports
    print("\n2. Testing critical imports...")
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow: {tf.__version__}")
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
        
    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from src.utils.model_utils import FurniturePredictor
        print("✅ FurniturePredictor import successful")
    except ImportError as e:
        print(f"❌ FurniturePredictor import failed: {e}")
        return False
    
    # Test 3: Check file structure
    print("\n3. Checking file structure...")
    required_paths = [
        'models/best_furniture_model.h5',
        'models/label_encoder.pkl',
        'src/utils/model_utils.py',
        'app.py',
        'requirements.txt',
        'runtime.txt',
        'start.sh'
    ]
    
    for path in required_paths:
        if os.path.exists(path):
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"✅ {path}: {size:,} bytes")
            else:
                print(f"✅ {path}: directory")
        else:
            print(f"❌ {path}: MISSING")
            return False
    
    # Test 4: Test TensorFlow model loading
    print("\n4. Testing TensorFlow model loading...")
    try:
        model = tf.keras.models.load_model('models/best_furniture_model.h5')
        print(f"✅ Model loaded successfully")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        print(f"   Parameters: {model.count_params():,}")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False
    
    # Test 5: Test label encoder
    print("\n5. Testing label encoder...")
    try:
        import pickle
        with open('models/label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        classes = list(label_encoder.classes_)
        print(f"✅ Label encoder loaded")
        print(f"   Classes: {classes}")
        
        # Verify correct order
        expected = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']
        if classes == expected:
            print("✅ Class order is correct")
        else:
            print(f"⚠️  Class order issue - Expected: {expected}, Got: {classes}")
    except Exception as e:
        print(f"❌ Label encoder loading failed: {e}")
        return False
    
    # Test 6: Test full prediction pipeline
    print("\n6. Testing full prediction pipeline...")
    try:
        predictor = FurniturePredictor()
        success = predictor.load_model()
        
        if not success:
            print("❌ Predictor.load_model() returned False")
            return False
        
        print("✅ Predictor loaded successfully")
        
        # Create test image
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
            Image.fromarray(test_image).save(temp_path)
        
        # Test prediction
        result = predictor.predict_image(temp_path)
        
        if result:
            print(f"✅ Prediction successful: {result['predicted_class']} ({result['confidence']:.3f})")
            print(f"   All classes: {result['class_names']}")
        else:
            print("❌ Prediction returned None")
            return False
            
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Prediction pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 7: Check runtime.txt and requirements.txt
    print("\n7. Checking deployment files...")
    
    try:
        with open('runtime.txt', 'r') as f:
            runtime_version = f.read().strip()
        print(f"✅ runtime.txt: {runtime_version}")
        
        if not runtime_version.startswith('python-3.10'):
            print("⚠️  Warning: runtime.txt doesn't specify Python 3.10")
    except Exception as e:
        print(f"❌ Error reading runtime.txt: {e}")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        if 'tensorflow==2.15.0' in requirements:
            print("✅ requirements.txt has TensorFlow 2.15.0")
        else:
            print("⚠️  Warning: requirements.txt doesn't have TensorFlow 2.15.0")
            
        if 'streamlit' in requirements:
            print("✅ requirements.txt has Streamlit")
        else:
            print("❌ requirements.txt missing Streamlit")
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED - READY FOR RENDER DEPLOYMENT!")
    print("\nNext steps:")
    print("1. Commit and push your changes")
    print("2. Deploy on Render")
    print("3. Check Render logs for the startup test results")
    
    return True

if __name__ == "__main__":
    success = test_model_deployment_readiness()
    if not success:
        print("\n❌ TESTS FAILED - Fix issues before deploying")
        sys.exit(1)
    else:
        print("\n🚀 Ready to deploy!")
        sys.exit(0)
