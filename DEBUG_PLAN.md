# Diksha Fundraising Bot - Debug Plan

## 🎯 Overview
This document provides a systematic approach to debugging the Diksha Fundraising Bot application, covering both local development and Railway deployment issues.

## 📋 Debug Checklist

### 1. **Environment Setup Verification**
- [ ] Python version compatibility (3.8+)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured
- [ ] Google Sheets credentials valid
- [ ] Network connectivity to external APIs

### 2. **Backend Service Debugging**

#### 2.1 Flask App Startup
```bash
# Test basic Flask startup
python app.py

# Expected output:
# ✅ Backend package imported successfully
# 🚀 Starting Flask app on port 5000
# 🌐 Health check available at: http://0.0.0.0:5000/api/health
```

#### 2.2 Health Check Endpoints
```bash
# Test health check
curl http://localhost:5000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Diksha Fundraising Backend",
#   "timestamp": "2024-01-15T10:30:00",
#   "backend_available": true
# }
```

#### 2.3 API Endpoints Testing
```bash
# Test pipeline endpoint
curl http://localhost:5000/api/pipeline

# Test activities endpoint
curl http://localhost:5000/api/activities

# Test proposals endpoint
curl http://localhost:5000/api/proposals

# Test alerts endpoint
curl http://localhost:5000/api/alerts
```

### 3. **Google Sheets Integration Debugging**

#### 3.1 Credentials Verification
```python
# Test credentials in Python
import os
import base64
import json

# Check if credentials are available
credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
if credentials_base64:
    try:
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials_info = json.loads(credentials_json)
        print("✅ Credentials decoded successfully")
        print(f"Service account: {credentials_info.get('client_email')}")
    except Exception as e:
        print(f"❌ Credentials decode failed: {e}")
else:
    print("❌ GOOGLE_CREDENTIALS_BASE64 not set")
```

#### 3.2 Sheets Access Test
```python
# Test Google Sheets access
from backend.core.sheets_db import SheetsDB

sheets_db = SheetsDB()
if sheets_db.initialized:
    print("✅ SheetsDB initialized successfully")
    
    # Test pipeline data
    pipeline_data = sheets_db.get_pipeline_data()
    print(f"📊 Pipeline data: {len(pipeline_data)} records")
    
    # Test interaction log
    activities = sheets_db.get_interaction_log()
    print(f"📝 Activities: {len(activities)} records")
    
    # Test proposals
    proposals = sheets_db.get_proposals()
    print(f"📋 Proposals: {len(proposals)} records")
    
    # Test alerts
    alerts = sheets_db.get_alerts()
    print(f"🚨 Alerts: {len(alerts)} records")
else:
    print("❌ SheetsDB initialization failed")
```

### 4. **Streamlit App Debugging**

#### 4.1 Local Streamlit Testing
```bash
# Navigate to streamlit app directory
cd streamlit-app

# Test Streamlit startup
streamlit run streamlit_app.py

# Expected output:
# ✅ Using lib package import for check_auth
# ✅ Using lib.api imports for dashboard metrics
# ✅ Final check_auth import: True
```

#### 4.2 Import System Testing
```python
# Test import system in streamlit-app/lib/
import sys
import os

# Check if lib path is correct
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
print(f"Lib path: {lib_path}")
print(f"Lib exists: {os.path.exists(lib_path)}")

# Test API imports
try:
    from lib.api import get_cached_pipeline_data
    print("✅ API import successful")
except ImportError as e:
    print(f"❌ API import failed: {e}")

# Test auth imports
try:
    from lib.auth import check_auth
    print("✅ Auth import successful")
except ImportError as e:
    print(f"❌ Auth import failed: {e}")
```

### 5. **Railway Deployment Debugging**

#### 5.1 Build Process Debugging
```bash
# Check Railway build logs for:
# - Python version
# - Dependencies installation
# - Import errors
# - Port configuration
```

#### 5.2 Runtime Debugging
```bash
# Check Railway runtime logs for:
# - Flask startup messages
# - Backend import status
# - Health check responses
# - API endpoint errors
```

#### 5.3 Environment Variables Check
```bash
# Verify Railway environment variables:
# - PORT (automatically set by Railway)
# - MAIN_SHEET_ID
# - GOOGLE_CREDENTIALS_BASE64
# - API_BASE (for Streamlit app)
```

### 6. **Common Issues & Solutions**

#### 6.1 Backend Import Failures
**Symptoms:** `ModuleNotFoundError` or `ImportError`
**Solutions:**
- Check if all backend modules exist
- Verify Python path configuration
- Ensure all dependencies are installed
- Check for circular imports

