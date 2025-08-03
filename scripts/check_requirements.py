#!/usr/bin/env python3
"""
Check if all required packages are installed and working
"""
import sys
import importlib

required_packages = [
    'tensorflow',
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'PIL',
    'sklearn',
    'matplotlib',
    'seaborn'
]

def check_package(package_name):
    try:
        importlib.import_module(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    print(" Checking required packages...")
    print("=" * 50)
    
    all_good = True
    
    for package in required_packages:
        is_installed, error = check_package(package)
        status = " Installed" if is_installed else " Missing"
        print(f"{package:15}: {status}")
        
        if not is_installed:
            all_good = False
            print(f"    Error: {error}")
    
    print("=" * 50)
    
    if all_good:
        print(" All packages are installed!")
        print("\n🚀 You can now run the notebooks or the Streamlit app.")
    else:
        print(" Some packages are missing!")
        print("\n Install missing packages with:")
        print("    pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
