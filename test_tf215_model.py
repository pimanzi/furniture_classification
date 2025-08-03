#!/usr/bin/env python3
"""
Test the TF 2.15 compatible model
"""

import os
import sys
import numpy as np
from PIL import Image
import tempfile

def test_tf215_compatible_model():
    """Test the TF 2.15 compatible model"""
    print("🧪 Testing TF 2.15 Compatible Model")
    print("=" * 50)
    
    try:
        from src.utils.model_utils import FurniturePredictor
        
        # Create test image
        print("📸 Creating test image...")
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        test_image_path = "test_image_tf215.jpg"
        img.save(test_image_path)
        print(f"✅ Test image created: {test_image_path}")
        
        # Initialize predictor (should use new model path)
        print("\n🤖 Initializing predictor with TF 2.15 compatible model...")
        predictor = FurniturePredictor()
        print(f"Model path: {predictor.model_path}")
        
        # Load model
        print("🧠 Loading model...")
        success = predictor.load_model()
        if not success:
            print("❌ Failed to load model")
            return False
        
        print("✅ Model loaded successfully")
        
        # Make prediction
        print("\n🔍 Making prediction...")
        result = predictor.predict_image(test_image_path)
        
        if result:
            print("✅ Prediction successful!")
            print(f"  Predicted class: {result['predicted_class']}")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  All class probabilities:")
            for i, (class_name, prob) in enumerate(zip(result['class_names'], result['all_predictions'])):
                print(f"    {class_name}: {prob:.3f}")
        else:
            print("❌ Prediction failed")
            return False
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tf215_compatible_model()
    if success:
        print("\n🎉 TF 2.15 COMPATIBLE MODEL TEST PASSED!")
        print("The model is ready for Render deployment.")
    else:
        print("\n❌ TF 2.15 COMPATIBLE MODEL TEST FAILED!")
    
    sys.exit(0 if success else 1)
