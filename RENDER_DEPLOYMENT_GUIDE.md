# Render.com Deployment Guide

## ✅ Configuration Files Ready

The following files have been created and pushed to your repository for Render deployment:

- `render.yaml` - Render service configuration
- `runtime.txt` - Python version specification (3.11.0)
- `requirements.txt` - Python dependencies
- `main.py` - Application entry point

## 🚀 Deployment Steps

### 1. Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `https://github.com/rohit543215/prompt-injector`

### 2. Configure Service Settings

**Basic Settings:**
- **Name**: `pii-detection-api` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `master`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- **Start Command**: `python main.py`

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (recommended)

### 3. Environment Variables

Add these environment variables in Render dashboard:

| Key | Value | Description |
|-----|-------|-------------|
| `PORT` | `8000` | Application port (Render will override) |
| `PYTHON_VERSION` | `3.11` | Python version |

### 4. Health Check

- **Health Check Path**: `/health`

## 🔧 Alternative: Using render.yaml (Recommended)

If you prefer Infrastructure as Code, Render will automatically detect the `render.yaml` file in your repository root and use those settings.

The `render.yaml` contains:
```yaml
services:
  - type: web
    name: pii-detection-api
    env: python
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: python main.py
    envVars:
      - key: PORT
        value: 8000
      - key: PYTHON_VERSION
        value: 3.11
    healthCheckPath: /health
```

## 🌐 API Endpoints

Once deployed, your API will be available at: `https://your-service-name.onrender.com`

**Key Endpoints:**
- `GET /` - API status
- `GET /health` - Health check
- `POST /analyze` - Analyze text for PII
- `POST /mask` - Mask PII in text
- `POST /unmask` - Unmask PII in text
- `POST /protect-prompt` - Generate protected prompts
- `GET /demo/sample-texts` - Get sample texts for testing

## 🔍 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-service-name.onrender.com/health

# Test PII detection
curl -X POST https://your-service-name.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact John Smith at john@email.com"}'

# Test prompt protection
curl -X POST https://your-service-name.onrender.com/protect-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Send email to john.doe@company.com about the meeting"}'
```

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails - Go Error**: 
   - ✅ Fixed: Updated configuration to use Python environment

2. **Module Import Errors**:
   - Check that all dependencies are in `requirements.txt`
   - Verify Python path configuration in `main.py`

3. **spaCy Model Not Found**:
   - Build command includes `python -m spacy download en_core_web_sm`
   - This downloads the required English model

4. **Port Issues**:
   - Render automatically assigns PORT environment variable
   - Application listens on `0.0.0.0:PORT`

### Logs and Monitoring:

- View deployment logs in Render dashboard
- Monitor application performance
- Set up alerts for downtime

## 🔗 Frontend Integration

Update your Netlify frontend to use the Render API URL:

```javascript
// In your frontend JavaScript
const API_BASE_URL = 'https://your-service-name.onrender.com';

// Example API call
async function analyzeText(text) {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
    });
    return response.json();
}
```

## 📝 Next Steps

1. Deploy the service on Render
2. Test all API endpoints
3. Update frontend to use the new API URL
4. Set up monitoring and alerts
5. Consider adding authentication for production use

## 💡 Production Considerations

- **Security**: Add API authentication
- **Rate Limiting**: Implement request limits
- **Monitoring**: Set up logging and metrics
- **Scaling**: Configure auto-scaling if needed
- **Database**: Consider adding persistent storage for session data

Your PII Detection API is now ready for production deployment on Render! 🎉