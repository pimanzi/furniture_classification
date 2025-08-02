# Render Deployment Guide for Furniture Classification App

## 🚀 Quick Deploy to Render

### Prerequisites
- Render account
- GitHub repository with this code
- All model files committed to the repository

### Step 1: Repository Setup
Make sure these files are in your repository:
- ✅ `runtime.txt` (Python 3.11.9)
- ✅ `requirements.txt` (with exact versions)
- ✅ `deploy/start.sh` (startup script)
- ✅ `models/best_furniture_model.h5` (trained model)
- ✅ `models/label_encoder.pkl` (label encoder)

### Step 2: Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `furniture-classification-app`
- **Environment**: `Python`
- **Region**: Choose your preferred region
- **Branch**: `main`

**Build & Deploy:**
- **Root Directory**: Leave empty (uses repository root)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `./deploy/start.sh`

**Advanced Settings:**
- **Python Version**: Will be read from `runtime.txt` (3.11.9)
- **Auto-Deploy**: Yes (recommended)

### Step 3: Environment Variables (Optional)
No additional environment variables are required. The app will use:
- `PORT`: Automatically set by Render
- Default paths for models and database

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for the build to complete (5-10 minutes)
3. Check the logs for any issues
4. Access your app at the provided Render URL

## 📋 Key Files Explanation

### `runtime.txt`
```
python-3.11.9
```
Specifies exact Python version for Render.

### `requirements.txt`
Contains exact package versions compatible with Python 3.11.9 and Render's environment.

### `deploy/start.sh`
- Performs health checks
- Verifies TensorFlow installation
- Checks model files exist
- Starts Streamlit with correct Render configuration

## 🔍 Troubleshooting

### Common Issues:

1. **TensorFlow Import Error**
   - Check if `tensorflow==2.15.0` is in requirements.txt
   - Verify Python version is 3.11.9

2. **Model File Not Found**
   - Ensure model files are committed to git
   - Check file paths in the code

3. **Port Binding Issues**
   - Render automatically sets `$PORT` environment variable
   - Start script uses `--server.port $PORT --server.address 0.0.0.0`

4. **Build Timeout**
   - TensorFlow installation can take time
   - Render has a 15-minute build timeout

### Health Check
Run locally before deploying:
```bash
python3 deploy/health_check.py
```

## 🎯 Expected Behavior

After successful deployment:
- App will be available at `https://your-service-name.onrender.com`
- Database will be created automatically on first run
- Model predictions will work with real TensorFlow (no demo mode)
- All features (prediction, retraining, analytics) will be functional

## 📝 Deployment Checklist

- [ ] Python 3.11.9 specified in `runtime.txt`
- [ ] No `pyproject.toml` or Poetry files in repository
- [ ] Model files committed and accessible
- [ ] requirements.txt has exact versions
- [ ] Start script is executable (`chmod +x deploy/start.sh`)
- [ ] Health check passes locally
- [ ] Repository is connected to Render
- [ ] Build and start commands are configured correctly

## 🔄 Updates and Redeployment

Render will automatically redeploy when you push to the main branch.
For manual redeployment, use the "Manual Deploy" button in Render dashboard.

---

**Ready to deploy!** 🚀
