# ATS Resume Scorer - Runbook

Operations guide for deploying, monitoring, and troubleshooting the ATS Resume Scorer application in production.

## Quick Start

### Health Checks

```bash
# Backend health
curl https://your-backend.com/health
# Expected: {"status": "healthy"}

# API status
curl https://your-backend.com/api/roles
# Expected: {"categories": [...], "levels": [...]}

# Frontend (browser)
https://your-frontend.com/
# Should load upload page within 5 seconds
```

### Status Dashboard
- **Frontend**: https://vercel.com/dashboard (Vercel)
- **Backend**: https://render.com/dashboard (Render)
- **Database**: https://supabase.com/dashboard (Supabase)

---

## Deployment Guide

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Vercel)                    │
│         React 19 + Vite + TypeScript + Tailwind          │
│              URL: https://your-app.vercel.app            │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
                       ↓
┌─────────────────────────────────────────────────────────┐
│                    Backend (Render)                      │
│         FastAPI + Python 3.11 + SQLAlchemy               │
│            URL: https://your-backend.onrender.com        │
└──────────────────────┬──────────────────────────────────┘
                       │ TCP
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Database (Supabase)                     │
│         PostgreSQL 14+ with Alembic migrations           │
└─────────────────────────────────────────────────────────┘
```

### Backend Deployment (Render)

#### Step 1: Repository Setup
1. Push code to GitHub (main branch)
2. Ensure `backend/Dockerfile` exists
3. Ensure `backend/requirements.txt` is current

#### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `ats-resume-scorer-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Plan**: Standard (or Starter for testing)

#### Step 3: Environment Variables
Add these in Render dashboard (Settings → Environment):

```
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
JWT_SECRET_KEY=<generate-32-char-hex-string>
ONLYOFFICE_JWT_SECRET=<generate-32-char-hex-string>
ONLYOFFICE_SERVER_URL=<your-onlyoffice-server-or-skip>
CORS_ORIGINS=https://your-app.vercel.app
BACKEND_URL=https://your-backend.onrender.com
ENVIRONMENT=production
MAX_FILE_SIZE_MB=50
ENABLE_SEMANTIC_MATCHING=false
```

**Generating Secrets:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 4: Deploy
1. Click "Deploy"
2. Wait for build to complete (~3-5 min)
3. Check logs for errors
4. Test health endpoint: `https://your-backend.onrender.com/health`

