# 🎓 Free Deployment Guide for Students

This guide will help you deploy your NFL Fantasy Platform **completely free** using student-friendly services.

## 📋 Overview

**Recommended Stack (100% Free):**

- **Frontend (Next.js)**: Vercel (Free tier - unlimited)
- **Backend (Go API)**: Railway ($5/month free credit) or Render (Free tier)
- **Database**: MongoDB Atlas (Free M0 tier - 512MB)

**Total Cost: $0/month** ✅

---

## 🚀 Step-by-Step Deployment

### Step 1: Set Up MongoDB Atlas (Database) - FREE

1. **Sign up** at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. **Create a free cluster** (M0 Sandbox):
   - Click "Build a Database"
   - Choose "M0" (Free tier)
   - Select a cloud provider (AWS, Google Cloud, or Azure)
   - Choose a region close to you
   - Click "Create"
3. **Create a database user**:
   - Go to "Database Access" → "Add New Database User"
   - Username: `nfl-platform-user`
   - Password: Generate a secure password (save it!)
   - Database User Privileges: "Read and write to any database"
4. **Whitelist your IP**:
   - Go to "Network Access" → "Add IP Address"
   - For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
   - For production: Add specific IPs later
5. **Get your connection string**:
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
   - Replace `<password>` with your actual password
   - Add database name: `mongodb+srv://username:password@cluster.mongodb.net/nfl_platform?retryWrites=true&w=majority`

**✅ Save this connection string - you'll need it later!**

---

### Step 2: Deploy Backend (Go API) - FREE Options

#### Option A: Railway (Recommended - $5/month free credit)

**Why Railway?**

- $5/month free credit (enough for small apps)
- Easy deployment from GitHub
- Automatic HTTPS
- Simple environment variable management

**Steps:**

