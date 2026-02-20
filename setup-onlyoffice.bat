@echo off
REM OnlyOffice Document Server Setup Script for Windows
REM This script helps set up OnlyOffice for the ATS Resume Scorer

echo ============================================
echo   OnlyOffice Document Server Setup
echo ============================================
echo.

REM Check if Docker is installed
echo Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo OK: Docker and Docker Compose found
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    (
        echo # ATS Resume Scorer - Environment Variables
        echo ENVIRONMENT=development
        echo BACKEND_URL=http://localhost:8000
        echo CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
        echo.
        echo # OnlyOffice Configuration
        echo ONLYOFFICE_SERVER_URL=http://localhost:8080
        echo ONLYOFFICE_JWT_SECRET=change-this-secret-in-production
    ) > .env
    echo OK: .env file created
) else (
    echo OK: .env file exists
)

REM Install backend dependencies
echo.
echo Installing backend dependencies...
cd backend
pip install pyjwt==2.8.0 httpx==0.26.0
cd ..
echo OK: Backend dependencies installed

REM Start OnlyOffice with Docker Compose
echo.
echo Starting OnlyOffice Document Server...
docker-compose up -d

echo.
echo Waiting for OnlyOffice to initialize (this may take 2-3 minutes)...
timeout /t 30 /nobreak >nul

REM Create data directory
echo.
echo Setting up data directory...
if not exist backend\data mkdir backend\data
echo OK: Data directory ready

REM Print success message
echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo OnlyOffice is now running at: http://localhost:8080
echo.
echo Next steps:
echo   1. Start backend:  cd backend ^&^& python -m uvicorn main:app --reload --port 8000
echo   2. Start frontend: cd frontend ^&^& npm run dev
echo   3. Open browser:   http://localhost:3000 (or http://localhost:5173)
echo.
echo Useful commands:
echo   - View logs:       docker-compose logs -f onlyoffice-documentserver
echo   - Stop OnlyOffice: docker-compose down
echo   - Restart:         docker-compose restart
echo.
echo Documentation:
echo   - Quick Start:     ONLYOFFICE_QUICKSTART.md
echo   - Full Guide:      docs/onlyoffice-setup.md
echo.

pause
