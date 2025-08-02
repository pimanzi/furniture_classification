"""
Health check endpoint for deployment
"""
import streamlit as st
import os
import sys
from datetime import datetime

def health_check():
    """Simple health check function"""
    try:
        # Check if required directories exist
        required_dirs = ['src', 'database', 'models']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        health_info = {
            "status": "healthy" if not missing_dirs else "warning",
            "timestamp": datetime.now().isoformat(),
            "python_version": python_version,
            "missing_directories": missing_dirs,
            "streamlit_version": st.__version__
        }
        
        return health_info
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    print("Health check:", health_check())
