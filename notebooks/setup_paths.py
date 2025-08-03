# Path setup for notebooks
import sys
import os

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Define paths relative to notebooks directory
PATHS = {
    'root': parent_dir,
    'furnitures': os.path.join(parent_dir, 'Furnitures'),
    'processed_data': os.path.join(parent_dir, 'processed_data'),
    'models': os.path.join(parent_dir, 'models'),
    'database': os.path.join(parent_dir, 'database'),
    'db_file': os.path.join(parent_dir, 'database', 'furniture_classification.db')
}

# Print paths for verification
def print_paths():
    print("Project paths:")
    for name, path in PATHS.items():
        exists = "" if os.path.exists(path) else "✗"
        print(f"  {name:15}: {exists} {path}")

if __name__ == "__main__":
    print_paths()