#### 6.2 Google Sheets Access Issues
**Symptoms:** `HttpError 403` or `HttpError 404`
**Solutions:**
- Verify service account email has access to the sheet
- Check if sheet ID is correct
- Ensure credentials are properly base64 encoded
- Verify sheet tabs exist and have data

#### 6.3 Streamlit Import Issues
**Symptoms:** `ModuleNotFoundError: No module named 'lib'`
**Solutions:**
- Check if `streamlit-app/lib/` directory exists
- Verify `__init__.py` files are present
- Ensure lib directory is not in `.gitignore`
- Check import path configuration

#### 6.4 Railway Health Check Failures
**Symptoms:** Health check timeout or 503 errors
**Solutions:**
- Verify Flask app starts successfully
- Check if app binds to `0.0.0.0:PORT`
- Ensure health check endpoint returns 200
- Check for startup errors in logs

### 7. **Debug Tools & Commands**

#### 7.1 Local Testing Scripts
```bash
# Test backend startup
python -c "from app import app; print('✅ Flask app imported successfully')"

# Test Google Sheets connection
python -c "from backend.core.sheets_db import SheetsDB; db = SheetsDB(); print(f'SheetsDB initialized: {db.initialized}')"

# Test Streamlit imports
cd streamlit-app && python -c "from lib.api import get_cached_pipeline_data; print('✅ Streamlit imports work')"
```

#### 7.2 Log Analysis
```bash
# Check Flask app logs
tail -f app.log

# Check Railway logs
railway logs

# Check Streamlit logs
streamlit run streamlit_app.py --logger.level debug
```

#### 7.3 Network Testing
```bash
# Test local API endpoints
curl -v http://localhost:5000/api/health
curl -v http://localhost:5000/api/pipeline

# Test Railway endpoints (replace with actual URL)
curl -v https://your-app.railway.app/api/health
curl -v https://your-app.railway.app/api/pipeline
```

### 8. **Performance Debugging**

#### 8.1 API Response Times
```python
import time
import requests

# Test API response times
start_time = time.time()
response = requests.get('http://localhost:5000/api/pipeline')
end_time = time.time()

print(f"API response time: {end_time - start_time:.2f} seconds")
print(f"Response status: {response.status_code}")
print(f"Data size: {len(response.content)} bytes")
```

#### 8.2 Google Sheets Performance
```python
# Test Google Sheets API performance
import time
from backend.core.sheets_db import SheetsDB

sheets_db = SheetsDB()
if sheets_db.initialized:
    start_time = time.time()
    data = sheets_db.get_pipeline_data()
    end_time = time.time()
    
    print(f"Sheets API response time: {end_time - start_time:.2f} seconds")
    print(f"Records retrieved: {len(data)}")
```

### 9. **Error Recovery Procedures**

#### 9.1 Backend Service Recovery
1. Check Railway logs for specific errors
2. Restart the Railway service
3. Verify environment variables
4. Test health check endpoint
5. Check Google Sheets connectivity

#### 9.2 Streamlit App Recovery
1. Clear Streamlit cache: `streamlit cache clear`
2. Restart Streamlit app
3. Check import paths
4. Verify API connectivity
5. Test with fallback data

#### 9.3 Data Recovery
1. Verify Google Sheets access
2. Check sheet permissions
3. Test with sample data
4. Verify data format
5. Check for empty responses

### 10. **Monitoring & Alerts**

#### 10.1 Health Monitoring
- Set up Railway health checks
- Monitor API response times
- Track error rates
- Monitor Google Sheets API usage

#### 10.2 Log Monitoring
- Set up log aggregation
- Monitor for error patterns
- Track performance metrics
- Alert on critical failures

## 🚀 Quick Debug Commands

```bash
# Full system test
python -c "
import sys
print(f'Python version: {sys.version}')
try:
    from app import app
    print('✅ Flask app OK')
except Exception as e:
    print(f'❌ Flask app error: {e}')

try:
    from backend.core.sheets_db import SheetsDB
    db = SheetsDB()
    print(f'✅ SheetsDB OK: {db.initialized}')
except Exception as e:
    print(f'❌ SheetsDB error: {e}')
"

# Test all API endpoints
for endpoint in ['/api/health', '/api/pipeline', '/api/activities', '/api/proposals', '/api/alerts']:
    try:
        response = requests.get(f'http://localhost:5000{endpoint}')
        print(f'✅ {endpoint}: {response.status_code}')
    except Exception as e:
        print(f'❌ {endpoint}: {e}')
```

## 📞 Support Contacts

- **Technical Issues:** Check logs and follow this debug plan
- **Google Sheets Issues:** Verify permissions and credentials
- **Railway Issues:** Check Railway documentation and logs
- **Streamlit Issues:** Check import paths and dependencies

---

**Last Updated:** January 2024
**Version:** 1.0
