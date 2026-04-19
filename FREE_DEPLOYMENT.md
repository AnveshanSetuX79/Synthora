# 🆓 FREE Deployment Guide - LocalAI Leads Platform

Deploy your entire platform for **$0/month** using free tiers from various providers.

## What You'll Get (100% FREE)

✅ Backend API server (FastAPI)  
✅ Frontend website (React)  
✅ PostgreSQL database  
✅ SSL/HTTPS encryption  
✅ Custom subdomain  
✅ Uptime monitoring  
✅ Automatic deployments  

**Total Cost: $0/month**

---

## Free Services Stack

| Service | Provider | Free Tier | Purpose |
|---------|----------|-----------|---------|
| **Backend** | Render.com | 750 hrs/mo | API server |
| **Frontend** | Vercel.com | Unlimited | Static site |
| **Database** | Neon.tech | 0.5 GB | PostgreSQL |
| **Domain** | DuckDNS | Unlimited | yourapp.duckdns.org |
| **SSL** | Automatic | Unlimited | HTTPS |
| **Monitoring** | UptimeRobot | 50 monitors | Keep backend awake |

---

## Step-by-Step Deployment

### Step 1: Setup Free Database (5 minutes)

**Using Neon.tech (Recommended)**

1. Go to [neon.tech](https://neon.tech)
2. Click "Sign Up" (use Google/GitHub for quick signup)
3. Click "Create a project"
4. Choose:
   - **Project name:** localai-leads
   - **Region:** Choose closest to your target users
   - **PostgreSQL version:** 15 (default)
5. Click "Create project"
6. Copy the connection string from the dashboard
   - It looks like: `postgresql://user:password@ep-xxx.neon.tech:5432/neondb?sslmode=require`
7. Save this connection string - you'll need it in Step 2

**Free Tier Includes:**
- 0.5 GB storage (enough for ~10,000 leads)
- Unlimited queries
- Automatic backups
- 1 project

**Alternative Free Databases:**
- **Supabase:** 500 MB, includes auth & storage
- **ElephantSQL:** 20 MB (very limited)
- **Railway:** 500 MB with $5 free credit

---

### Step 2: Deploy Backend on Render (10 minutes)

**Using Render.com**

1. Go to [render.com](https://render.com)
2. Click "Get Started" and sign up (use GitHub/Google)
3. Click "New +" → "Web Service"
4. Choose "Build and deploy from a Git repository" → "Next"
5. Click "Configure account" → Skip (we'll upload manually)
6. Go back and click "Deploy from local files"

**Upload Your Backend:**

**Method A: Using Render Dashboard**
1. Zip your `backend` folder
2. Upload via Render dashboard
3. Extract and configure

**Method B: Using Render CLI (Easier)**
```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
cd backend
render deploy
```

**Method C: Manual Upload via SFTP**
1. Create service first
2. Use provided SFTP credentials
3. Upload backend folder

**Configure Your Service:**

After upload, configure these settings:

- **Name:** `localai-backend`
- **Region:** Oregon (US West) or closest to you
- **Branch:** main (or leave default)
- **Root Directory:** Leave empty if you uploaded just backend folder
- **Runtime:** Python 3
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5
  ```

**Add Environment Variables:**

Click "Environment" tab and add these variables:

```env
# Database (from Step 1)
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech:5432/neondb?sslmode=require

# Authentication (generate random key)
SECRET_KEY=your-random-secret-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=production
DEBUG=False

# Payment Provider (get from Razorpay)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Google Places API (get from Google Cloud Console)
GOOGLE_PLACES_API_KEY=your_google_api_key

# SMS Provider (choose one)
SMS_ENABLED=true
SMS_PROVIDER=msg91

# MSG91 (India - ₹0.15/SMS)
MSG91_AUTH_KEY=your_msg91_auth_key
MSG91_SENDER_ID=LOCALA

# TRAI DLT (Required for India SMS)
TRAI_DLT_ENTITY_ID=your_entity_id
TRAI_DLT_TEMPLATE_ID=your_template_id

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@yourdomain.com

# AI (optional - for enhanced features)
USE_OLLAMA=false
# OPENAI_API_KEY=sk-proj-your-key-here
```

**Generate SECRET_KEY:**
```bash
# On your local machine
openssl rand -hex 32
```

Click "Create Web Service"

**Wait for deployment** (5-10 minutes)

Your backend will be available at: `https://localai-backend.onrender.com`

**Test it:** Visit `https://localai-backend.onrender.com/docs`

You should see the FastAPI documentation page.

**Run Database Migrations:**

1. In Render dashboard, click your service
2. Click "Shell" tab (top right)
3. Run:
   ```bash
   alembic upgrade head
   ```
4. Wait for migrations to complete

**Free Tier Limits:**
- 750 hours/month (enough for 24/7 with one service)
- 512 MB RAM
- Spins down after 15 min inactivity
- First request after sleep takes ~30 seconds

---

### Step 3: Deploy Frontend on Vercel (5 minutes)

**Using Vercel.com**

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" (use GitHub/Google)
3. Click "Add New..." → "Project"

**Upload Your Frontend:**

**Method A: Drag & Drop (Easiest)**
1. Build your frontend locally first:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. Drag the `dist` folder to Vercel
3. Done!

**Method B: Using Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

**Method C: Upload Entire Project**
1. Click "Browse" and select your `frontend` folder
2. Vercel will auto-detect Vite

**Configure Project:**

- **Framework Preset:** Vite (auto-detected)
- **Root Directory:** `./` (or `frontend` if uploading whole project)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

**Add Environment Variables:**

Click "Environment Variables" and add:

```env
VITE_API_URL=https://localai-backend.onrender.com
VITE_RAZORPAY_KEY_ID=rzp_test_your_key_id
```

Click "Deploy"

Wait 2-3 minutes for deployment.

Your frontend will be at: `https://your-project-name.vercel.app`

**Free Tier Includes:**
- Unlimited deployments
- 100 GB bandwidth/month
- Automatic SSL
- Global CDN
- Custom domains

**Alternative: Netlify**

If you prefer Netlify:

1. Go to [netlify.com](https://netlify.com)
2. Drag & drop your `frontend/dist` folder
3. Add environment variables in Site Settings → Environment Variables
4. Done!

---

### Step 4: Keep Backend Awake (5 minutes)

Render free tier sleeps after 15 minutes of inactivity. Keep it awake with UptimeRobot.

**Using UptimeRobot.com**

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Click "Register for FREE"
3. Verify email and login
4. Click "Add New Monitor"
5. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** LocalAI Backend
   - **URL:** `https://localai-backend.onrender.com/docs`
   - **Monitoring Interval:** 5 minutes
6. Click "Create Monitor"

This pings your backend every 5 minutes, preventing it from sleeping.

**Free Tier:**
- 50 monitors
- 5-minute intervals
- Email/SMS alerts
- 2-month logs

**Alternative: Cron-job.org**

1. Go to [cron-job.org](https://cron-job.org)
2. Create free account
3. Create cronjob:
   - URL: `https://localai-backend.onrender.com/docs`
   - Interval: Every 10 minutes

---

### Step 5: Setup Custom Domain (Optional, 5 minutes)

**Option A: DuckDNS (Easiest)**

1. Go to [duckdns.org](https://duckdns.org)
2. Login with Google/GitHub
3. Enter subdomain: `yourapp` (becomes `yourapp.duckdns.org`)
4. Click "Add domain"
5. In Vercel:
   - Go to Project Settings → Domains
   - Add `yourapp.duckdns.org`
   - Copy the CNAME record
6. In DuckDNS:
   - Update your domain with the CNAME target
7. Wait 5-10 minutes for DNS propagation

**Option B: FreeDNS**

1. Go to [freedns.afraid.org](https://freedns.afraid.org)
2. Create account
3. Choose from 1000+ free domains
4. Setup CNAME to point to Vercel

**Option C: Use Default URLs**

Just use the provided URLs:
- Frontend: `https://your-project.vercel.app`
- Backend: `https://localai-backend.onrender.com`

They work perfectly and include free SSL!

---

### Step 6: Create Admin User (2 minutes)

**Method A: Using Render Shell**

1. Go to Render dashboard
2. Click your backend service
3. Click "Shell" tab
4. Run:
   ```bash
   python scripts/create_admin_user.py
   ```
5. Follow prompts to create admin

**Method B: Using API Directly**

1. Go to `https://localai-backend.onrender.com/docs`
2. Find `/api/auth/register` endpoint
3. Click "Try it out"
4. Enter admin details:
   ```json
   {
     "email": "admin@example.com",
     "password": "SecurePassword123!",
     "full_name": "Admin User",
     "user_type": "admin"
   }
   ```
5. Click "Execute"

**Method C: Using Frontend**

1. Visit your frontend URL
2. Click "Sign Up"
3. Register as admin
4. Manually update database to set role to "admin"

---

## 🎉 Deployment Complete!

Your platform is now live and accessible:

```
✅ Frontend: https://your-project.vercel.app
✅ Backend API: https://localai-backend.onrender.com
✅ API Docs: https://localai-backend.onrender.com/docs
✅ Database: Neon PostgreSQL (0.5 GB)
✅ SSL: Automatic HTTPS
✅ Monitoring: UptimeRobot keeping backend awake
```

**Total Cost: $0/month** 🎉

---

## Testing Your Deployment

1. **Test Backend:**
   ```bash
   curl https://localai-backend.onrender.com/docs
   ```

2. **Test Frontend:**
   - Visit your Vercel URL
   - Try logging in
   - Check if API calls work

3. **Test Database:**
   - Register a new user
   - Check if data persists
   - Try CRUD operations

---

## Free Tier Limitations

**Be aware of:**

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Backend sleeps after 15 min | 30s cold start | Use UptimeRobot |
| 512 MB RAM | ~50 concurrent users | Upgrade to $7/mo |
| 0.5 GB database | ~10,000 leads | Upgrade to $19/mo |
| 750 hours/month | Can't run 24/7 with multiple services | Use only 1 backend |

**When to upgrade:**
- More than 100 daily active users
- Need faster response times (no cold starts)
- Database > 0.5 GB
- Need background workers

---

## Upgrading from FREE

When you outgrow free tier:

### Render Upgrade ($7/month)
- 24/7 uptime (no sleeping)
- 512 MB RAM
- Faster cold starts
- Priority support

### Neon Upgrade ($19/month)
- 3 GB storage
- More compute units
- Point-in-time recovery
- Better performance

### Vercel (Stay FREE)
- Free tier is very generous
- Only upgrade if you need:
  - More bandwidth (>100 GB/mo)
  - Team features
  - Advanced analytics

**Total after upgrade: ~$26/month**

---

## Alternative FREE Combinations

### Option 1: Railway (All-in-One)
- **Backend:** Railway ($5 free credit)
- **Frontend:** Railway (included)
- **Database:** Railway PostgreSQL (included)
- **Pros:** Everything in one place
- **Cons:** Credit runs out after ~1 month

### Option 2: Fly.io
- **Backend:** Fly.io (3 VMs free)
- **Frontend:** Vercel (free)
- **Database:** Fly.io Postgres (free)
- **Pros:** More control, better performance
- **Cons:** More complex setup

### Option 3: Oracle Cloud (Advanced)
- **Backend:** Oracle Cloud VM (free forever)
- **Frontend:** Vercel (free)
- **Database:** Oracle Cloud (free)
- **Pros:** Most generous free tier (4 CPUs, 24 GB RAM)
- **Cons:** Complex setup, requires credit card

---

## Troubleshooting

### Backend won't start

**Check logs:**
1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for errors

**Common issues:**
- Missing environment variables
- Database connection failed
- Port binding error

**Fix:**
```bash
# In Render Shell
python -m app.main
# Check error messages
```

### Frontend shows blank page

**Check:**
1. Browser console for errors (F12)
2. Verify `VITE_API_URL` is correct
3. Check if backend is running

**Fix:**
```bash
# Rebuild frontend locally
cd frontend
npm run build

# Redeploy to Vercel
vercel --prod
```

### Database connection errors

**Check:**
1. Verify `DATABASE_URL` in Render environment variables
2. Test connection:
   ```bash
   # In Render Shell
   python
   >>> from app.database import engine
   >>> engine.connect()
   ```

**Fix:**
- Ensure `?sslmode=require` is in connection string
- Check Neon dashboard for database status

### Backend keeps sleeping

**Check:**
1. UptimeRobot is active
2. Monitor interval is 5 minutes
3. URL is correct

**Fix:**
- Reduce interval to 5 minutes
- Add multiple monitors
- Consider upgrading to paid tier ($7/mo)

### API calls failing (CORS errors)

**Check:**
1. Backend logs for CORS errors
2. Verify frontend URL is allowed

**Fix:**
Add to `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoring Your FREE Deployment

### UptimeRobot Dashboard
- Check uptime percentage
- View response times
- Get downtime alerts

### Render Dashboard
- View logs in real-time
- Monitor CPU/RAM usage
- Check deployment history

### Neon Dashboard
- Monitor database size
- View query performance
- Check connection count

### Vercel Analytics (FREE)
- Page views
- Unique visitors
- Performance metrics

---

## Backup Strategy (FREE)

### Database Backups

**Neon automatic backups:**
- Daily backups (retained 7 days)
- Point-in-time recovery (paid feature)

**Manual backups:**
```bash
# From your local machine
pg_dump "postgresql://user:pass@ep-xxx.neon.tech/neondb" > backup.sql

# Schedule with cron (Linux/Mac)
crontab -e
# Add: 0 2 * * * pg_dump "your-db-url" > ~/backups/backup_$(date +\%Y\%m\%d).sql
```

### Code Backups

Keep local copies:
```bash
# Zip your project
zip -r localai-leads-backup.zip .

# Or use rsync
rsync -av /path/to/project /path/to/backup
```

---

## Performance Optimization (FREE)

### Backend Optimization

1. **Reduce cold start time:**
   - Keep dependencies minimal
   - Use UptimeRobot to prevent sleep

2. **Optimize database queries:**
   - Add indexes (already included)
   - Use connection pooling

3. **Enable caching:**
   ```python
   # In app/main.py
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.inmemory import InMemoryBackend
   
   @app.on_event("startup")
   async def startup():
       FastAPICache.init(InMemoryBackend())
   ```

### Frontend Optimization

1. **Already optimized:**
   - Code splitting (Vite)
   - Minification
   - Tree shaking
   - Gzip compression (Vercel)

2. **Additional optimizations:**
   - Lazy load routes
   - Optimize images
   - Use CDN (Vercel provides)

---

## Security Checklist

- [x] HTTPS enabled (automatic)
- [x] Environment variables secured
- [x] Database uses SSL
- [x] CORS configured
- [ ] Change default SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable rate limiting
- [ ] Setup monitoring alerts
- [ ] Regular backups
- [ ] Keep dependencies updated

---

## Cost Breakdown

### Current (FREE)
```
Backend (Render):        $0/mo
Frontend (Vercel):       $0/mo
Database (Neon):         $0/mo
Domain (DuckDNS):        $0/mo
SSL (Automatic):         $0/mo
Monitoring (UptimeRobot): $0/mo
─────────────────────────────
Total:                   $0/mo 🎉
```

### After Upgrade (Production)
```
Backend (Render):        $7/mo
Frontend (Vercel):       $0/mo (stay free)
Database (Neon):         $19/mo
Domain (Namecheap):      $1/mo
SSL (Automatic):         $0/mo
Monitoring (UptimeRobot): $0/mo (stay free)
─────────────────────────────
Total:                   $27/mo
```

---

## Next Steps

1. **Test everything thoroughly**
2. **Add your content and data**
3. **Invite users to test**
4. **Monitor performance**
5. **Plan for scaling when needed**

---

## Getting Help

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com

**Vercel Support:**
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

**Neon Support:**
- Docs: https://neon.tech/docs
- Discord: https://discord.gg/neon

**Platform Issues:**
- Check logs first
- Search error messages
- Ask in relevant community forums

---

## Success! 🚀

You've successfully deployed your LocalAI Leads platform for FREE!

Your platform is now:
- ✅ Live and accessible
- ✅ Secured with HTTPS
- ✅ Backed by PostgreSQL
- ✅ Monitored 24/7
- ✅ Costing $0/month

**Share your deployment:**
- Frontend: `https://your-project.vercel.app`
- API Docs: `https://localai-backend.onrender.com/docs`

Happy deploying! 🎉
