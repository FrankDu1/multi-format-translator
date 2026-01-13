# Fixing CORS and Dependency Issues in a Dockerized Flask Translation API

## Background

I was deploying a multi-format translation service with a microservices architecture:
- **Frontend**: Running on port 5001
- **Translation API**: Running on port 5002
- **OCR Service**: Port 8899
- **Inpainting Service**: Port 8900

Everything worked locally, but after deploying to Docker on a remote server (accessed via IP: `http://40.162.204.61`), I encountered two critical issues.

---

## Problem 1: CORS Blocking API Requests

### Error Message
```
Access to fetch at 'http://40.162.204.61:5002/api/translate/translate-text' 
from origin 'http://40.162.204.61:5001' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause
When the frontend (port 5001) tries to call the backend API (port 5002), browsers treat this as a **cross-origin request** because:
- Different ports = Different origins
- Browser sends a **preflight OPTIONS request** to check permissions
- The API didn't respond with proper CORS headers

### Initial Configuration (Incomplete)
```python
# app.py - Old version
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
```

This only set `Access-Control-Allow-Origin`, but **missed the critical header**:
- ❌ Missing: `Access-Control-Allow-Headers: Content-Type`

Without this, browsers reject POST requests with JSON payloads.

### Solution
Implemented **comprehensive CORS configuration** with all necessary headers:

```python
# config.py
APP_ENV = os.getenv('APP_ENV', 'development')

if APP_ENV == 'production':
    # 🔒 Strict: Explicit origins only
    ALLOWED_ORIGINS = ['https://offerupup.cn', 'https://www.offerupup.cn']
else:
    # 🔓 Permissive: Allow all for development
    ALLOWED_ORIGINS = ['*']
```

```python
# app.py
if ALLOWED_ORIGINS == ['*']:
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": [
                 "Content-Type",      # ✅ Critical!
                 "Authorization",
                 "X-Requested-With",
                 "Accept",
                 "Origin"
             ],
             "expose_headers": ["Content-Type", "Content-Length"],
             "max_age": 3600,
             "supports_credentials": False
         }})
```

**Key Points:**
- `allow_headers` must explicitly list all headers the frontend will send
- `max_age: 3600` caches preflight results for 1 hour (reduces requests)
- Wildcard (`*`) origin cannot use `supports_credentials: True` (browser restriction)

---

## Problem 2: Missing torch Dependency in Cloud Translation Mode

### Error Message
```python
NameError: name 'AutoTokenizer' is not defined
ModuleNotFoundError: No module named 'torch'
```

### Root Cause
The application supports two translation modes:
1. **Local Mode**: Uses NLLB model (requires PyTorch + transformers)
2. **Cloud Mode**: Uses Alibaba Cloud Translation API (no local model needed)

However, the code imported `torch` at the **module level**:
```python
# ❌ Old version - imports torch unconditionally
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
```

Even with `USE_CLOUD_TRANSLATE=true`, Python tried to import torch, causing errors.

### Solution
Implemented **conditional imports** and **lazy loading**:

```python
# ✅ New version - conditional import
import os
from dotenv import load_dotenv
load_dotenv()

USE_CLOUD_TRANSLATE = os.getenv('USE_CLOUD_TRANSLATE', 'false').lower() == 'true'

if not USE_CLOUD_TRANSLATE:
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        TORCH_AVAILABLE = True
    except ImportError:
        TORCH_AVAILABLE = False
        logging.warning("⚠️ torch not available, cloud translation required")
else:
    logging.info("ℹ️ Cloud translation mode, skipping torch import")
```

**Modified Methods:**
```python
def load_model(self):
    """Load model (local mode only)"""
    if USE_CLOUD_TRANSLATE:
        logger.info("ℹ️ Cloud translation mode, skipping model load")
        return
    
    # Only import torch when actually needed
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    # ... load model
```

**Files Modified:**
- `nllb_translator_pipeline.py` - Main translator service
- `text_translator.py` - Text translation handler
- `local_translator.py` - Local model wrapper
- `torch_compat.py` - PyTorch compatibility shim

---

## Best Practices Implemented

### 1. Environment-Based CORS Configuration
```bash
# Development/Testing
APP_ENV=development
ALLOWED_ORIGINS=*

