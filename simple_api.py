#!/usr/bin/env python3
"""
Simple FastAPI server for furniture classification - designed for load testing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.furniture_predictor import FurniturePredictor
from utils.database import FurnitureDB

app = FastAPI(title="Furniture Classification API", version="1.0.0")

# Initialize components
try:
    predictor = FurniturePredictor()
    db = FurnitureDB()
    print(" API components initialized successfully")
except Exception as e:
    print(f" Failed to initialize components: {e}")
    predictor = None
    db = None

@app.get("/")
async def root():
    return {"message": "Furniture Classification API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "predictor_loaded": predictor is not None,
        "database_connected": db is not None
    }

@app.post("/predict")
async def predict_furniture(file: UploadFile = File(...)):
    """Predict furniture type from uploaded image"""
    if not predictor:
        raise HTTPException(status_code=500, detail="Predictor not initialized")
    
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Make prediction
        prediction, confidence = predictor.predict(image)
        
        # Log prediction to database
        if db:
            try:
                db.log_prediction(prediction, confidence, file.filename)
            except Exception as e:
                print(f"Warning: Failed to log prediction to database: {e}")
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "filename": file.filename,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/analytics")  
async def get_analytics():
    """Get prediction analytics"""
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Get analytics data
        analytics = db.get_analytics()
        return {
            "analytics": analytics,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Furniture Classification API...")
    uvicorn.run(app, host="0.0.0.0", port=8517, log_level="info")