1. **Sign up** at [railway.app](https://railway.app) (use GitHub login)
2. **Install Railway CLI** (optional, but helpful):
   ```bash
   npm install -g @railway/cli
   railway login
   ```
3. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
4. **Configure the service**:
   - Railway will auto-detect Go
   - Set these environment variables in Railway dashboard:
     ```
     MONGODB_URI=your_mongodb_connection_string_here
     DB_NAME=nfl_platform
     JWT_SECRET=generate_a_random_secret_key_here
     GEMINI_API_KEY=your_gemini_api_key
    PORT=808
     ENVIRONMENT=production
     ```
   - To generate JWT_SECRET: `openssl rand -base64 32`
5. **Deploy**:
   - Railway will automatically build and deploy
   - Your API will be available at: `https://your-project-name.up.railway.app`

**✅ Save your API URL!**

#### Option B: Render (Free tier with limitations)

**Why Render?**

- Free tier available (but spins down after 15 min inactivity)
- Good for development/testing
- Easy GitHub integration

**Steps:**

1. **Sign up** at [render.com](https://render.com) (use GitHub login)
2. **Create a new Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
3. **Configure**:
   - **Name**: `nfl-platform-api`
   - **Environment**: `Go`
   - **Build Command**: `go build -o nfl-api cmd/api/main.go`
   - **Start Command**: `./nfl-api`
   - **Plan**: Free
4. **Add Environment Variables**:
   ```
   MONGODB_URI=your_mongodb_connection_string
   DB_NAME=nfl_platform
   JWT_SECRET=your_random_secret
   GEMINI_API_KEY=your_gemini_api_key
   PORT=8080
   ENVIRONMENT=production
   ```
5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy
   - Your API: `https://nfl-platform-api.onrender.com`

**Note**: Free tier spins down after inactivity. First request may take 30-60 seconds.

---

### Step 3: Deploy Frontend (Next.js) - Vercel (FREE)

**Why Vercel?**

- **Perfect for Next.js** (made by Next.js creators)
- Completely free for personal projects
- Automatic HTTPS
- Global CDN
- Instant deployments

**Steps:**

1. **Sign up** at [vercel.com](https://vercel.com) (use GitHub login)
2. **Import your project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - **Root Directory**: Select `frontend` folder
3. **Configure build settings**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)
4. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-or-render-url.com
   ```
   (Use the backend URL from Step 2)
5. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your frontend: `https://your-project.vercel.app`

**✅ Your app is now live!**

---

## 🔧 Post-Deployment Setup

### 1. Initialize Database Indexes

After deployment, you need to create database indexes. You can do this by:

**Option A: Run locally (recommended)**

```bash
# Set your production MongoDB URI
export MONGODB_URI="your_mongodb_connection_string"
export DB_NAME="nfl_platform"

# Run the index creation script
go run cmd/create_waiver_indexes/main.go
```

**Option B: SSH into your deployment** (if available)

### 2. Load Initial Data (Optional)

If you want to load NFL data:

```bash
# Set environment variables
export MONGODB_URI="your_mongodb_connection_string"
export DB_NAME="nfl_platform"

# Load data (this takes 30-60 minutes for full dataset)
make load-maximum-data
```

### 3. Update CORS Settings

Update your backend CORS middleware to allow your Vercel domain:

```go
// internal/middleware/cors.go
func CORS() gin.HandlerFunc {
    return cors.New(cors.Config{
        AllowOrigins: []string{
            "https://your-project.vercel.app",
            "http://localhost:3000", // Keep for local dev
        },
        // ... rest of config
    })
}
```

---

## 🎓 AWS Alternative (If You Want to Use AWS)

**AWS Educate** provides free credits for students:

- $75-200 in credits (varies by institution)
- Valid for 1 year
- Good for learning AWS services

**AWS Free Tier Services:**

- **EC2**: 750 hours/month of t2.micro (free for 12 months)
- **RDS**: 750 hours/month of db.t2.micro (free for 12 months)
- **Elastic Beanstalk**: Free (just pay for EC2)
- **S3**: 5GB storage free (always free)

**However**, AWS is more complex than Railway/Render. For a quick deployment, stick with the recommended stack above.

**If you want to use AWS**, here's a quick guide:

1. **Sign up for AWS Educate**: [aws.amazon.com/education/awseducate](https://aws.amazon.com/education/awseducate/)
2. **Deploy Backend to Elastic Beanstalk**:
   - Create a new application
   - Upload your Go code
   - Configure environment variables
3. **Deploy Frontend to S3 + CloudFront**:
   - Build: `npm run build`
   - Upload `out` folder to S3
   - Enable static website hosting
   - Optionally add CloudFront for CDN

**But honestly, Railway + Vercel is much easier!** 😊

---

## 💰 Cost Breakdown

### Recommended Stack (100% Free)

- **MongoDB Atlas M0**: $0/month (512MB storage)
- **Railway**: $0/month ($5 credit covers small apps)
- **Vercel**: $0/month (unlimited for personal projects)
- **Gemini API**: ~$0.001 per request (very cheap)
- **Total**: **$0-5/month** (depending on usage)

### If You Exceed Free Tiers

- **Railway**: $5/month for Hobby plan
- **Render**: $7/month for Starter plan
- **MongoDB Atlas**: $9/month for M2 cluster (if you need more storage)

---

## 🔒 Security Checklist

Before going to production:

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Update CORS to only allow your Vercel domain
- [ ] Restrict MongoDB IP whitelist (remove 0.0.0.0/0)
- [ ] Use HTTPS everywhere (automatic with Vercel/Railway)
- [ ] Don't commit `.env` files to Git
- [ ] Enable MongoDB authentication (already done)
- [ ] Consider adding rate limiting (see DEPLOYMENT.md)

---

## 🐛 Troubleshooting

### Backend won't start

- Check environment variables are set correctly
- Verify MongoDB connection string
- Check logs in Railway/Render dashboard

### Frontend can't connect to backend

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is running (check Railway/Render dashboard)

### Database connection fails

- Verify MongoDB IP whitelist includes your deployment IP
- Check connection string format
- Ensure database user has correct permissions

### Build fails

- Check build logs in Vercel/Railway dashboard
- Ensure all dependencies are in `package.json`/`go.mod`
- Verify Node.js/Go versions are compatible

---

## 📚 Additional Resources

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas Docs**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **Next.js Deployment**: [nextjs.org/docs/deployment](https://nextjs.org/docs/deployment)

---

## 🎉 You're Done!

Your application should now be live at:

- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-api.railway.app` or `https://your-api.onrender.com`

**Next Steps:**

1. Test your deployed app
2. Share it with friends!
3. Monitor usage in Railway/Vercel dashboards
4. Load NFL data if needed

---

**Questions?** Check the main `DEPLOYMENT.md` or open an issue on GitHub.

**Good luck with your deployment!** 🚀
