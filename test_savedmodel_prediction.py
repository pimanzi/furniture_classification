#!/usr/bin/env python3
"""Test SavedModel prediction functionality."""

import os
import sys
import tensorflow as tf
from PIL import Image
import numpy as np

# Add src to path
sys.path.append('src')
from utils.model_utils import FurniturePredictor

def create_test_image():
    """Create a test image for prediction."""
    # Create a 224x224 RGB test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(test_image)
    test_path = "test_image.jpg"
    img.save(test_path)
    return test_path

def main():
    print("🧪 Testing SavedModel Prediction Functionality")
    print("=" * 50)
    
    # Create test image
    test_image_path = create_test_image()
    print(f"📸 Created test image: {test_image_path}")
    
    try:
        # Initialize classifier
        classifier = FurniturePredictor()
        
        # Test prediction
        print("\n🔍 Testing prediction...")
        result = classifier.predict_image(test_image_path)
        
        if result:
            print(f"\n✅ Prediction successful!")
            print(f"Predicted class: {result['predicted_class']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Available classes: {result['class_names']}")
        else:
            print("❌ Prediction failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"🧹 Cleaned up test image")

if __name__ == "__main__":
    main()
