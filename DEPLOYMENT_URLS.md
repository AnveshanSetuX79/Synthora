# Deployment URLs

## Backend (API)
- **URL:** https://synthora-bvfl.onrender.com
- **API Docs:** https://synthora-bvfl.onrender.com/docs
- **Health Check:** https://synthora-bvfl.onrender.com/api/health

## Frontend
- **Status:** Not yet deployed
- **Recommended:** Deploy to Vercel.com

## Next Steps

### 1. Test Your Backend
Visit: https://synthora-bvfl.onrender.com/docs

You should see the FastAPI documentation page with all your API endpoints.

### 2. Deploy Frontend to Vercel

**Quick Deploy:**

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "Add New..." → "Project"
3. Upload your `frontend` folder or connect GitHub
4. Add environment variables:
   ```
   VITE_API_URL=https://synthora-bvfl.onrender.com
   VITE_RAZORPAY_KEY_ID=your_razorpay_key_id
   ```
5. Click "Deploy"

**Or build and deploy manually:**

```bash
cd frontend

# Update .env file (already done)
# VITE_API_URL=https://synthora-bvfl.onrender.com

# Install dependencies
npm install

# Build for production
npm run build

# Deploy the dist folder to Vercel
npx vercel --prod
```

### 3. Update Backend CORS Settings

After deploying frontend, you need to allow your frontend URL in the backend.

In your backend code (`backend/app/main.py`), update CORS origins to include your Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",  # Add your Vercel URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Keep Backend Awake (Important!)

Render free tier sleeps after 15 minutes. Set up UptimeRobot:

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Create free account
3. Add monitor:
   - Type: HTTP(s)
   - URL: `https://synthora-bvfl.onrender.com/api/health`
   - Interval: 5 minutes

This keeps your backend awake 24/7.

### 5. Create Admin User

Once backend is running, create an admin user:

**Method 1: Using Render Shell**
1. Go to Render dashboard
2. Click your service → "Shell" tab
3. Run:
   ```bash
   python scripts/create_admin_user.py
   ```

**Method 2: Using API**
1. Go to https://synthora-bvfl.onrender.com/docs
2. Find `/api/auth/register` endpoint
3. Click "Try it out"
4. Register with admin credentials

## Environment Variables Reference

### Backend (Render)
```env
DATABASE_URL=your_neon_database_url
SECRET_KEY=your_secret_key
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
GOOGLE_PLACES_API_KEY=your_google_api_key
SMS_ENABLED=true
MSG91_AUTH_KEY=your_msg91_key
# ... other variables
```

### Frontend (Vercel)
```env
VITE_API_URL=https://synthora-bvfl.onrender.com
VITE_RAZORPAY_KEY_ID=your_razorpay_key_id
```

## Troubleshooting

### Backend not responding
- Check Render logs
- Verify environment variables are set
- Check database connection

### Frontend can't connect to backend
- Verify VITE_API_URL is correct
- Check CORS settings in backend
- Check browser console for errors

### Database errors
- Run migrations: `alembic upgrade head`
- Check DATABASE_URL is correct
- Verify database is accessible

## Cost Summary

```
Backend (Render Free):     $0/mo
Frontend (Vercel Free):    $0/mo
Database (Neon Free):      $0/mo
Monitoring (UptimeRobot):  $0/mo
─────────────────────────────────
Total:                     $0/mo 🎉
```

## Support

- Backend URL: https://synthora-bvfl.onrender.com
- API Docs: https://synthora-bvfl.onrender.com/docs
- Render Dashboard: https://dashboard.render.com
