# Spotlight Setup Guide

## Issue 1: Google Maps Errors (FIXED)

### Problem
You're seeing these errors:
```
InvalidKeyMapError - Google Maps JavaScript API error
Element with name "gmp-map" already defined (loaded multiple times)
```

### Root Cause
The hardcoded API key in your code (`AIzaSyBXGbZ0f6cCG4Kf6PpxBt5y9eKhPJU8vX4`) is invalid.

### Solution

**Step 1: Get a Google Maps API Key**
1. Go to: https://console.cloud.google.com/google/maps-apis/credentials
2. Create a new project (or select existing)
3. Click "Create Credentials" → "API Key"
4. Copy your API key

**Step 2: Enable Required APIs**
In Google Cloud Console, enable these APIs:
- Maps JavaScript API
- Places API  
- Geocoding API

**Step 3: Create `.env.local` file**
```bash
cd /Users/melany.macias/Documents/Personal/spotlight/frontend
touch .env.local
```

**Step 4: Add your API key to `.env.local`**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

**Step 5: Restart frontend dev server**
```bash
npm run dev
```

---

## Issue 2: Terminal Logs (EXPLAINED)

### What You're Seeing
```bash
INFO:     Uvicorn running on http://0.0.0.0:8000
🚀 Starting Spotlight API...
✓ Database initialized
INFO:     Application startup complete.
```

### This is Normal!
You **are** seeing the logs correctly. You'll see request logs when you:
1. Make API calls from the frontend
2. Use `curl` to test endpoints

### To See More Detailed Logs

**Option 1: Increase uvicorn log level**
```bash
uvicorn main:app --reload --log-level debug
```

**Option 2: Add Python logging to main.py**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Then in endpoints:
@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "healthy"}
```

**Option 3: Watch logs in real-time with colors**
```bash
uvicorn main:app --reload --access-log --log-config log_config.yaml
```

### Test That Logs Are Working
```bash
# In another terminal, make a request:
curl http://localhost:8000/health

# You should see in the server terminal:
# INFO: 127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
```

### Example: Test Concepts API (You Should See Request Logs)
```bash
# List all concepts
curl http://localhost:8000/api/concepts

# You should see in server terminal:
# INFO: 127.0.0.1:xxxxx - "GET /api/concepts HTTP/1.1" 200 OK
```

---

## Quick Start Checklist

- [ ] Get Google Maps API key
- [ ] Enable Maps JavaScript API, Places API, Geocoding API
- [ ] Create `frontend/.env.local` with your API key
- [ ] Restart frontend: `npm run dev`
- [ ] Backend is running: `uvicorn main:app --reload`
- [ ] Test: Open http://localhost:3000
- [ ] Google Maps errors should be gone ✅

---

## Debugging Tips

### Frontend Errors
**Check browser console:**
- Open DevTools (F12)
- Console tab
- Should NOT see "InvalidKeyMapError" anymore

### Backend Logs
**Test if backend is working:**
```bash
# Health check
curl http://localhost:8000/health

# List concepts (should show 5 system defaults)
curl http://localhost:8000/api/concepts

# You should see logs in terminal for each request
```

### Still Not Seeing Logs?
Make sure you're running uvicorn directly (not in background):
```bash
cd /Users/melany.macias/Documents/Personal/spotlight/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Do NOT background it** (`&` at end) if you want to see logs.

---

## What Logs You Should See

### On Startup:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28214] using WatchFiles
INFO:     Started server process [28227]
INFO:     Waiting for application startup.
🚀 Starting Spotlight API...
Initializing database at: sqlite:///./spotlight.db
✓ Database tables created successfully
✓ Database initialized
INFO:     Application startup complete.
```

### On Each Request:
```
INFO:     127.0.0.1:54321 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:54322 - "GET /api/concepts HTTP/1.1" 200 OK
INFO:     127.0.0.1:54323 - "POST /api/discover HTTP/1.1" 200 OK
```

### If You're Not Seeing Request Logs:
1. ✅ Your server IS working
2. ✅ Logs ARE being generated
3. ❓ You just haven't made any requests yet

**Make a request to see logs appear**:
```bash
curl http://localhost:8000/health
```

You should immediately see:
```
INFO:     127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
```

---

## Summary

**Google Maps Issue**: Hardcoded invalid API key
- **Fix**: Get real key, add to `.env.local`, restart frontend

**Logs Issue**: No issue! Logs appear when requests are made
- **Fix**: Make a request (curl or use frontend)

**Your terminal output is correct.** You're seeing exactly what you should see. Request logs will appear when you use the API.

