#!/usr/bin/env python3
"""
Create a .keras model file for maximum compatibility with TensorFlow 2.15.0
"""

import os
import sys
import numpy as np

def create_keras_format_model():
    """Create a .keras format model for TensorFlow 2.15.0 compatibility"""
    print("🔧 Creating .keras Format Model for TensorFlow 2.15.0")
    print("=" * 60)
    
    try:
        import tensorflow as tf
        print(f"Using TensorFlow version: {tf.__version__}")
        
        # Load the original model
        model_path = 'models/best_furniture_model.h5'
        print(f"📂 Loading original model: {model_path}")
        
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
            
        model = tf.keras.models.load_model(model_path)
        print("✅ Original model loaded successfully")
        
        print(f"Model info:")
        print(f"  Input shape: {model.input_shape}")
        print(f"  Output shape: {model.output_shape}")
        print(f"  Number of layers: {len(model.layers)}")
        
        # Save in .keras format (Keras 3 native format)
        keras_model_path = 'models/furniture_model.keras'
        print(f"\n💾 Saving in .keras format: {keras_model_path}")
        model.save(keras_model_path)
        print("✅ .keras model saved successfully!")
        
        # Test loading the .keras model
        print("\n🔍 Testing .keras model loading...")
        test_model = tf.keras.models.load_model(keras_model_path)
        print("✅ .keras model loads successfully!")
        
        # Test prediction
        print("\n🧪 Testing prediction...")
        dummy_input = np.random.random((1, 224, 224, 3))
        prediction = test_model.predict(dummy_input, verbose=0)
        print(f"✅ Test prediction successful: shape {prediction.shape}")
        print(f"Sample prediction: {prediction[0]}")
        
        # Get file size
        file_size = os.path.getsize(keras_model_path)
        print(f"\n📊 Model file size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        return keras_model_path
        
    except Exception as e:
        print(f"❌ .keras model creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    keras_model_path = create_keras_format_model()
    
    if keras_model_path:
        print(f"\n🎉 SUCCESS! .keras model created: {keras_model_path}")
        print("\n📋 Next Steps:")
        print("1. Update your code to use the .keras model")
        print("2. Test locally")
        print("3. Commit and deploy to Render")
        print(f"\n💡 Model loading code:")
        print(f"   model = tf.keras.models.load_model('{keras_model_path}')")
        print(f"\n✨ .keras format should be compatible with TensorFlow 2.15.0!")
        return 0
    else:
        print("\n❌ FAILED to create .keras model")
        return 1

if __name__ == "__main__":
    sys.exit(main())
