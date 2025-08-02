#!/usr/bin/env python3
"""
Health check script for Render deployment
Verifies that all required components are available
"""

import sys
import os

def check_tensorflow():
    """Check if TensorFlow is available and working"""
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__} is available")
        return True
    except ImportError as e:
        print(f"❌ TensorFlow not available: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    model_path = "models/best_furniture_model.h5"
    encoder_path = "models/label_encoder.pkl"
    
    if os.path.exists(model_path):
        print(f"✅ Model file found: {model_path}")
        model_ok = True
    else:
        print(f"❌ Model file missing: {model_path}")
        model_ok = False
    
    if os.path.exists(encoder_path):
        print(f"✅ Label encoder found: {encoder_path}")
        encoder_ok = True
    else:
        print(f"⚠️ Label encoder missing: {encoder_path} (will use default)")
        encoder_ok = True  # Not critical
    
    return model_ok and encoder_ok

def check_dependencies():
    """Check if all required packages are available"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'pillow', 
        'matplotlib', 'seaborn', 'plotly', 'sklearn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing.append(package)
    
    return len(missing) == 0

def main():
    print("🔍 Running health check for Furniture Classification App...")
    print("=" * 60)
    
    # Check all components
    tf_ok = check_tensorflow()
    model_ok = check_model_files()
    deps_ok = check_dependencies()
    
    print("=" * 60)
    
    if tf_ok and model_ok and deps_ok:
        print("✅ All health checks passed! App is ready to deploy.")
        sys.exit(0)
    else:
        print("❌ Some health checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
