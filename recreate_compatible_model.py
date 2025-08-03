#!/usr/bin/env python3
"""
Recreate model architecture and transfer weights to ensure TensorFlow 2.15.0 compatibility
"""

import os
import sys
import numpy as np
import pickle

def recreate_compatible_model():
    """Recreate the model architecture from scratch for compatibility"""
    print("🔧 Recreating Model Architecture for TensorFlow 2.15.0 Compatibility")
    print("=" * 70)
    
    try:
        import tensorflow as tf
        print(f"Using TensorFlow version: {tf.__version__}")
        
        # Load the original model to get weights and architecture info
        print("📂 Loading original model to extract weights...")
        original_model = tf.keras.models.load_model('models/best_furniture_model.h5')
        print("✅ Original model loaded successfully")
        
        print(f"Original model info:")
        print(f"  Input shape: {original_model.input_shape}")
        print(f"  Output shape: {original_model.output_shape}")
        print(f"  Number of layers: {len(original_model.layers)}")
        
        # Recreate the model architecture manually
        print("\n🏗️ Recreating model architecture from scratch...")
        
        # Create input layer with explicit shape (avoid batch_shape parameter)
        inputs = tf.keras.Input(shape=(224, 224, 3), name='input_layer')
        
        # Try to identify the base model type from the original
        base_model_layer = None
        for layer in original_model.layers:
            if 'efficientnet' in layer.name.lower():
                print("🔍 Detected EfficientNetB0 base model")
                try:
                    from tensorflow.keras.applications import EfficientNetB0
                    base_model = EfficientNetB0(
                        weights='imagenet',
                        include_top=False,
                        input_tensor=inputs
                    )
                    base_model_name = "EfficientNetB0"
                    break
                except Exception as e:
                    print(f"⚠️ EfficientNetB0 failed: {e}")
                    base_model = None
            elif 'mobilenet' in layer.name.lower():
                print("🔍 Detected MobileNetV2 base model")
                from tensorflow.keras.applications import MobileNetV2
                base_model = MobileNetV2(
                    weights='imagenet',
                    include_top=False,
                    input_tensor=inputs
                )
                base_model_name = "MobileNetV2"
                break
        
        if 'base_model' not in locals() or base_model is None:
            print("🔍 Using EfficientNetB0 as default")
            try:
                from tensorflow.keras.applications import EfficientNetB0
                base_model = EfficientNetB0(
                    weights='imagenet',
                    include_top=False,
                    input_tensor=inputs
                )
                base_model_name = "EfficientNetB0"
            except Exception as e:
                print(f"⚠️ EfficientNetB0 failed, using MobileNetV2: {e}")
                from tensorflow.keras.applications import MobileNetV2
                base_model = MobileNetV2(
                    weights='imagenet',
                    include_top=False,
                    input_tensor=inputs
                )
                base_model_name = "MobileNetV2"
        
        # Freeze base model
        base_model.trainable = False
        
        # Add custom top layers (recreate the classifier)
        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D(name='global_avg_pool')(x)
        x = tf.keras.layers.Dropout(0.3, name='dropout_1')(x)
        x = tf.keras.layers.Dense(256, activation='relu', name='dense_1')(x)
        x = tf.keras.layers.Dropout(0.4, name='dropout_2')(x)
        outputs = tf.keras.layers.Dense(5, activation='softmax', name='predictions')(x)
        
        # Create the new model
        new_model = tf.keras.Model(inputs, outputs, name='furniture_classifier_compatible')
        
        print(f"✅ New model architecture created using {base_model_name}")
        print(f"New model info:")
        print(f"  Input shape: {new_model.input_shape}")
        print(f"  Output shape: {new_model.output_shape}")
        print(f"  Number of layers: {len(new_model.layers)}")
        
        # Try to transfer weights from the original model
        print("\n🔄 Attempting to transfer weights...")
        transferred_layers = 0
        
        for i, layer in enumerate(new_model.layers):
            if i < len(original_model.layers):
                try:
                    original_weights = original_model.layers[i].get_weights()
                    if len(original_weights) > 0:
                        layer.set_weights(original_weights)
                        transferred_layers += 1
                except Exception as e:
                    print(f"⚠️ Could not transfer weights for layer {layer.name}: {e}")
        
        print(f"✅ Transferred weights for {transferred_layers} layers")
        
        # Compile the model
        print("\n⚙️ Compiling model...")
        new_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Save the compatible model
        compatible_path = 'models/best_furniture_model_tf215_compatible.h5'
        print(f"\n💾 Saving compatible model to: {compatible_path}")
        
        # Use older save format for maximum compatibility
        new_model.save(compatible_path, save_format='h5', include_optimizer=False)
        print("✅ Compatible model saved successfully")
        
        # Test the compatible model
        print("\n🔍 Testing compatible model...")
        test_model = tf.keras.models.load_model(compatible_path)
        print("✅ Compatible model loads successfully!")
        
        # Test prediction
        dummy_input = np.random.random((1, 224, 224, 3))
        prediction = test_model.predict(dummy_input, verbose=0)
        print(f"✅ Test prediction works: shape {prediction.shape}")
        print(f"Sample prediction: {prediction[0]}")
        
        return compatible_path
        
    except Exception as e:
        print(f"❌ Model recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    # Check if original model exists
    if not os.path.exists('models/best_furniture_model.h5'):
        print("❌ Original model not found: models/best_furniture_model.h5")
        return 1
    
    # Recreate compatible model
    compatible_path = recreate_compatible_model()
    
    if compatible_path:
        print(f"\n🎉 SUCCESS! Compatible model created: {compatible_path}")
        print("\nNext steps:")
        print("1. Update your code to use the new compatible model")
        print("2. Test locally")
        print("3. Commit and deploy to Render")
        print(f"\nRecommended model path: {compatible_path}")
        return 0
    else:
        print("\n❌ FAILED to create compatible model")
        return 1

if __name__ == "__main__":
    sys.exit(main())