#### Step 5: Set Up PostgreSQL Database
Option A: Use Supabase (recommended)
- Create account at [supabase.com](https://supabase.com)
- Create new project (PostgreSQL 14+)
- Copy connection string to `DATABASE_URL`
- Run migrations (see below)

Option B: Use Render Database
- In Render, add PostgreSQL service
- Link to backend service
- Render will provide `DATABASE_URL`

#### Step 6: Run Database Migrations
```bash
# Option 1: Via Render CLI
render run "alembic upgrade head"

# Option 2: SSH into Render
# (Use Render dashboard → Shell)
cd /opt/render/project && alembic upgrade head
```

### Frontend Deployment (Vercel)

#### Step 1: Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import GitHub repository
4. Select `frontend` directory as root

#### Step 2: Configure Build
- **Framework**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm ci`

#### Step 3: Environment Variables
Add in Vercel dashboard (Settings → Environment Variables):

```
VITE_API_URL=https://your-backend.onrender.com
```

#### Step 4: Deploy
1. Click "Deploy"
2. Wait for build (~2 min)
3. Test frontend: https://your-app.vercel.app
4. Verify API connection: Open DevTools Console (should see API calls)

### Database Setup (Supabase)

#### Step 1: Create Project
1. Go to [supabase.com](https://supabase.com)
2. Create new organization
3. Create new project
4. Save credentials

#### Step 2: Get Connection String
1. Project Settings → Database
2. Copy "Connection string" (URI format)
3. Use in backend `DATABASE_URL`

#### Step 3: Run Migrations
```bash
# Download connection string from Supabase
# Run from local machine
cd backend
PGPASSWORD=your_password psql -h db.supabase.co -U postgres -d postgres -f scripts/init_db.sql

# Or use Alembic
alembic upgrade head
```

#### Step 4: Create PostgreSQL Session Store Table
```sql
-- Run in Supabase SQL editor
CREATE TABLE IF NOT EXISTS session_store (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    data JSONB,
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_session_id ON session_store(session_id);
CREATE INDEX idx_expires_at ON session_store(expires_at);
```

---

## Monitoring & Alerts

### Backend Monitoring

#### Render Dashboard
- CPU/Memory usage
- Request rate
- Error rate
- Recent logs

#### Manual Health Checks
```bash
# Health endpoint (daily)
curl https://your-backend.onrender.com/health

# API connectivity (daily)
curl https://your-backend.onrender.com/api/roles

# Database connectivity (weekly)
curl https://your-backend.onrender.com/api/health
```

#### Key Metrics to Watch
- **Response time**: Should be <1s for most endpoints
- **Error rate**: Should be <1%
- **Database connections**: Should not max out
- **Disk usage**: Track file uploads

### Frontend Monitoring

#### Vercel Analytics
- Performance metrics
- Error rate
- Core Web Vitals
- Page load time

#### Manual Testing
```bash
# Test frontend loads
curl -I https://your-app.vercel.app/

# Test E2E smoke tests
npm run test:e2e:smoke -- --base-url https://your-app.vercel.app
```

### Database Monitoring

#### Supabase Dashboard
- Table sizes
- Connection pool status
- Query performance
- Backup status

---

## Common Issues & Solutions

### Backend Not Responding

**Symptoms**: `/health` returns 500 or timeout

**Diagnosis:**
```bash
# 1. Check Render logs
# Render Dashboard → Logs tab

# 2. Check if service is running
curl -i https://your-backend.onrender.com/health

# 3. Check environment variables
# Render Dashboard → Settings → Environment Variables
```

**Solutions:**
1. **Restart service**: Render Dashboard → Manual Deploy
2. **Check DATABASE_URL**: Verify PostgreSQL is running
3. **Check JWT_SECRET_KEY**: Must be set and ≥32 chars
4. **Review logs for specific errors**: Click "Log" in Render

### Database Connection Failed

**Symptoms**: "Database connection refused" in logs

**Diagnosis:**
```bash
# 1. Test database connection locally
psql 'postgresql://user:password@host/database'

# 2. Check connection string format
# Should be: postgresql://username:password@host:port/database

# 3. Check Supabase is accepting connections
# Supabase Dashboard → Project Settings → Database
```

**Solutions:**
1. Verify DATABASE_URL in environment variables
2. Ensure PostgreSQL service is running in Supabase
3. Reset Supabase password if connection still fails
4. Run migrations again: `alembic upgrade head`

### API Key/JWT Errors

**Symptoms**: "Invalid token" or "Unauthorized" responses

**Diagnosis:**
```bash
# 1. Check JWT_SECRET_KEY is set
# Render Dashboard → Environment Variables

# 2. Verify token expiration
# JWT tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30)
```

**Solutions:**
1. Regenerate JWT_SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Update in Render environment variables
3. Restart backend service
4. Test new token creation

### Frontend API Calls Failing

**Symptoms**: CORS errors in browser console

**Diagnosis:**
```
Access to XMLHttpRequest at 'https://api.example.com/'
from origin 'https://app.example.com' has been blocked by CORS policy
```

**Solutions:**
1. Add frontend URL to backend `CORS_ORIGINS`
2. Ensure `ENVIRONMENT=production` in backend
3. Restart backend service
4. Test with: `curl -H "Origin: https://app.example.com" -i https://api.example.com/`

### File Upload Failing

**Symptoms**: Upload returns 413 or "File too large"

**Diagnosis:**
1. Check file size: Should be <`MAX_FILE_SIZE_MB` (default: 10 MB)
2. Check file format: Must be PDF or DOCX
3. Check for magic bytes corruption

**Solutions:**
1. Increase `MAX_FILE_SIZE_MB` in environment variables (max recommended: 50)
2. Use correct file format
3. Try re-saving the file in Office/Adobe

### OnlyOffice Integration Not Working

**Symptoms**: Document editor shows blank or "Failed to open document"

**Diagnosis:**
1. Check `ONLYOFFICE_SERVER_URL` is set and reachable
2. Check `ONLYOFFICE_JWT_SECRET` is configured
3. Verify document is accessible at provided URL

**Solutions:**
1. Start OnlyOffice: `docker-compose up onlyoffice`
2. Verify URL is accessible: `curl http://onlyoffice:8080/`
3. Regenerate JWT secret
4. Check backend logs for JWT errors

---

## Scaling & Optimization

### When to Scale

Scale **backend** when:
- CPU usage consistently >70%
- Memory usage consistently >80%
- Database connection pool exhausted
- Response time >2 seconds

Scale **database** when:
- Connections hit pool limit
- Query performance degrades
- Disk space >80% full

Scale **frontend** when:
- Build time exceeds 5 minutes
- Static asset size exceeds 5 MB

### Optimization Tips

#### Backend
- Enable `ENABLE_SEMANTIC_MATCHING=false` (saves 200+ MB memory)
- Use connection pooling (SQLAlchemy): `pool_size=10, max_overflow=20`
- Cache role keywords and verb tiers
- Compress PDF parsing (reduce PDF page limits)

#### Database
- Create indexes on frequently queried columns
- Archive old sessions: Delete sessions older than 30 days
- Vacuum and analyze tables monthly

#### Frontend
- Enable Vercel analytics to track slow pages
- Use lazy loading for components
- Optimize images (Vercel does this automatically)

---

## Disaster Recovery

### Backup Strategy

#### Daily
- Supabase automatic backups (7-day retention)
- Git commits (source code)

#### Weekly
- Manual Supabase backup export (to cloud storage)
- Database schema dump

#### Monthly
- Full application backup
- Document recovery procedure

### Restore Procedures

#### Database Restore
```bash
# 1. Download backup from Supabase
# Supabase Dashboard → Backups tab

# 2. Restore locally (test first)
psql -U postgres < backup.sql

# 3. Restore to production
# Supabase → Backups → Restore (one-click)

# 4. Verify data
curl https://your-backend.onrender.com/api/roles
```

#### Code Rollback
```bash
# 1. Identify broken commit
git log --oneline

# 2. Revert locally
git revert <commit-hash>

# 3. Push to main
git push origin main

# 4. Render auto-redeploys
# Check status in Render Dashboard
```

#### Full Recovery
1. Restore database from Supabase backup
2. Redeploy backend: Manual Deploy in Render Dashboard
3. Redeploy frontend: Redeploy in Vercel Dashboard
4. Run smoke tests: `npm run test:e2e:smoke`

---

## Maintenance

### Weekly
- [ ] Check `/health` endpoint
- [ ] Review error logs
- [ ] Check database disk usage
- [ ] Monitor API response times

### Monthly
- [ ] Delete old sessions from database
- [ ] Review and rotate JWT secrets if needed
- [ ] Update dependencies (`pip`, `npm`)
- [ ] Backup database manually
- [ ] Test disaster recovery procedure

### Quarterly
- [ ] Security audit (dependencies, secrets)
- [ ] Performance optimization review
- [ ] Capacity planning check
- [ ] Documentation update

---

## Useful Commands

### Render CLI
```bash
# Deploy
render deploy --service-id <id>

# View logs
render logs --service-id <id>

# SSH into service
render connect --service-id <id>
```

### Database Access
```bash
# Connect to Supabase database
psql postgresql://user:password@db.supabase.co:5432/postgres

# List tables
\dt

# View session store
SELECT COUNT(*) FROM session_store;

# Delete expired sessions
DELETE FROM session_store WHERE expires_at < NOW();
```

### Frontend Testing
```bash
# Test deployment
npm run test:e2e:smoke -- --base-url https://your-app.vercel.app

# Generate test report
npm run test:e2e:report
```

---

## Contact & Escalation

**Alerting**: Set up Render alerts in dashboard:
- CPU >80%
- Memory >80%
- Errors >5% of requests

**Escalation Path**:
1. Check logs (Render/Supabase/Vercel)
2. Restart service (Manual Deploy)
3. Check recent commits (git log)
4. Restore from backup if data corruption
5. Create GitHub issue if persistent

**On-Call**: See repository README for maintainer contact info

---

**Last Updated**: March 2026
**Version**: 1.0
**Review Date**: April 2026
