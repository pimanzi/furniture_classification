# Populate database with existing training data
import sys
import os
import numpy as np
import pickle
sys.path.append('..')
from src.utils.database import FurnitureDB

def populate_database():
    """Populate database with existing training data"""
    
    # Load processed data
    processed_dir = '../processed_data'
    
    if not os.path.exists(processed_dir):
        print("Processed data directory not found!")
        print("Please run the data processing notebook first.")
        return
    
    try:
        # Load saved data
        paths_train = np.load(os.path.join(processed_dir, 'paths_train.npy'))
        paths_val = np.load(os.path.join(processed_dir, 'paths_val.npy'))
        paths_test = np.load(os.path.join(processed_dir, 'paths_test.npy'))
        y_train = np.load(os.path.join(processed_dir, 'y_train.npy'))
        y_val = np.load(os.path.join(processed_dir, 'y_val.npy'))
        y_test = np.load(os.path.join(processed_dir, 'y_test.npy'))

        # Load configuration
        with open(os.path.join(processed_dir, 'config.pkl'), 'rb') as f:
            config = pickle.load(f)

        class_names = config['classes']
        
        print("Loaded training data successfully!")
        print(f"Training samples: {len(paths_train)}")
        print(f"Validation samples: {len(paths_val)}")
        print(f"Test samples: {len(paths_test)}")
        print(f"Classes: {class_names}")
        
        # Initialize database
        db = FurnitureDB()
        
        # Populate with original data
        db.populate_original_data(
            paths_train, paths_val, paths_test,
            y_train, y_val, y_test, class_names
        )
        
        print("Database populated successfully!")
        
        # Print some statistics
        stats = db.get_training_data_stats()
        print("\nOriginal data distribution:")
        print(stats['original_data'])
        
    except Exception as e:
        print(f"Error populating database: {str(e)}")
        print("Make sure you have run the processing notebook first.")

if __name__ == "__main__":
    populate_database()
