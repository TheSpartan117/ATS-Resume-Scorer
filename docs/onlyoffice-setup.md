# OnlyOffice Document Server Integration Setup Guide

This guide explains how to set up and use OnlyOffice Document Server Community Edition for 100% Word-like editing in the ATS Resume Scorer application.

## Overview

OnlyOffice Document Server provides a professional document editing experience with:
- **100% Word compatibility** - Zero format discrepancy
- **Rich editing features** - All Microsoft Word features available
- **Real-time collaboration** - Multiple users can edit simultaneously
- **Auto-save** - Changes are automatically saved
- **Secure** - JWT token-based authentication

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│                 │      │                  │      │                     │
│  React Frontend │─────▶│  FastAPI Backend │─────▶│  OnlyOffice Server  │
│  (Port 3000)    │      │  (Port 8000)     │      │  (Port 8080)        │
│                 │      │                  │      │                     │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
        │                         │                          │
        │                         │                          │
        └──────────  JWT Auth  ───┴──────────────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- Minimum 2GB RAM available for Docker

## Installation

### 1. Start OnlyOffice Document Server

From the project root directory:

```bash
# Start OnlyOffice in detached mode
docker-compose up -d

# Check if OnlyOffice is running
docker-compose ps

# View OnlyOffice logs
docker-compose logs -f onlyoffice-documentserver
```

**Wait for initialization**: First startup takes 2-3 minutes as OnlyOffice initializes.

**Verify installation**: Open http://localhost:8080/welcome in your browser. You should see the OnlyOffice welcome page.

### 2. Install Backend Dependencies

```bash
cd backend

# Install Python dependencies (includes PyJWT and httpx)
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create or update `.env` file in the project root:

```bash
# OnlyOffice Configuration
ONLYOFFICE_SERVER_URL=http://localhost:8080
ONLYOFFICE_JWT_SECRET=your-secret-key-change-in-production
BACKEND_URL=http://localhost:8000

# CORS Configuration (include OnlyOffice server)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

**Important**: Change `ONLYOFFICE_JWT_SECRET` to a strong random string in production!

### 4. Start Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 5. Start Frontend Development Server

```bash
cd frontend
npm install
npm run dev
```

The application should now be running at http://localhost:3000 (or http://localhost:5173 with Vite).

## Usage

### Uploading and Editing Documents

1. **Upload a Resume**: Go to the home page and upload a DOCX file
2. **Navigate to Editor**: Click "Edit Resume" or navigate to `/editor`
3. **Select OnlyOffice Tab**: The OnlyOffice Editor tab is now the default
4. **Edit Document**: Use familiar Word-like interface to edit your resume
5. **Auto-save**: Changes are automatically saved every few seconds

### Tab Options

The editor provides multiple viewing/editing modes:

- **OnlyOffice Editor** (Default): 100% Word-compatible editing
- **Preview**: View original document with docx-preview
- **Structure Editor**: TipTap rich text editor (fallback)

### API Endpoints

The integration adds the following endpoints:

#### `POST /api/onlyoffice/config/{session_id}`
Generate OnlyOffice editor configuration with JWT token.

**Response:**
```json
{
  "documentType": "word",
  "document": {
    "fileType": "docx",
    "key": "unique-document-key",
    "title": "resume.docx",
    "url": "http://localhost:8000/api/onlyoffice/download/session123",
    "permissions": { "edit": true, "download": true, ... }
  },
  "editorConfig": {
    "callbackUrl": "http://localhost:8000/api/onlyoffice/callback",
    "mode": "edit",
    "user": { "id": "user123", "name": "User" }
  },
  "token": "jwt-token-here"
}
```

#### `GET /api/onlyoffice/download/{session_id}`
Serve document file for OnlyOffice to load.

#### `POST /api/onlyoffice/callback`
Handle document save callbacks from OnlyOffice.

**Callback Status Codes:**
- `1`: Document is being edited
- `2`: Document is ready for saving
- `3`: Document saving error
- `4`: Document closed with no changes
- `6`: Document being edited, user left
- `7`: Force save error

#### `POST /api/onlyoffice/upload/{session_id}`
Upload a new document for editing.

#### `GET /api/onlyoffice/health`
Check OnlyOffice server health.

## Docker Commands

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

### Restart OnlyOffice
```bash
docker-compose restart onlyoffice-documentserver
```

### Remove Volumes (Clean Reset)
```bash
docker-compose down -v
```

## Troubleshooting

### OnlyOffice not loading

**Problem**: Editor shows "Failed to load OnlyOffice Document Server"

**Solutions**:
1. Check if Docker is running: `docker ps`
2. Check if OnlyOffice container is up: `docker-compose ps`
3. Verify port 8080 is accessible: `curl http://localhost:8080/welcome`
4. Check container logs: `docker-compose logs onlyoffice-documentserver`
5. Restart container: `docker-compose restart`

### JWT Token Errors

**Problem**: "Invalid token" errors in logs

**Solutions**:
1. Verify `ONLYOFFICE_JWT_SECRET` matches in `.env` and `docker-compose.yml`
2. Ensure JWT_ENABLED=true in docker-compose.yml
3. Check backend logs for JWT generation errors
4. Restart both backend and OnlyOffice after changing secrets

