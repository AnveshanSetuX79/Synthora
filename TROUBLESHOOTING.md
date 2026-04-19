# Troubleshooting Deployment Issues

## Your Deployment URLs

- **Frontend:** https://synthora-nu.vercel.app
- **Backend:** https://synthora-bvfl.onrender.com
- **API Docs:** https://synthora-bvfl.onrender.com/docs

## Common Issues & Solutions

### 1. Frontend Shows Blank Page

**Check:**
1. Open browser console (F12 → Console tab)
2. Look for errors

**Common causes:**
- API connection issues
- JavaScript errors
- Missing environment variables

**Fix:**
```bash
# Verify Vercel environment variables are set:
VITE_API_URL=https://synthora-bvfl.onrender.com
VITE_RAZORPAY_KEY_ID=your_key
```

### 2. Backend Not Responding (Cold Start)

Render free tier sleeps after 15 minutes.

**Symptoms:**
- First request takes 30-60 seconds
- "Service Unavailable" error

**Fix:**
- Wait 30-60 seconds for backend to wake up
- Setup UptimeRobot to keep it awake (see below)

**Test backend:**
Visit: https://synthora-bvfl.onrender.com/docs

### 3. CORS Errors

**Symptoms:**
Browser console shows:
```
Access to fetch at 'https://synthora-bvfl.onrender.com/api/...' 
from origin 'https://synthora-nu.vercel.app' has been blocked by CORS policy
```

**Fix:**
Update `backend/app/main.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://synthora-nu.vercel.app",  # Add your Vercel URL
        "*"  # Or allow all for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push and redeploy backend.

### 4. API Calls Failing

**Check:**
1. Open browser console (F12 → Network tab)
2. Look for failed requests (red)
3. Click on failed request to see details

**Common issues:**
- Wrong API URL in frontend
- Backend is sleeping
- CORS not configured
- Missing authentication

**Fix:**
1. Verify `VITE_API_URL` in Vercel environment variables
2. Check backend logs in Render dashboard
3. Test API directly: https://synthora-bvfl.onrender.com/docs

### 5. Database Connection Errors

**Symptoms:**
- Backend logs show database errors
- 500 Internal Server Error

**Check:**
1. Go to Render dashboard → Your service → Logs
2. Look for database connection errors

**Fix:**
1. Verify `DATABASE_URL` in Render environment variables
2. Check Neon database is running
3. Run migrations:
   ```bash
   # In Render Shell
   alembic upgrade head
   ```

### 6. Environment Variables Not Set

**Frontend (Vercel):**
1. Go to Vercel project → Settings → Environment Variables
2. Add:
   ```
   VITE_API_URL=https://synthora-bvfl.onrender.com
   VITE_RAZORPAY_KEY_ID=your_key
   ```
3. Redeploy

**Backend (Render):**
1. Go to Render service → Environment
2. Verify all variables are set (see DEPLOYMENT_URLS.md)
3. Redeploy if changed

## Quick Diagnostic Steps

### Step 1: Test Backend
```bash
curl https://synthora-bvfl.onrender.com/api/health
```

Expected response:
```json
{"status": "healthy"}
```

If this fails, backend is down or sleeping.

### Step 2: Test Frontend
Visit: https://synthora-nu.vercel.app

**If blank page:**
- Open console (F12)
- Check for errors
- Look at Network tab for failed requests

### Step 3: Test API Connection
1. Visit frontend
2. Try to login or register
3. Check Network tab for API calls
4. If CORS error → Fix CORS settings
5. If 404 → Check API URL
6. If timeout → Backend is sleeping

## Setup UptimeRobot (Keep Backend Awake)

**Free solution to prevent backend from sleeping:**

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up (free)
3. Add New Monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://synthora-bvfl.onrender.com/api/health`
   - **Interval:** 5 minutes
4. Save

This pings your backend every 5 minutes, keeping it awake 24/7.

## Check Deployment Status

### Vercel
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click your project
3. Check latest deployment status
4. View logs if failed

### Render
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click your service
3. Check "Logs" tab for errors
4. Check "Events" tab for deployment history

## Common Error Messages

### "Failed to fetch"
- Backend is down or sleeping
- CORS issue
- Wrong API URL

**Fix:** Wait for backend to wake up, check CORS

### "Network Error"
- Backend not accessible
- Wrong URL
- Firewall blocking

**Fix:** Verify backend URL, test with curl

### "401 Unauthorized"
- Not logged in
- Token expired
- Invalid credentials

**Fix:** Login again

### "500 Internal Server Error"
- Backend error
- Database connection issue
- Missing environment variable

**Fix:** Check Render logs

## Still Not Working?

### 1. Check Render Logs
```
Render Dashboard → Your Service → Logs
```
Look for:
- Startup errors
- Database connection errors
- Missing environment variables

### 2. Check Vercel Logs
```
Vercel Dashboard → Your Project → Deployments → Latest → View Function Logs
```

### 3. Check Browser Console
```
F12 → Console tab
```
Look for:
- JavaScript errors
- CORS errors
- Failed API calls

### 4. Test Locally
```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

If it works locally but not in production:
- Environment variables issue
- CORS configuration
- Build configuration

## Get Help

**Share these details:**
1. Frontend URL and what you see
2. Backend URL and response
3. Browser console errors (F12 → Console)
4. Network tab errors (F12 → Network)
5. Render logs (if backend issue)

## Quick Fixes Checklist

- [ ] Backend is running (visit /docs)
- [ ] Frontend deployed successfully
- [ ] Environment variables set in Vercel
- [ ] Environment variables set in Render
- [ ] CORS configured with frontend URL
- [ ] Database migrations ran
- [ ] UptimeRobot monitoring setup
- [ ] Browser console shows no errors
- [ ] Network tab shows successful API calls

## Performance Tips

### Frontend
- Already optimized with code splitting
- Uses CDN (Vercel)
- Gzip compression enabled

### Backend
- Increase workers if needed (costs money)
- Setup Redis caching (optional)
- Use connection pooling (already configured)

### Database
- Add indexes (already done)
- Monitor query performance in Neon dashboard
- Upgrade if > 0.5 GB

## Monitoring

**Free tools:**
- UptimeRobot: Uptime monitoring
- Vercel Analytics: Page views, performance
- Render Metrics: CPU, RAM usage
- Neon Dashboard: Database size, queries

## Need to Rollback?

### Vercel
1. Go to Deployments
2. Find working deployment
3. Click "..." → "Promote to Production"

### Render
1. Go to Events tab
2. Find working deployment
3. Click "Rollback"

---

**Most Common Issue:** Backend sleeping on first request. Wait 30-60 seconds or setup UptimeRobot.