# Production
APP_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Conditional Dependencies
- Cloud mode: Only requires `requests`, `flask`, `flask-cors`
- Local mode: Adds `torch`, `transformers` (1GB+ dependencies)
- Reduces Docker image size and startup time

### 3. Smart URL Detection (Frontend)
```javascript
const hostname = window.location.hostname;
const isIP = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname);

if (hostname === 'localhost') {
    return 'http://localhost:5002/api';
} else if (isIP) {
    return protocol + '//' + hostname + ':5002/api';
} else {
    return '/translator-api/api';  // Nginx proxy
}
```

### 4. Graceful Fallback
```python
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Continue with cloud translation
```

---

## Deployment Steps

### 1. Update Configuration
```yaml
# docker-compose.yml
api:
  environment:
    - APP_ENV=development
    - ALLOWED_ORIGINS=*
    - USE_CLOUD_TRANSLATE=true
    - ALI_ACCESS_KEY_ID=${ALI_ACCESS_KEY_ID}
    - ALI_ACCESS_KEY_SECRET=${ALI_ACCESS_KEY_SECRET}
```

### 2. Rebuild Docker Image
```bash
cd translator_api
docker build -t translator-api:latest .
```

### 3. Deploy
```bash
docker-compose down
docker-compose up -d
```

### 4. Verify CORS
```bash
curl -I -X OPTIONS http://localhost:5002/api/translate/translate-text \
  -H "Origin: http://40.162.204.61:5001" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

**Expected Response:**
```
Access-Control-Allow-Origin: http://40.162.204.61:5001
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, ...
Access-Control-Max-Age: 3600
```

---

## Results

✅ **CORS Issues Resolved**
- Frontend can now call backend API from any origin (dev mode)
- Preflight requests properly handled
- 1-hour caching reduces unnecessary OPTIONS requests

✅ **Dependency Issues Resolved**
- Cloud translation works without torch/transformers
- Docker image size reduced by ~1GB
- Faster startup time (no model loading)

✅ **Production Ready**
- Environment-based configuration
- Easy to switch between permissive (dev) and strict (prod) CORS
- Graceful fallback for missing dependencies

---

## Lessons Learned

1. **CORS is Not Optional**: Always configure `allow_headers` explicitly, especially for `Content-Type`

2. **Conditional Imports Matter**: Don't import heavy dependencies at module level if they're optional

3. **Test Preflight Requests**: Use `curl` to test OPTIONS requests before browser testing

4. **Environment Variables**: Use `.env` files and environment-based configuration for flexibility

5. **Docker Considerations**: 
   - Image size matters
   - Startup time impacts user experience
   - Optional dependencies should be truly optional

---

## Security Recommendations

### Development
```env
APP_ENV=development
ALLOWED_ORIGINS=*  # OK for dev
```

### Production
```env
APP_ENV=production
ALLOWED_ORIGINS=https://yourdomain.com  # Explicit only
CORS_ALLOW_CREDENTIALS=true  # If using cookies
```

**Never use `ALLOWED_ORIGINS=*` in production!**

---

## Useful Resources

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## Conclusion

CORS and dependency management are common pain points in microservices architectures. By implementing environment-based configuration and conditional imports, we achieved:
- **Flexibility**: Works in dev, test, and prod environments
- **Performance**: Faster startup, smaller images
- **Security**: Configurable CORS policies
- **Maintainability**: Clear separation of concerns

The code is now production-ready and easily adaptable to different deployment scenarios.

---

**GitHub Repository**: [multi-format-translator](https://github.com/frankdu1/multi-format-translator) _(replace with your actual repo)_

**Tech Stack**: Flask, Docker, React, Alibaba Cloud Translation API, PyTorch (optional)
