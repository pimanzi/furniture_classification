# Render Deployment Guide

## Overview
This guide will help you deploy the Furniture Classification app on Render with proper Python 3.10 configuration to ensure TensorFlow compatibility.

## Prerequisites
- GitHub repository with your code
- Render account (free tier works)

## Deployment Steps

### 1. Prepare Your Repository
Make sure these files are in your repository:
- ✅ `runtime.txt` - Specifies Python 3.10.12
- ✅ `pyproject.toml` - Project configuration with Python 3.10 requirement
- ✅ `requirements.txt` - Pinned dependencies for Python 3.10
- ✅ `start.sh` - Startup script with validation
- ✅ `.python-version` - Version file for consistency

### 2. Create Web Service on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:

   **Basic Settings:**
   - **Name**: `furniture-classification` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh`

   **Advanced Settings:**
   - **Python Version**: Will be set by `runtime.txt` (3.10.12)
   - **Auto-Deploy**: `Yes` (deploys on git push)

### 3. Environment Variables
No additional environment variables needed. The app will automatically:
- Use Render's `$PORT` environment variable
- Configure Streamlit for headless operation
- Set proper CORS settings

### 4. Expected Build Process
```
📦 Build Log:
✅ Detected Python 3.10.12 from runtime.txt
✅ Installing dependencies from requirements.txt
✅ TensorFlow 2.15.0 installed successfully
✅ All dependencies resolved

🚀 Deploy Log:
✅ Python version verified: 3.10.12
✅ TensorFlow loaded successfully
✅ Model files found
✅ Label encoder found
✅ Streamlit app started on port $PORT
```

### 5. Troubleshooting

**If TensorFlow fails to install:**
- Check that `runtime.txt` specifies Python 3.10.12
- Verify `requirements.txt` has `tensorflow==2.15.0`
- Check build logs for version conflicts

**If models are missing:**
- Ensure `models/` directory is committed to git
- Check `.gitignore` doesn't exclude model files
- Verify model files are under GitHub's 100MB limit

**If app won't start:**
- Check the build logs for any pip install errors
- Verify `start.sh` is executable (should be handled by git)
- Check that all dependencies are properly pinned

### 6. Performance Considerations

**Free Tier Limitations:**
- 512MB RAM (sufficient for the model)
- CPU-only inference (no GPU needed)
- App sleeps after 15 minutes of inactivity
- 750 hours/month usage limit

**Optimization Tips:**
- Model loading happens at startup (first request may be slow)
- Subsequent predictions are fast (2-4ms)
- Database persists between deployments

### 7. Post-Deployment Verification

Once deployed, verify:
1. **Health check**: Visit your app URL
2. **Upload test**: Try uploading a furniture image
3. **Check predictions**: Verify tables/TVs are classified correctly
4. **Analytics**: Confirm prediction logging works

### 8. Custom Domain (Optional)
In Render dashboard:
1. Go to your service → **Settings**
2. Scroll to **Custom Domains**
3. Add your domain and configure DNS

## Deployment Checklist

- [ ] Repository contains all required files
- [ ] `runtime.txt` specifies Python 3.10.12
- [ ] `requirements.txt` has pinned versions
- [ ] Model files are committed and accessible
- [ ] `.gitignore` allows necessary files
- [ ] GitHub repository is public or connected to Render
- [ ] Render service configured with correct commands
- [ ] Build completes without errors
- [ ] App starts successfully
- [ ] Predictions work correctly
- [ ] Tables/TVs classification is fixed

## Expected Costs
- **Free Tier**: $0/month (with limitations)
- **Starter Plan**: $7/month (no sleep, more resources)
- **Standard Plan**: $25/month (production-ready)

## Support
If you encounter issues:
1. Check Render build/deploy logs
2. Verify Python 3.10 is being used
3. Test locally first with Python 3.10
4. Contact Render support if needed
