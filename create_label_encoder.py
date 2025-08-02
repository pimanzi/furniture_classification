#!/usr/bin/env python3
"""
Create a label encoder for the furniture classification model
"""
import pickle
from sklearn.preprocessing import LabelEncoder

# Define the class names exactly as they should be
class_names = ['Almirah', 'Chair', 'Fridge', 'Table', 'TV']

# Create label encoder
label_encoder = LabelEncoder()
label_encoder.fit(class_names)

# Save the label encoder
with open('models/label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)

print("✓ Label encoder created and saved to models/label_encoder.pkl")
print(f"Classes: {list(label_encoder.classes_)}")
print(f"Class mapping:")
for i, class_name in enumerate(label_encoder.classes_):
    print(f"  {i}: {class_name}")