### Document Not Saving

**Problem**: Changes are not persisted

**Solutions**:
1. Check callback URL is accessible from OnlyOffice container
2. Verify backend receives callback: check logs for "Received callback"
3. Ensure `backend/data/` directory is writable
4. Check network connectivity between containers

### Port Conflicts

**Problem**: Port 8080 already in use

**Solutions**:
1. Stop other services using port 8080
2. Change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8081:80"  # Use 8081 instead
   ```
3. Update `ONLYOFFICE_SERVER_URL` in `.env` accordingly
4. Update frontend component to use new port

### Memory Issues

**Problem**: OnlyOffice container crashes or is slow

**Solutions**:
1. Increase Docker memory limit (Docker Desktop settings)
2. Close other applications to free up RAM
3. Restart Docker daemon
4. Check system resources: `docker stats`

## Security Considerations

### Production Deployment

For production environments:

1. **Change JWT Secret**:
   ```bash
   # Generate strong random secret
   openssl rand -base64 32
   ```

2. **Use HTTPS**:
   - Deploy OnlyOffice behind HTTPS reverse proxy
   - Update `ONLYOFFICE_SERVER_URL` to use https://

3. **Restrict CORS**:
   ```env
   CORS_ORIGINS=https://yourdomain.com
   ```

4. **Add Authentication**:
   - Integrate with your user authentication system
   - Pass real user IDs to OnlyOffice config

5. **Network Isolation**:
   - Use Docker networks to isolate OnlyOffice
   - Don't expose port 8080 publicly

6. **Monitor Resources**:
   - Set up container resource limits
   - Monitor memory and CPU usage

## Advanced Configuration

### Custom Fonts

Add custom fonts to OnlyOffice:

```yaml
volumes:
  - ./custom-fonts:/usr/share/fonts/truetype/custom
```

### Redis for Clustering

For high-availability setup:

```yaml
services:
  redis:
    image: redis:alpine

  onlyoffice-documentserver:
    environment:
      - REDIS_SERVER_HOST=redis
      - REDIS_SERVER_PORT=6379
```

### PostgreSQL Storage

Use PostgreSQL for document metadata:

```yaml
services:
  postgres:
    image: postgres:13

  onlyoffice-documentserver:
    environment:
      - DB_TYPE=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
```

## File Storage

Documents are stored in:
- **Backend**: `backend/data/` directory
- **OnlyOffice**: Docker volumes (managed by Docker)

### Volume Management

View volumes:
```bash
docker volume ls | grep onlyoffice
```

Backup volumes:
```bash
docker run --rm -v onlyoffice_data:/data -v $(pwd):/backup alpine tar czf /backup/onlyoffice-backup.tar.gz /data
```

Restore volumes:
```bash
docker run --rm -v onlyoffice_data:/data -v $(pwd):/backup alpine tar xzf /backup/onlyoffice-backup.tar.gz -C /
```

## Performance Optimization

### Recommended Settings

1. **Auto-save interval**: 5 seconds (default)
2. **Force-save**: Enabled for data integrity
3. **Connection timeout**: 30 seconds

### Scaling

For high-traffic scenarios:
- Deploy multiple OnlyOffice instances behind load balancer
- Use shared Redis for session management
- Implement document service clustering

## Migration from TipTap

The OnlyOffice integration **replaces** the TipTap editor as the default. However:
- TipTap remains available as "Structure Editor" fallback
- Preview tab still uses docx-preview
- All existing features remain functional

## Support and Resources

### Documentation
- [OnlyOffice Docs](https://api.onlyoffice.com/editors/basic)
- [Docker Hub](https://hub.docker.com/r/onlyoffice/documentserver)
- [GitHub Repository](https://github.com/ONLYOFFICE/DocumentServer)

### Community
- [OnlyOffice Forum](https://forum.onlyoffice.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/onlyoffice)

### License
- Community Edition is **free** and open-source (AGPL v3)
- No restrictions on number of connections
- Commercial support available separately

## Testing

### Health Check
```bash
curl http://localhost:8000/api/onlyoffice/health
```

Expected response:
```json
{
  "status": "healthy",
  "onlyoffice_server": "http://localhost:8080",
  "message": "OnlyOffice Document Server is accessible"
}
```

### Test Document Upload
```bash
curl -X POST http://localhost:8000/api/onlyoffice/upload/test123 \
  --data-binary @sample.docx
```

### Test Config Generation
```bash
curl -X POST http://localhost:8000/api/onlyoffice/config/test123
```

## Uninstall

To completely remove OnlyOffice:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all documents)
docker-compose down -v

# Remove images
docker rmi onlyoffice/documentserver:latest

# Remove backend integration
rm backend/api/onlyoffice.py
rm docs/onlyoffice-setup.md
```

## Changelog

### Version 1.0.0 (2026-02-20)
- Initial OnlyOffice integration
- JWT authentication support
- Auto-save and callback handling
- Docker Compose configuration
- Frontend component with error handling
- Complete documentation

---

**Need Help?** Check the troubleshooting section or contact support.
