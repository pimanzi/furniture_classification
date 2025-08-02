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
    """Initialize SQLite database"""
    try:
        from src.utils.database import FurnitureDB
        db = FurnitureDB()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def check_model_availability():
    """Check if model files exist"""
    model_path = "models/best_furniture_model.h5"
    if os.path.exists(model_path):
        print(f"✓ Model found at: {model_path}")
        return True
    else:
        print(f"⚠ Model not found at: {model_path}")
        return False

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
