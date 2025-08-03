#!/usr/bin/env python3
"""
Create a label encoder for the furniture classification model

This script creates a label encoder that matches the expected class names
for the furniture classification model. The label encoder is saved to the
models directory and used by the predictor for consistent class mapping.

Usage:
    python src/utils/create_label_encoder.py
    
Author: Furniture Classification Project
"""
import pickle
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder

def create_label_encoder():
    """Create and save a label encoder for furniture classes"""
    # Define the class names exactly as they should be
    class_names = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']
    
    # Create label encoder and manually set classes to maintain order
    # Note: LabelEncoder.fit() sorts alphabetically, so we set classes_ directly
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(class_names, dtype=object)
    
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    # Save the label encoder
    encoder_path = 'models/label_encoder.pkl'
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    
    print("✓ Label encoder created and saved to models/label_encoder.pkl")
    print(f"Classes: {list(label_encoder.classes_)}")
    print(f"Class mapping:")
    for i, class_name in enumerate(label_encoder.classes_):
        print(f"  {i}: {class_name}")
    
    return encoder_path

if __name__ == "__main__":
    create_label_encoder()
