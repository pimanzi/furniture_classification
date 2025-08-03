import numpy as np
import pandas as pd
import os
from datetime import datetime
import pickle

# Import TensorFlow and required modules
try:
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetB0, MobileNetV2
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
    from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
    from tensorflow.keras.utils import to_categorical
    print("✓ TensorFlow loaded successfully")
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TensorFlow not available: {e}")
    TENSORFLOW_AVAILABLE = False

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class FurnitureModelTrainer:
    def __init__(self, img_size=224, batch_size=32, num_classes=5):
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for model training but is not available.")
        
        self.img_size = img_size
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.class_names = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']
        
    def create_model(self, input_shape=(224, 224, 3)):
        """Create model with transfer learning"""
        try:
            print("Attempting to load EfficientNetB0...")
            base_model = EfficientNetB0(
                weights='imagenet',
                include_top=False,
                input_shape=input_shape
            )
            model_name = "EfficientNetB0"
        except Exception as e:
            print(f"EfficientNetB0 loading failed: {str(e)}")
            print("Falling back to MobileNetV2...")
            base_model = MobileNetV2(
                weights='imagenet',
                include_top=False,
                input_shape=input_shape
            )
            model_name = "MobileNetV2"
        
        # Freeze base model initially
        base_model.trainable = False
    
        inputs = base_model.input
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.3)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.4)(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model, base_model, model_name
    
    def prepare_data_from_dataframe(self, df, validation_split=0.2):
        """Prepare training data from DataFrame"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        
        # Print data info for debugging
        print(f"Data shape: {df.shape}")
        print(f"Unique classes: {df['class_name'].unique()}")
        print(f"Class ID range: {df['class_id'].min()} to {df['class_id'].max()}")
        
        # Ensure class IDs are within expected range [0, 4]
        valid_class_ids = set(range(self.num_classes))
        df_filtered = df[df['class_id'].isin(valid_class_ids)].copy()
        
        if len(df_filtered) < len(df):
            print(f"Warning: Filtered out {len(df) - len(df_filtered)} samples with invalid class IDs")
        
       
        df_filtered['class_id_encoded'] = df_filtered['class_id']
        
        # Create a label encoder that maps to our expected class names
        label_encoder = LabelEncoder()
        label_encoder.fit(self.class_names) 
        
        # Check if we have enough samples for stratified split
        class_counts = df_filtered['class_name'].value_counts()
        min_samples_per_class = class_counts.min()
        
        if min_samples_per_class < 2 or len(df_filtered) < 10:
            # If we have too few samples, don't use validation split
            print(f"Warning: Insufficient data for validation split. Using all data for training.")
            print(f"Minimum samples per class: {min_samples_per_class}")
            
            train_df = df_filtered.copy()
            val_df = df_filtered.sample(min(len(df_filtered), 5), random_state=42) 
            
            y_train = to_categorical(train_df['class_id_encoded'], num_classes=self.num_classes)
            y_val = to_categorical(val_df['class_id_encoded'], num_classes=self.num_classes)
        else:
            # Use stratified split only if we have enough samples
            try:
                train_df, val_df = train_test_split(
                    df_filtered, test_size=validation_split, 
                    stratify=df_filtered['class_name'], random_state=42
                )
            except ValueError:
                # Fallback to random split if stratified fails
                print("Stratified split failed, using random split...")
                train_df, val_df = train_test_split(
                    df_filtered, test_size=validation_split, random_state=42
                )
            
            # Convert to one-hot encoding
            y_train = to_categorical(train_df['class_id_encoded'], num_classes=self.num_classes)
            y_val = to_categorical(val_df['class_id_encoded'], num_classes=self.num_classes)
        
        print(f"Final training samples: {len(train_df)}")
        print(f"Final validation samples: {len(val_df)}")
        print(f"Training labels shape: {y_train.shape}")
        print(f"Validation labels shape: {y_val.shape}")
        
        return train_df, val_df, y_train, y_val, label_encoder
    
    def create_data_generator(self, df, labels, augment=False, shuffle=True):
        """Create data generator from DataFrame"""
        if augment:
            datagen = ImageDataGenerator(
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                zoom_range=0.2,
                fill_mode='nearest',
                rescale=1./255
            )
        else:
            datagen = ImageDataGenerator(rescale=1./255)
        
        def data_generator():
            indices = np.arange(len(df))
            while True:
                if shuffle:
                    np.random.shuffle(indices)
                
                for start_idx in range(0, len(indices), self.batch_size):
                    batch_indices = indices[start_idx:start_idx + self.batch_size]
                    batch_paths = df.iloc[batch_indices]['image_path'].values
                    batch_labels = labels[batch_indices]
                    
                    batch_images = []
                    valid_labels = []
                    
                    for i, path in enumerate(batch_paths):
                        try:
                            if os.path.exists(path) and i < len(batch_labels):
                                img = load_img(path, target_size=(self.img_size, self.img_size))
                                img_array = img_to_array(img)
                                
                                if augment:
                                    img_array = datagen.random_transform(img_array)
                                
                                img_array = img_array / 255.0
                                batch_images.append(img_array)
                                valid_labels.append(batch_labels[i])
                        except Exception as e:
                            print(f"Error processing image {path}: {str(e)}")
                            continue
                    
                    if len(batch_images) > 0:
                        yield np.array(batch_images), np.array(valid_labels)
        
        return data_generator
    
    def train_model(self, combined_data, epochs=10, model_save_path='models/retrained_model.h5'):
        """Train model on combined data"""
        print("Preparing data for retraining...")
        
        # Prepare data
        train_df, val_df, y_train, y_val, label_encoder = self.prepare_data_from_dataframe(combined_data)
        
        print(f"Training samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")
        
        # Create generators
        train_generator = self.create_data_generator(train_df, y_train, augment=True, shuffle=True)
        val_generator = self.create_data_generator(val_df, y_val, augment=False, shuffle=False)
        
        # Calculate steps
        steps_per_epoch = len(train_df) // self.batch_size
        validation_steps = len(val_df) // self.batch_size
        
        if steps_per_epoch == 0:
            steps_per_epoch = 1
        if validation_steps == 0:
            validation_steps = 1
        
        # Create model
        model, base_model, model_name = self.create_model()
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                model_save_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=3,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        print("Starting model training...")
        start_time = datetime.now()
        
        # Train model
        history = model.fit(
            train_generator(),
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_data=val_generator(),
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds() / 60  
        
        # Get final accuracy
        final_accuracy = max(history.history['val_accuracy'])
        
        # Save label encoder
        encoder_path = model_save_path.replace('.h5', '_label_encoder.pkl')
        with open(encoder_path, 'wb') as f:
            pickle.dump(label_encoder, f)
        
        return {
            'model': model,
            'history': history,
            'final_accuracy': final_accuracy,
            'training_time': training_time,
            'model_path': model_save_path,
            'label_encoder': label_encoder,
            'original_count': len(combined_data[combined_data['image_path'].str.contains('Furnitures')]),
            'user_count': len(combined_data[~combined_data['image_path'].str.contains('Furnitures')])
        }

class FurniturePredictor:
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
        
    def load_model(self):
        """Load the trained model and label encoder"""
        try:
            if not os.path.exists(self.model_path):
                print(f"Model directory not found at {self.model_path}")
                print("Please train a model first using the Retrain section.")
                return False
                
            print(f"Loading SavedModel from: {self.model_path}")
            
            # For SavedModel format, we need to use tf.saved_model.load for loading
            # but tf.keras.models.load_model for inference in Keras-compatible way
            try:
                # First try loading as Keras model (works if saved with model.export())
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"✓ Model loaded as Keras model from {self.model_path}")
            except Exception as keras_error:
                print(f"Keras loading failed: {str(keras_error)}")
                print("Trying to load as raw SavedModel...")
                # Fallback to raw SavedModel loading
                self.model = tf.saved_model.load(self.model_path)
                print(f"✓ Model loaded as SavedModel from {self.model_path}")
            
            # Try to load label encoder with fallback
            self.label_encoder = None
            if os.path.exists(self.label_encoder_path):
                try:
                    with open(self.label_encoder_path, 'rb') as f:
                        self.label_encoder = pickle.load(f)
                    print(f"✓ Label encoder loaded from {self.label_encoder_path}")
                    print(f"Label encoder classes: {list(self.label_encoder.classes_)}")
                    
                    # Verify the label encoder has the expected classes
                    expected_classes = set(self.class_names)
                    actual_classes = set(str(cls) for cls in self.label_encoder.classes_)
                    
                    if expected_classes != actual_classes:
                        print(f"⚠️ Label encoder class mismatch!")
                        print(f"Expected: {self.class_names}")
                        print(f"Actual: {list(self.label_encoder.classes_)}")
                        print("Creating fallback encoder...")
                        self.label_encoder = self._create_fallback_encoder()
                        
                except Exception as le_error:
                    print(f"⚠️ Error loading label encoder: {str(le_error)}")
                    print("Creating fallback encoder...")
                    self.label_encoder = self._create_fallback_encoder()
            else:
                print(f"Label encoder not found at {self.label_encoder_path}")
                print("Creating fallback encoder...")
                self.label_encoder = self._create_fallback_encoder()
                
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
        return True
    
    def _create_fallback_encoder(self):
        """Create a fallback label encoder with correct class order"""
        from sklearn.preprocessing import LabelEncoder
        import numpy as np
        
        fallback_encoder = LabelEncoder()
        # Manually set the classes in the correct order
        fallback_encoder.classes_ = np.array(self.class_names, dtype=object)
        print(f"✓ Fallback encoder created with classes: {self.class_names}")
        return fallback_encoder
    
    def predict_image(self, image_path):
        """Make prediction on a single image"""
        if self.model is None:
            if not self.load_model():
                print("❌ Failed to load model")
                return None
        
        try:
            # Load and preprocess image
            print(f"📸 Loading image: {image_path}")
            img = load_img(image_path, target_size=(self.img_size, self.img_size))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0
            
            print(f"🔍 Making prediction...")
            
            # Make prediction - handle both Keras models and raw SavedModels
            try:
                # Try Keras model predict() method first
                predictions = self.model.predict(img_array, verbose=0)
            except AttributeError:
                # If it's a raw SavedModel, use the inference function
                print("Using SavedModel inference function...")
                infer = self.model.signatures["serving_default"]
                # Get the input key name
                input_key = list(infer.structured_input_signature[1].keys())[0]
                prediction_result = infer(**{input_key: tf.constant(img_array, dtype=tf.float32)})
                # Get the output
                output_key = list(prediction_result.keys())[0]
                predictions = prediction_result[output_key].numpy()
            
            confidence = np.max(predictions[0])
            predicted_class_idx = np.argmax(predictions[0])
            
            print(f"🎯 Raw prediction index: {predicted_class_idx}")
            print(f"🎯 Confidence: {confidence:.3f}")
            
            # Get class name with robust error handling
            try:
                if self.label_encoder is not None:
                    if hasattr(self.label_encoder, 'classes_') and len(self.label_encoder.classes_) > predicted_class_idx:
                        predicted_class = str(self.label_encoder.classes_[predicted_class_idx])
                        print(f"✓ Using label encoder: {predicted_class}")
                    else:
                        print("⚠️ Label encoder classes_ issue, using default")
                        predicted_class = self.class_names[predicted_class_idx] if predicted_class_idx < len(self.class_names) else "Unknown"
                else:
                    print("⚠️ No label encoder, using default class names")
                    predicted_class = self.class_names[predicted_class_idx] if predicted_class_idx < len(self.class_names) else "Unknown"
            except Exception as class_error:
                print(f"❌ Error getting class name: {str(class_error)}")
                predicted_class = self.class_names[predicted_class_idx] if predicted_class_idx < len(self.class_names) else "Unknown"
            
            result = {
                'predicted_class': predicted_class,
                'confidence': float(confidence),
                'all_predictions': predictions[0].tolist(),
                'class_names': self.class_names
            }
            
            print(f"✅ Prediction successful: {predicted_class} ({confidence:.3f})")
            return result
            
        except Exception as e:
            print(f"❌ Error making prediction: {str(e)}")
            import traceback
            print("Full traceback:")
            traceback.print_exc()
            return None
    
    def predict_batch(self, image_paths):
        """Make predictions on multiple images"""
        results = []
        for image_path in image_paths:
            result = self.predict_image(image_path)
            if result:
                result['image_path'] = image_path
                results.append(result)
        return results
