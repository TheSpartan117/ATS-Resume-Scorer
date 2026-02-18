# Deployment Documentation

## Overview

This guide covers deploying the ATS Resume Scorer API to production environments. The application is built with FastAPI and requires PostgreSQL, with optional LanguageTool integration for grammar checking.

---

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, Windows Server

### Recommended (Production)
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1Gbps+

---

## Dependencies

### Core Services

#### 1. PostgreSQL 14+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verify installation
psql --version  # Should be 14.x or higher

# Create database
sudo -u postgres psql
CREATE DATABASE ats_db;
CREATE USER ats_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ats_db TO ats_user;
\q
```

#### 2. Python 3.11+
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

#### 3. LanguageTool (Optional but Recommended)
```bash
# Option A: Docker (Recommended)
docker run -d -p 8081:8010 erikvl87/languagetool

# Option B: Standalone JAR
wget https://languagetool.org/download/LanguageTool-stable.zip
unzip LanguageTool-stable.zip
cd LanguageTool-6.3
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081

# Option C: Python library (bundled)
# No additional setup needed, but slower than server
```

**LanguageTool Configuration:**
- If using Docker/standalone server: Set `LANGUAGETOOL_URL=http://localhost:8081`
- If using Python library: Leave `LANGUAGETOOL_URL` unset
- To disable: Set `LANGUAGETOOL_ENABLED=false`

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/ats-resume-scorer.git
cd ats-resume-scorer/backend
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Requirements:**
```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
python-multipart==0.0.9
python-docx==1.1.0
reportlab==4.4.10
PyMuPDF==1.27.1
pypdf==4.0.1
pdfplumber==0.10.4
spacy==3.7.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pydantic==2.6.0
email-validator==2.3.0
slowapi==0.1.9
language-tool-python==2.7.1
selenium==4.15.2
webdriver-manager==4.0.1
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://ats_user:secure_password@localhost:5432/ats_db

# JWT Authentication
SECRET_KEY=your-secret-key-here-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production

# File Upload
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=pdf,docx
UPLOAD_DIR=/var/www/ats-resume-scorer/uploads

# LanguageTool (optional)
LANGUAGETOOL_ENABLED=true
LANGUAGETOOL_URL=http://localhost:8081
```

**Generate Secret Key:**
```bash
openssl rand -hex 32
```

### 5. Initialize Database
```bash
# Run migrations
alembic upgrade head

# Verify
python -c "from database import engine; print(engine.table_names())"
```

---

## Deployment Methods

### Method 1: Systemd Service (Recommended for Linux)

#### 1. Create Service File
```bash
sudo nano /etc/systemd/system/ats-api.service
```

```ini
[Unit]
Description=ATS Resume Scorer API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/ats-resume-scorer/backend
Environment="PATH=/var/www/ats-resume-scorer/backend/venv/bin"
EnvironmentFile=/var/www/ats-resume-scorer/backend/.env
ExecStart=/var/www/ats-resume-scorer/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/log/ats-api/access.log \
    --error-logfile /var/log/ats-api/error.log \
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Enable and Start Service
```bash
# Create log directory
sudo mkdir -p /var/log/ats-api
sudo chown www-data:www-data /var/log/ats-api

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable ats-api
sudo systemctl start ats-api

# Check status
sudo systemctl status ats-api

# View logs
sudo journalctl -u ats-api -f
```

### Method 2: Docker

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: ats_db
      POSTGRES_USER: ats_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

  languagetool:
    image: erikvl87/languagetool
    ports:
      - "8081:8010"
    restart: always

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://ats_user:secure_password@db:5432/ats_db
      SECRET_KEY: ${SECRET_KEY}
      LANGUAGETOOL_URL: http://languagetool:8010
      ENVIRONMENT: production
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      - db
      - languagetool
    restart: always

volumes:
  postgres_data:
```

#### 3. Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Stop services
docker-compose down
```

### Method 3: Cloud Platforms

#### AWS (Elastic Beanstalk)
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 ats-resume-scorer

# Create environment
eb create ats-prod --database.engine postgres

# Deploy
eb deploy

# Configure environment variables
eb setenv SECRET_KEY=your-key DATABASE_URL=your-db-url
```

#### Heroku
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create ats-resume-scorer

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configure
heroku config:set SECRET_KEY=your-key
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head
```

#### Google Cloud Platform (Cloud Run)
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/ats-api

# Deploy
gcloud run deploy ats-api \
  --image gcr.io/PROJECT_ID/ats-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://..." \
  --set-env-vars "SECRET_KEY=..."
```

---

## Reverse Proxy Setup (Nginx)

### 1. Install Nginx
```bash
sudo apt install nginx
```

### 2. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/ats-api
```

```nginx
upstream ats_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # Client body size for file uploads
    client_max_body_size 10M;

    # Proxy configuration
    location / {
        proxy_pass http://ats_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
    }

    # Static files (if needed)
    location /static/ {
        alias /var/www/ats-resume-scorer/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://ats_backend;
    }
}
```

### 3. Enable Site and Get SSL Certificate
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ats-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

## Performance Optimization

### 1. Gunicorn Configuration
```python
# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4  # 2 * CPU cores + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5
preload_app = True
accesslog = "/var/log/ats-api/access.log"
errorlog = "/var/log/ats-api/error.log"
loglevel = "info"
```

**Start with config:**
```bash
gunicorn -c gunicorn_config.py main:app
```

### 2. Database Connection Pooling
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Max additional connections when pool exhausted
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Test connection before using
)
```

### 3. Caching with Redis (Recommended)
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 1gb
# Set: maxmemory-policy allkeys-lru

# Restart
sudo systemctl restart redis
```

**Python Integration:**
```python
# Add to requirements.txt
redis==4.5.1
redis-py==4.5.1

