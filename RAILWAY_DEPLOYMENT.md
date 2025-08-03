# Railway Deployment Guide for Furniture Classification App

## Overview
This app is now configured to deploy on Railway.app with the original H5 model format, which should avoid the memory issues experienced on Render.

## Deployment Steps

### 1. Push to GitHub
Make sure all changes are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. Deploy on Railway
1. Go to [Railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `furniture_classification` repository
6. Railway will automatically detect the Python app and deploy it

### 3. Configuration Files
The following files are configured for Railway:

- **`railway.toml`** - Railway-specific configuration
- **`Procfile`** - Process definition for web service
- **`railway_start.sh`** - Startup script with health checks
- **`requirements.txt`** - Python dependencies (already optimized)

### 4. Environment Variables
Railway will automatically set:
- `PORT` - The port your app should listen on
- `PYTHONPATH` - Set to `/app` for proper imports

### 5. Expected Results
✅ **Memory Usage**: Should be much lower with H5 model vs SavedModel  
✅ **Startup Time**: Faster startup without SavedModel conversion  
✅ **Model Loading**: Direct H5 loading with TensorFlow 2.15.0  
✅ **UI Functionality**: All original features restored  

## Key Differences from Render

1. **Model Format**: Back to H5 (.h5) instead of SavedModel
2. **Memory Optimization**: Removed complex memory optimizations that caused issues
3. **Startup Process**: Simplified startup with direct model loading
4. **Health Checks**: Tests H5 model loading instead of SavedModel

## Troubleshooting

If deployment fails:
1. Check Railway logs for specific error messages
2. Verify all model files are committed to repository
3. Ensure Python 3.10 compatibility
4. Check that TensorFlow 2.15.0 is compatible with Railway's environment

## Model Files Required
- `models/best_furniture_model.h5` (13.5MB)
- `models/label_encoder.pkl` (283 bytes)

Total model size: ~13.5MB (much smaller than SavedModel format)
