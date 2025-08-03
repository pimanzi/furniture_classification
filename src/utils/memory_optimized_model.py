"""
Memory-optimized model loading for Render deployment
Reduces memory usage during model loading and inference
"""
import os
import gc
import numpy as np
import pickle

try:
    import tensorflow as tf
    # Configure TensorFlow for memory optimization
    tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True) if tf.config.list_physical_devices('GPU') else None
    # Limit TensorFlow threading to reduce memory overhead
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TensorFlow not available: {e}")
    TENSORFLOW_AVAILABLE = False
except Exception as gpu_error:
    print(f"GPU config warning: {gpu_error}")
    TENSORFLOW_AVAILABLE = True

class MemoryOptimizedPredictor:
    """Memory-optimized predictor for Render deployment"""
    
    def __init__(self, model_path='models/furniture_savedmodel', 
                 label_encoder_path='models/label_encoder.pkl'):
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for predictions but is not available.")
            
        self.model_path = model_path
        self.label_encoder_path = label_encoder_path
        self.model = None
        self.label_encoder = None
        self.class_names = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']
        self.img_size = 224
        self._model_loaded = False
        
    def _optimize_memory(self):
        """Force garbage collection and memory optimization"""
        gc.collect()
        if hasattr(tf, 'keras'):
            try:
                tf.keras.backend.clear_session()
            except:
                pass
    
    def load_model_lazy(self):
        """Lazy load model only when needed to save memory"""
        if self._model_loaded and self.model is not None:
            return True
            
        try:
            print(f"🔄 Loading model from: {self.model_path}")
            
            # Clear any existing model from memory
            if self.model is not None:
                del self.model
                self._optimize_memory()
            
            # Load SavedModel with memory optimization
            if os.path.isdir(self.model_path):
                print("📦 Loading SavedModel format...")
                
                # Use tf.saved_model.load for lower memory footprint
                self.model = tf.saved_model.load(self.model_path)
                print("✅ SavedModel loaded successfully")
                
                # Get inference function
                self.infer_fn = self.model.signatures.get("serving_default")
                if self.infer_fn is None:
                    print("⚠️ No serving_default signature found, using first available")
                    self.infer_fn = list(self.model.signatures.values())[0]
                
                # Get input/output specs for optimization
                self.input_spec = list(self.infer_fn.structured_input_signature[1].values())[0]
                self.input_key = list(self.infer_fn.structured_input_signature[1].keys())[0]
                
                print(f"📋 Input spec: {self.input_spec}")
                
            else:
                raise FileNotFoundError(f"Model path {self.model_path} not found")
            
            # Load label encoder with memory optimization
            self._load_label_encoder()
            
            self._model_loaded = True
            self._optimize_memory()
            
            print("✅ Model loading completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_label_encoder(self):
        """Load label encoder with fallback"""
        try:
            if os.path.exists(self.label_encoder_path):
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print(f"✅ Label encoder loaded")
            else:
                print("⚠️ Label encoder not found, using default classes")
                self.label_encoder = None
        except Exception as e:
            print(f"⚠️ Error loading label encoder: {e}, using default classes")
            self.label_encoder = None
    
    def _preprocess_image(self, image_path):
        """Memory-efficient image preprocessing"""
        try:
            from tensorflow.keras.preprocessing.image import load_img, img_to_array
            
            # Load image with target size to save memory
            img = load_img(image_path, target_size=(self.img_size, self.img_size))
            img_array = img_to_array(img)
            
            # Convert to float32 and normalize in one step
            img_array = np.expand_dims(img_array, axis=0).astype(np.float32) / 255.0
            
            # Clean up intermediate objects
            del img
            
            return img_array
            
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            return None
    
    def predict_image(self, image_path):
        """Memory-optimized prediction"""
        try:
            # Lazy load model
            if not self.load_model_lazy():
                return None
            
            # Preprocess image
            img_array = self._preprocess_image(image_path)
            if img_array is None:
                return None
            
            print(f"🔍 Making prediction for: {os.path.basename(image_path)}")
            
            # Make prediction using SavedModel inference
            prediction_result = self.infer_fn(**{self.input_key: img_array})
            
            # Extract predictions from result
            output_key = list(prediction_result.keys())[0]
            predictions = prediction_result[output_key].numpy()[0]
            
            # Get results
            confidence = float(np.max(predictions))
            predicted_class_idx = int(np.argmax(predictions))
            
            # Get class name
            if self.label_encoder is not None and hasattr(self.label_encoder, 'classes_'):
                if predicted_class_idx < len(self.label_encoder.classes_):
                    predicted_class = str(self.label_encoder.classes_[predicted_class_idx])
                else:
                    predicted_class = self.class_names[predicted_class_idx] if predicted_class_idx < len(self.class_names) else "Unknown"
            else:
                predicted_class = self.class_names[predicted_class_idx] if predicted_class_idx < len(self.class_names) else "Unknown"
            
            # Clean up arrays
            del img_array, prediction_result
            self._optimize_memory()
            
            result = {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'class_index': predicted_class_idx,
                'all_predictions': predictions.tolist(),
                'class_names': self.class_names
            }
            
            print(f"✅ Prediction: {predicted_class} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def health_check(self):
        """Quick health check for the model"""
        try:
            if not self.load_model_lazy():
                return {"status": "error", "message": "Model failed to load"}
            
            # Create dummy input for quick test
            dummy_input = np.random.rand(1, self.img_size, self.img_size, 3).astype(np.float32)
            
            # Test inference
            prediction_result = self.infer_fn(**{self.input_key: dummy_input})
            output_key = list(prediction_result.keys())[0]
            predictions = prediction_result[output_key].numpy()[0]
            
            # Clean up
            del dummy_input, prediction_result
            self._optimize_memory()
            
            return {
                "status": "healthy", 
                "message": "Model loaded and working",
                "output_shape": predictions.shape,
                "classes": self.class_names
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Health check failed: {str(e)}"}
    
    def get_memory_info(self):
        """Get current memory usage info"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "model_loaded": self._model_loaded
            }
        except ImportError:
            return {"message": "psutil not available for memory monitoring"}
        except Exception as e:
            return {"error": str(e)}

# Global predictor instance for memory efficiency
_global_predictor = None

def get_global_predictor():
    """Get or create global predictor instance"""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = MemoryOptimizedPredictor()
    return _global_predictor
