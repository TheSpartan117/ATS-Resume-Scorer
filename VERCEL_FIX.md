# Vercel Deployment Fix

## Issue
The deployed frontend at https://ats-resume-scorer-omega.vercel.app/ has a typo in the API URL environment variable:
- **Wrong:** `ats-resume-scorer-ap.er.com/api/uploadii`
- **Correct:** `ats-resume-scorer-api.onrender.com/api/upload`

## Solution Applied

Created `frontend/.env.production` with the correct API URL:
```
VITE_API_URL=https://ats-resume-scorer-api.onrender.com
```

## How to Deploy the Fix

### Option 1: Automatic Deployment (Recommended)
1. Commit and push the new `.env.production` file:
   ```bash
   cd ats-resume-scorer
   git add frontend/.env.production VERCEL_FIX.md
   git commit -m "fix: correct API URL in production environment"
   git push origin main
   ```

2. Vercel will automatically detect the push and redeploy (if auto-deploy is enabled)

3. Verify the deployment at: https://ats-resume-scorer-omega.vercel.app/

### Option 2: Manual Vercel Environment Variable Update
1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: `ats-resume-scorer-omega`
3. Go to **Settings** → **Environment Variables**
4. Find `VITE_API_URL` and update it to:
   ```
   https://ats-resume-scorer-api.onrender.com
   ```
5. Go to **Deployments** tab
6. Click the three dots on the latest deployment → **Redeploy**

### Option 3: Redeploy via Vercel CLI
```bash
cd frontend
npm run build
vercel --prod
```

## Verification Steps

After redeploying, verify the fix:

1. **Check the deployed site:**
   ```bash
   curl -s https://ats-resume-scorer-omega.vercel.app/assets/index-*.js | grep -o "https://ats-resume-scorer-api.onrender.com"
   ```
   Should return the correct URL.

2. **Test file upload:**
   - Go to https://ats-resume-scorer-omega.vercel.app/
   - Upload a resume file
   - Should successfully upload without errors

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Should see API calls to `https://ats-resume-scorer-api.onrender.com/api/upload`
   - No more 422 errors or malformed URLs

## Root Cause

The typo was in Vercel's environment variable settings. Someone manually entered:
- `VITE_API_URL=https://ats-resume-scorer-ap.er.com`

Instead of:
- `VITE_API_URL=https://ats-resume-scorer-api.onrender.com`

By adding `.env.production` to the repository, future deployments will use the correct URL from the file instead of relying on manual environment variable entry.
