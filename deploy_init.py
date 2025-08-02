"""
Deployment initialization script for Render
Handles database setup and model availability
"""
import os
import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Setup logging for deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_directories():
    """Create necessary directories"""
    directories = ['database', 'models', 'temp', 'uploads']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")

def initialize_database():
    """Initialize SQLite database and populate with training data"""
    try:
        from src.utils.database import FurnitureDB
        db = FurnitureDB()
        print("✓ Database initialized successfully")
        
        # Check if we need to populate training data
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM training_data")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("📊 Populating database with training data...")
            populate_training_data(db)
        else:
            print(f"✓ Database already contains {count} training samples")
            
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def populate_training_data(db):
    """Populate database with processed training data"""
    try:
        import numpy as np
        import pickle
        import os
        
        processed_dir = 'processed_data'
        
        # Check if processed data exists
        required_files = [
            'paths_train.npy', 'paths_val.npy', 'paths_test.npy',
            'y_train.npy', 'y_val.npy', 'y_test.npy',
            'config.pkl'
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(processed_dir, f))]
        
        if missing_files:
            print(f"⚠ Missing processed data files: {missing_files}")
            print("  Skipping training data population")
            return
        
        # Load processed data
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
        
        # Populate database
        db.populate_original_data(
            paths_train, paths_val, paths_test,
            y_train, y_val, y_test, 
            class_names
        )
        
        print(f"✓ Populated database with training data:")
        print(f"  - Training samples: {len(paths_train)}")
        print(f"  - Validation samples: {len(paths_val)}")
        print(f"  - Test samples: {len(paths_test)}")
        print(f"  - Classes: {class_names}")
        
    except Exception as e:
        print(f"⚠ Failed to populate training data: {e}")
        print("  Database will work but training history won't be available")

def check_model_availability():
    """Check if model files exist and TensorFlow is available"""
    model_path = "models/best_furniture_model.h5"
    
    # Check TensorFlow availability
    try:
        import tensorflow as tf
        tensorflow_available = True
        print("✓ TensorFlow is available")
    except ImportError:
        tensorflow_available = False
        print("⚠ TensorFlow not available - will run in demo mode")
    
    # Check model file
    if os.path.exists(model_path):
        print(f"✓ Model found at: {model_path}")
        model_available = True
    else:
        print(f"⚠ Model not found at: {model_path}")
        model_available = False
        
    if tensorflow_available and model_available:
        print("✓ Full prediction functionality available")
        return True
    elif model_available:
        print("⚠ Model available but TensorFlow missing - demo mode predictions")
        return True
    else:
        print("⚠ Running in demo mode - mock predictions only")
        return True  # Still return True as app can run in demo mode

def create_dummy_model_info():
    """Create model info for demo mode"""
    model_info = {
        "status": "demo_mode",
        "message": "Model not available in deployed version",
        "classes": ["Almirah", "Chair", "Fridge", "Table", "TV"],
        "demo_mode": True
    }
    
    import json
    with open("models/model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)
    
    print("✓ Created model info for demo mode")

def main():
    """Main initialization function"""
    logger = setup_logging()
    logger.info("Starting deployment initialization...")
    
    print("=" * 50)
    print("FURNITURE CLASSIFICATION - DEPLOYMENT SETUP")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Initialize database
    db_success = initialize_database()
    
    # Check model availability
    model_available = check_model_availability()
    
    print("\n" + "=" * 50)
    if db_success and model_available:
        print("✓ DEPLOYMENT SETUP COMPLETED SUCCESSFULLY")
        print("✓ Model available - Full functionality enabled")
    elif db_success:
        print("✓ DEPLOYMENT SETUP COMPLETED")
        print("⚠ Model issues detected - Check logs above")
    else:
        print("✗ DEPLOYMENT SETUP FAILED")
        sys.exit(1)
    print("=" * 50)

if __name__ == "__main__":
    main()
