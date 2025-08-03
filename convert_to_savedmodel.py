#!/usr/bin/env python3
"""
Convert model to SavedModel format for maximum TensorFlow compatibility
"""

import os
import sys
import shutil
import numpy as np

def convert_to_savedmodel():
    """Convert H5 model to SavedModel format"""
    print("🔧 Converting Model to SavedModel Format (RECOMMENDED)")
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
        
        # Define SavedModel directory path
        savedmodel_dir = 'models/furniture_savedmodel'
        
        # Remove existing SavedModel directory if it exists
        if os.path.exists(savedmodel_dir):
            print(f"🗑️ Removing existing SavedModel: {savedmodel_dir}")
            shutil.rmtree(savedmodel_dir)
        
        # Save as SavedModel format using model.export() for Keras 3 compatibility
        print(f"\n💾 Saving as SavedModel format: {savedmodel_dir}")
        print("Using model.export() for Keras 3 SavedModel format...")
        model.export(savedmodel_dir)
        print("✅ SavedModel saved successfully!")
        
        # Verify the SavedModel can be loaded as Keras model
        print("\n🔍 Verifying SavedModel loading...")
        test_model = tf.keras.models.load_model(savedmodel_dir)
        print("✅ SavedModel loads successfully as Keras model!")
        
        # Test prediction to ensure it works
        print("\n🧪 Testing prediction...")
        dummy_input = np.random.random((1, 224, 224, 3))
        prediction = test_model.predict(dummy_input, verbose=0)
        print(f"✅ Test prediction successful: shape {prediction.shape}")
        print(f"Sample prediction: {prediction[0]}")
        
        # Check SavedModel directory contents
        print(f"\n📁 SavedModel directory contents:")
        for root, dirs, files in os.walk(savedmodel_dir):
            level = root.replace(savedmodel_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_size = os.path.getsize(os.path.join(root, file))
                print(f"{subindent}{file} ({file_size} bytes)")
        
        return savedmodel_dir
        
    except Exception as e:
        print(f"❌ SavedModel conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    savedmodel_path = convert_to_savedmodel()
    
    if savedmodel_path:
        print(f"\n🎉 SUCCESS! SavedModel created at: {savedmodel_path}")
        print("\n📋 Next Steps:")
        print("1. Update your code to use the SavedModel directory")
        print("2. Test locally with the new SavedModel")
        print("3. Commit and deploy to Render")
        print(f"\n💡 Model loading code:")
        print(f"   model = tf.keras.models.load_model('{savedmodel_path}')")
        print(f"\n✨ SavedModel format using model.export() is fully compatible with TensorFlow 2.15!")
        return 0
    else:
        print("\n❌ FAILED to create SavedModel")
        return 1

if __name__ == "__main__":
    sys.exit(main())
