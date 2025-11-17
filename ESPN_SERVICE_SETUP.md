# 🔧 ESPN Service Setup

## Problem
The ESPN integration requires a Flask service that was running locally on `localhost:5002`, but it's not deployed in production.

## Current Status
- ✅ ESPN credentials are being saved correctly
- ❌ ESPN roster/free agents calls are failing because Flask service isn't available

## Solution Options

### Option 1: Deploy Flask Service (Recommended for Full Functionality)

The Flask service (`app.py`) needs to be deployed separately. You can deploy it to:

**Railway (Easiest):**
1. Create a new Railway service
2. Set Python as the runtime
3. Add `app.py` and `requirements.txt`
4. Set environment variables if needed
5. Get the URL (e.g., `https://your-flask-service.up.railway.app`)
6. Add `FLASK_SERVICE_URL` to your Go API's Railway environment variables

**Render:**
1. Create a new Web Service
2. Use Python runtime
3. Deploy `app.py`
4. Get the URL and add to Railway env vars

### Option 2: Disable ESPN Features (Quick Fix)

If you don't need ESPN functionality right now, you can:
1. Hide the ESPN features in the frontend
2. Or show a "Coming Soon" message
3. The credentials will still be saved, but roster calls will fail gracefully

### Option 3: Integrate ESPN into Go Service (Advanced)

You could rewrite the Flask ESPN functionality directly in Go, but this is more work.

---

## Quick Fix: Make URL Configurable

I've already updated the code to use an environment variable `FLASK_SERVICE_URL`. 

**To fix the immediate issue:**

1. **In Railway** (where your Go API is deployed):
   - Go to **Variables** tab
   - Add new variable:
     - **Key**: `FLASK_SERVICE_URL`
     - **Value**: `http://localhost:5002` (for now, or your deployed Flask URL)
   - Redeploy

2. **For production**, you'll need to:
   - Deploy the Flask service (`app.py`)
   - Update `FLASK_SERVICE_URL` to point to the deployed Flask service

---

## Deploy Flask Service to Railway

If you want to deploy the Flask service:

1. **Create a new Railway service:**
   - Click "New Project" → "Empty Service"
   - Name it: `fantasy-assistant-flask`

2. **Configure it:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py` or `gunicorn app:app`
   - **Port**: `5002` (or let Railway assign one)

3. **Add files:**
   - `app.py`
   - `requirements.txt` (create if missing)

4. **Set environment variables** (if needed):
   - `ESPN_LEAGUE_ID`
   - `ESPN_TEAM_ID`
   - `ESPN_YEAR`
   - `ESPN_S2`
   - `ESPN_SWID`

5. **Get the URL:**
   - Railway will give you a URL like: `https://fantasy-assistant-flask.up.railway.app`

6. **Update Go API:**
   - In your Go API Railway service
   - Update `FLASK_SERVICE_URL` to: `https://fantasy-assistant-flask.up.railway.app`
   - Redeploy

---

## Check Flask Service Requirements

Make sure you have a `requirements.txt` for the Flask service:

```txt
flask
flask-cors
espn-api
python-dotenv
```

---

## Current Error

The error "Unable to reach ESPN service" happens because:
- Go API tries to call: `http://localhost:5002/api/espn/roster`
- But `localhost:5002` doesn't exist in Railway's production environment
- The Flask service needs to be deployed separately

---

**Next Steps:**
1. Decide if you want to deploy the Flask service now
2. Or temporarily disable ESPN features until you deploy it
3. The code is now configurable, so once Flask is deployed, just update the URL!

