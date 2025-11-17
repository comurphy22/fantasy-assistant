# 🚀 Deploy Flask Service to Railway

## Quick Steps

### 1. Create New Railway Service

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Empty Service"**
3. Name it: `fantasy-assistant-flask`

### 2. Connect to GitHub

1. Click **"Connect GitHub Repo"**
2. Select your repository: `fantasy-assistant`
3. Railway will auto-detect it

### 3. Configure the Service

Railway should auto-detect Python, but verify:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py` (or `gunicorn app:app -b 0.0.0.0:$PORT`)
- **Root Directory**: Leave blank (or set if Flask app is in subdirectory)

### 4. Add Environment Variables (Optional)

If you want to override default ESPN credentials:

- `ESPN_LEAGUE_ID`
- `ESPN_TEAM_ID`
- `ESPN_YEAR`
- `ESPN_S2`
- `ESPN_SWID`
- `ALLOWED_ORIGINS` (defaults to localhost + Railway backend)

### 5. Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Start the Flask app
3. Assign a public URL

### 6. Get the Flask Service URL

After deployment:
1. Go to the Flask service in Railway
2. Click **"Settings"** → **"Networking"**
3. Copy the public domain (e.g., `https://fantasy-assistant-flask.up.railway.app`)

### 7. Update Go API

1. Go to your **Go API service** in Railway
2. Go to **"Variables"** tab
3. Add/Update:
   - **Key**: `FLASK_SERVICE_URL`
   - **Value**: `https://fantasy-assistant-flask.up.railway.app` (your Flask URL)
4. **Redeploy** the Go API service

### 8. Test

1. Try the ESPN features in your frontend
2. Check Railway logs if there are issues

---

## Files Needed

✅ `app.py` - Flask application  
✅ `requirements.txt` - Python dependencies (already created)

---

## Using Gunicorn (Recommended for Production)

For better performance, use Gunicorn instead of Flask's dev server:

**Start Command**: `gunicorn app:app -b 0.0.0.0:$PORT --workers 2`

This is already in `requirements.txt`, so just update the start command in Railway.

---

## Troubleshooting

### Flask service won't start?
- Check Railway logs
- Verify `requirements.txt` exists
- Make sure `app.py` is in the root directory

### CORS errors?
- Verify `ALLOWED_ORIGINS` includes your Go API URL
- Check Flask service logs

### Can't connect from Go API?
- Verify `FLASK_SERVICE_URL` is set correctly in Go API service
- Check Flask service is running (check logs)
- Verify the URL is accessible (try in browser)

---

## Cost

Railway's free tier ($5/month credit) should cover both services:
- Go API service
- Flask service

Both are lightweight and should stay within the free tier.

---

**After deployment, your ESPN integration should work!** 🎉

