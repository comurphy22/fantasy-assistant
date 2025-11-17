# 🚀 Quick Deployment Checklist

Use this checklist to deploy your app step-by-step.

## ✅ Pre-Deployment

- [ ] Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Ensure your code is pushed to GitHub
- [ ] Test locally that everything works

---

## 📦 Step 1: MongoDB Atlas (5 minutes)

- [ ] Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- [ ] Create M0 (Free) cluster
- [ ] Create database user (username + password)
- [ ] Whitelist IP: `0.0.0.0/0` (for now)
- [ ] Get connection string
- [ ] **Save connection string** ✅

**Connection string format:**
```
mongodb+srv://username:password@cluster.mongodb.net/nfl_platform?retryWrites=true&w=majority
```

---

## 🔧 Step 2: Deploy Backend (10 minutes)

### Option A: Railway (Recommended)

- [ ] Sign up at [railway.app](https://railway.app) (GitHub login)
- [ ] Create new project → Deploy from GitHub
- [ ] Select your repository
- [ ] Add environment variables:
  - [ ] `MONGODB_URI` = your MongoDB connection string
  - [ ] `DB_NAME` = `nfl_platform`
  - [ ] `JWT_SECRET` = generate with `openssl rand -base64 32`
  - [ ] `GEMINI_API_KEY` = your Gemini API key
  - [ ] `PORT` = `8080`
  - [ ] `ENVIRONMENT` = `production`
- [ ] Wait for deployment
- [ ] **Save your API URL** ✅ (e.g., `https://your-project.up.railway.app`)

### Option B: Render

- [ ] Sign up at [render.com](https://render.com) (GitHub login)
- [ ] New → Web Service
- [ ] Connect GitHub repo
- [ ] Configure:
  - Build: `go build -o nfl-api cmd/api/main.go`
  - Start: `./nfl-api`
- [ ] Add same environment variables as Railway
- [ ] Deploy
- [ ] **Save your API URL** ✅

---

## 🎨 Step 3: Deploy Frontend (5 minutes)

- [ ] Sign up at [vercel.com](https://vercel.com) (GitHub login)
- [ ] Add New → Project
- [ ] Import GitHub repository
- [ ] **Important**: Set Root Directory to `frontend`
- [ ] Add environment variable:
  - [ ] `NEXT_PUBLIC_API_URL` = your backend URL from Step 2
- [ ] Deploy
- [ ] **Save your frontend URL** ✅ (e.g., `https://your-project.vercel.app`)

---

## 🔒 Step 4: Update CORS (2 minutes)

Update your backend CORS to allow your Vercel domain:

1. Edit `internal/middleware/cors.go`
2. Add your Vercel URL to allowed origins
3. Redeploy backend (Railway/Render will auto-deploy on git push)

---

## 🗄️ Step 5: Initialize Database (5 minutes)

Run locally to create indexes:

```bash
# Set environment variables
export MONGODB_URI="your_mongodb_connection_string"
export DB_NAME="nfl_platform"

# Create indexes
go run scripts/create_indexes.go

# Optional: Create waiver indexes
go run cmd/create_waiver_indexes/main.go
```

---

## 📊 Step 6: Load Data (Optional - 30-60 minutes)

If you want NFL data in your database:

```bash
export MONGODB_URI="your_mongodb_connection_string"
export DB_NAME="nfl_platform"

# Load maximum data (all seasons)
make load-maximum-data
```

---

## ✅ Step 7: Test Your Deployment

- [ ] Visit your frontend URL
- [ ] Register a new account
- [ ] Login
- [ ] Test chatbot
- [ ] Test player search
- [ ] Check browser console for errors

---

## 🔐 Security (Before Production)

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Update MongoDB IP whitelist (remove `0.0.0.0/0`, add specific IPs)
- [ ] Verify HTTPS is enabled (automatic with Vercel/Railway)
- [ ] Don't commit `.env` files to Git

---

## 📝 URLs to Save

- **Frontend**: `https://________________.vercel.app`
- **Backend**: `https://________________.railway.app` or `.onrender.com`
- **MongoDB Connection**: `mongodb+srv://...`

---

## 🆘 Troubleshooting

**Backend won't start?**
- Check environment variables in Railway/Render dashboard
- Check logs in dashboard
- Verify MongoDB connection string

**Frontend can't connect?**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend
- Check browser console for errors

**Database connection fails?**
- Verify MongoDB IP whitelist
- Check connection string format
- Ensure database user has correct permissions

---

## 🎉 You're Done!

Your app should now be live! Share it with friends and test it out.

**Next Steps:**
- Monitor usage in dashboards
- Load NFL data if needed
- Customize and improve!

---

**Need help?** Check `FREE_DEPLOYMENT_GUIDE.md` for detailed instructions.

