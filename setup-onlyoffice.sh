#!/bin/bash

# OnlyOffice Document Server Setup Script
# This script helps set up OnlyOffice for the ATS Resume Scorer

set -e

echo "============================================"
echo "  OnlyOffice Document Server Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo -e "${YELLOW}Creating .env file from template...${NC}"

    # Generate random JWT secret
    JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "change-this-secret-$(date +%s)")

    cat > .env << EOF
# ATS Resume Scorer - Environment Variables
ENVIRONMENT=development
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# OnlyOffice Configuration
ONLYOFFICE_SERVER_URL=http://localhost:8080
ONLYOFFICE_JWT_SECRET=${JWT_SECRET}
EOF

    echo -e "${GREEN}✓ .env file created with random JWT secret${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check if backend dependencies are installed
echo ""
echo "Checking backend dependencies..."
if ! python3 -c "import jwt" &> /dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend
    pip install pyjwt==2.8.0 httpx==0.26.0
    cd ..
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Backend dependencies already installed${NC}"
fi

# Start OnlyOffice with Docker Compose
echo ""
echo -e "${YELLOW}Starting OnlyOffice Document Server...${NC}"
docker-compose up -d

echo ""
echo "Waiting for OnlyOffice to initialize (this may take 2-3 minutes on first run)..."

# Wait for OnlyOffice to be ready
MAX_WAIT=180
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8080/welcome > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OnlyOffice is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 5
    WAITED=$((WAITED + 5))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${RED}❌ OnlyOffice failed to start within $MAX_WAIT seconds${NC}"
    echo "Check logs with: docker-compose logs onlyoffice-documentserver"
    exit 1
fi

# Create data directory if it doesn't exist
echo ""
echo "Setting up data directory..."
mkdir -p backend/data
chmod 755 backend/data
echo -e "${GREEN}✓ Data directory ready${NC}"

# Print success message
echo ""
echo "============================================"
echo -e "${GREEN}  ✓ Setup Complete!${NC}"
echo "============================================"
echo ""
echo "OnlyOffice is now running at: http://localhost:8080"
echo ""
echo "Next steps:"
echo "  1. Start backend:  cd backend && python -m uvicorn main:app --reload --port 8000"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Open browser:   http://localhost:3000 (or http://localhost:5173)"
echo ""
echo "Useful commands:"
echo "  - View logs:       docker-compose logs -f onlyoffice-documentserver"
echo "  - Stop OnlyOffice: docker-compose down"
echo "  - Restart:         docker-compose restart"
echo ""
echo "Documentation:"
echo "  - Quick Start:     ONLYOFFICE_QUICKSTART.md"
echo "  - Full Guide:      docs/onlyoffice-setup.md"
echo ""
echo "Health check: curl http://localhost:8000/api/onlyoffice/health"
echo ""