# cache.py
import redis
import json

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def cache_resume_score(resume_id: str, score_data: dict, ttl: int = 3600):
    """Cache resume score for 1 hour"""
    key = f"score:{resume_id}"
    redis_client.setex(key, ttl, json.dumps(score_data))

def get_cached_score(resume_id: str):
    """Get cached score"""
    key = f"score:{resume_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else None
```

### 4. CDN for Static Assets
- Upload frontend build to CDN (CloudFlare, AWS CloudFront)
- Serve API from separate subdomain (api.yourdomain.com)
- Enable CORS for CDN domain

---

## Monitoring & Maintenance

### 1. Application Monitoring

#### Logging
```python
# main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler(
    '/var/log/ats-api/app.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger("ats_api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

#### Metrics with Prometheus
```python
# Add to requirements.txt
prometheus-client==0.16.0

# metrics.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
resume_uploads = Counter('resume_uploads_total', 'Total resume uploads')
scoring_errors = Counter('scoring_errors_total', 'Total scoring errors')

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 2. Health Checks
```python
# health.py
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/db")
async def health_check_db():
    """Database health check"""
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@router.get("/health/languagetool")
async def health_check_lt():
    """LanguageTool health check"""
    try:
        # Test LanguageTool
        from services.red_flags_validator import RedFlagsValidator
        validator = RedFlagsValidator()
        lt = validator._get_language_tool()
        status = "available" if lt else "unavailable"
        return {"status": "healthy", "languagetool": status}
    except Exception as e:
        return {"status": "unhealthy", "languagetool": str(e)}
```

### 3. Automated Backups
```bash
# Create backup script
sudo nano /usr/local/bin/backup-ats-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/ats-db"
DB_NAME="ats_db"
DB_USER="ats_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/ats_db_$DATE.sql.gz

# Delete backups older than 30 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ats_db_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-ats-db.sh

# Add cron job (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-ats-db.sh
```

### 4. Log Rotation
```bash
sudo nano /etc/logrotate.d/ats-api
```

```
/var/log/ats-api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ats-api > /dev/null 2>&1 || true
    endscript
}
```

---

## Security Best Practices

### 1. Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Deny direct access to API port
sudo ufw deny 8000/tcp
```

### 2. Environment Security
```bash
# Restrict .env file permissions
chmod 600 .env
chown www-data:www-data .env

# Restrict upload directory
chmod 750 /var/www/ats-resume-scorer/uploads
chown www-data:www-data /var/www/ats-resume-scorer/uploads
```

### 3. Rate Limiting
Already configured in application with `slowapi`:
```python
# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_resume(...):
    ...
```

### 4. Database Security
```sql
-- Restrict database user permissions
REVOKE ALL ON DATABASE ats_db FROM PUBLIC;
GRANT CONNECT ON DATABASE ats_db TO ats_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ats_user;

-- Enable SSL for database connections
-- Edit postgresql.conf:
-- ssl = on
-- ssl_cert_file = '/path/to/server.crt'
-- ssl_key_file = '/path/to/server.key'
```

---

## Troubleshooting

### Issue: High Memory Usage
**Cause**: Too many worker processes or memory leaks
**Solution**:
```bash
# Reduce workers
workers = 2  # Instead of 4

# Enable memory monitoring
max_requests = 1000  # Restart worker after 1000 requests
max_requests_jitter = 50
```

### Issue: Slow PDF Parsing
**Cause**: Large files or complex PDFs
**Solution**:
```python
# Increase timeout in nginx
proxy_read_timeout 180s;

# Increase timeout in gunicorn
timeout = 180
```

### Issue: LanguageTool Unavailable
**Cause**: Service not running or connection issues
**Solution**:
```bash
# Check if LanguageTool is running
curl http://localhost:8081/v2/check

# Restart LanguageTool
docker restart languagetool

# Or disable grammar checking
LANGUAGETOOL_ENABLED=false
```

### Issue: Database Connection Pool Exhausted
**Cause**: Too many concurrent requests
**Solution**:
```python
# Increase pool size
pool_size=20
max_overflow=40
```

### Issue: High CPU Usage
**Cause**: Grammar checking or fuzzy matching
**Solution**:
```python
# Disable fuzzy matching
USE_FUZZY_MATCHING = False

# Reduce grammar check scope
MAX_GRAMMAR_CHECKS = 5  # Instead of 10
```

---

## Scaling Strategies

### Horizontal Scaling
```bash
# Add more application servers behind load balancer
# Use Nginx or HAProxy for load balancing

# nginx.conf
upstream ats_backend {
    least_conn;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
```

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Use SSD storage for faster file I/O
- Upgrade database server

### Database Scaling
- **Read Replicas**: For analytics and reporting
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Sharding**: If data exceeds single server capacity

---

## Production Checklist

- [ ] PostgreSQL installed and configured
- [ ] Database created and migrated
- [ ] Environment variables configured
- [ ] Secret key generated (32+ characters)
- [ ] CORS origins set correctly
- [ ] SSL certificate installed
- [ ] Nginx configured as reverse proxy
- [ ] Firewall rules configured
- [ ] Systemd service enabled
- [ ] Log rotation configured
- [ ] Automated backups scheduled
- [ ] Monitoring/alerting configured
- [ ] Health check endpoints verified
- [ ] Rate limiting tested
- [ ] File upload limits set
- [ ] LanguageTool running (optional)
- [ ] Redis cache configured (optional)
- [ ] CDN configured for frontend
- [ ] Documentation deployed

---

## Support

For deployment issues:
- **Documentation**: See API.md, ARCHITECTURE.md, MIGRATION.md
- **GitHub Issues**: Report bugs and feature requests
- **Email**: devops@atsresumescorer.com
- **Status Page**: status.atsresumescorer.com
