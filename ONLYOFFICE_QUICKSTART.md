# OnlyOffice Quick Start Guide

Get OnlyOffice Document Server running in 5 minutes!

## What is OnlyOffice?

OnlyOffice provides **100% Microsoft Word-compatible** editing for your ATS Resume Scorer application. Unlike other editors, OnlyOffice preserves all formatting, styles, and document structure with **zero discrepancy**.

## Quick Setup

### Step 1: Start OnlyOffice (30 seconds)

```bash
# From project root
docker-compose up -d
```

Wait 2-3 minutes for first-time initialization, then verify at: http://localhost:8080/welcome

### Step 2: Install Dependencies (1 minute)

```bash
# Backend dependencies
cd backend
pip install pyjwt==2.8.0 httpx==0.26.0

# Frontend is already configured - no additional packages needed
```

### Step 3: Configure Environment (30 seconds)

Create `.env` file in project root:

```bash
ONLYOFFICE_SERVER_URL=http://localhost:8080
ONLYOFFICE_JWT_SECRET=change-this-secret-in-production
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

### Step 4: Start Application (1 minute)

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 5: Test It! (1 minute)

1. Open http://localhost:3000 (or http://localhost:5173)
2. Upload a DOCX resume
3. Click "Edit Resume"
4. **OnlyOffice Editor tab is now the default!**
5. Edit your document with full Word features

## Features You Get

✅ **100% Word Compatibility** - All formatting preserved
✅ **Rich Editing** - All Microsoft Word features
✅ **Auto-Save** - Changes saved automatically
✅ **Track Changes** - Review mode available
✅ **Comments** - Add comments to documents
✅ **Print & Download** - Full document control
✅ **No Format Loss** - Zero discrepancy guarantee

## Common Commands

### Start OnlyOffice
```bash
docker-compose up -d
```

### Stop OnlyOffice
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f onlyoffice-documentserver
```

### Check Status
```bash
# Check if running
docker-compose ps

# Check health
curl http://localhost:8000/api/onlyoffice/health
```

### Restart (if needed)
```bash
docker-compose restart onlyoffice-documentserver
```

## Troubleshooting

### OnlyOffice Not Loading?

**Check if Docker is running:**
```bash
docker ps
```

**Verify OnlyOffice is up:**
```bash
docker-compose ps
curl http://localhost:8080/welcome
```

**View logs for errors:**
```bash
docker-compose logs onlyoffice-documentserver
```

**Restart everything:**
```bash
docker-compose down
docker-compose up -d
# Wait 2-3 minutes
```

### Port 8080 Already in Use?

Change port in `docker-compose.yml`:
```yaml
ports:
  - "8081:80"  # Use 8081 instead
```

Update `.env`:
```bash
ONLYOFFICE_SERVER_URL=http://localhost:8081
```

### Editor Shows Error?

1. Ensure all three services are running:
   - OnlyOffice (port 8080)
   - Backend (port 8000)
   - Frontend (port 3000 or 5173)

2. Check browser console for specific errors

3. Verify backend logs show no JWT errors

4. Try the fallback editors (Preview or Structure Editor tabs)

## File Locations

- **Configuration**: `docker-compose.yml`
- **Backend API**: `backend/api/onlyoffice.py`
- **Frontend Component**: `frontend/src/components/OnlyOfficeEditor.tsx`
- **Documentation**: `docs/onlyoffice-setup.md`
- **Documents Storage**: `backend/data/`

## How It Works

```
1. Upload DOCX → Stored in backend/data/
2. Open Editor → Frontend requests config from backend
3. Backend generates JWT token → Secure access
4. OnlyOffice loads document → Full Word interface
5. Edit document → Real-time editing
6. Auto-save → OnlyOffice sends callbacks to backend
7. Backend saves changes → Document updated
```

## Integration Overview

The OnlyOffice integration adds:

**Backend (`backend/api/onlyoffice.py`):**
- `/api/onlyoffice/config/{session_id}` - Generate editor config
- `/api/onlyoffice/callback` - Handle save callbacks
- `/api/onlyoffice/download/{session_id}` - Serve documents
- `/api/onlyoffice/upload/{session_id}` - Upload documents
- `/api/onlyoffice/health` - Health check

**Frontend (`frontend/src/components/OnlyOfficeEditor.tsx`):**
- Embeds OnlyOffice Document Editor
- Handles loading states
- Error recovery with fallbacks
- Auto-connects to backend

**Editor Page Updates:**
- OnlyOffice tab is now **default**
- Previous editors still available as fallbacks
- Seamless tab switching

## Production Deployment

For production:

1. **Generate strong JWT secret:**
   ```bash
   openssl rand -base64 32
   ```

2. **Use HTTPS:**
   ```bash
   ONLYOFFICE_SERVER_URL=https://onlyoffice.yourdomain.com
   ```

3. **Restrict CORS:**
   ```bash
   CORS_ORIGINS=https://yourdomain.com
   ```

4. **Add authentication:**
   - Integrate with your auth system
   - Pass real user IDs

See `docs/onlyoffice-setup.md` for complete production setup guide.

## Getting Help

- **Full Documentation**: `docs/onlyoffice-setup.md`
- **OnlyOffice Docs**: https://api.onlyoffice.com/editors/basic
- **Docker Issues**: Check `docker-compose logs`
- **Backend Issues**: Check backend console logs
- **Frontend Issues**: Check browser developer console

## Next Steps

1. ✅ Follow this quick start
2. 📖 Read full documentation in `docs/onlyoffice-setup.md`
3. 🔒 Configure production security settings
4. 🚀 Deploy to production

---

**Success?** You should now see the OnlyOffice Editor tab as default when editing resumes!

**Having issues?** Check the Troubleshooting section above or read the full documentation.
