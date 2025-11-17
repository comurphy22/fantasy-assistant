# 🔧 Fix Flask Service Gunicorn Error

## Problem
Gunicorn is trying to import `main:app` but your Flask file is `app.py`, so it should be `app:app`.

## Solution

### Option 1: Update Start Command in Railway (Recommended)

In your Flask service settings in Railway:

1. Go to **Settings** → **Service**
2. Find **Start Command**
3. Change it to:
   ```
   gunicorn app:app -b 0.0.0.0:$PORT
   ```
4. Save and redeploy

### Option 2: Use Procfile

I've created a `Procfile` in `flask-service/` that Railway will automatically detect.

**Start Command in Railway:** Leave blank (Railway will use Procfile automatically)

Or set it to:
```
gunicorn app:app -b 0.0.0.0:$PORT
```

### Option 3: Use Python Directly (Simpler, but less performant)

**Start Command:**
```
python app.py
```

This uses Flask's built-in server (fine for development, but gunicorn is better for production).

---

## Recommended Configuration

**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `gunicorn app:app -b 0.0.0.0:$PORT`  
**Root Directory:** `flask-service`

---

## Why This Happened

Railway's auto-detection might have defaulted to `gunicorn main:app` (common convention), but your file is `app.py`, not `main.py`.

---

**After updating the start command, redeploy and it should work!**

