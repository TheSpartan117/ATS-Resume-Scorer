#!/bin/bash
# Start Servers Script - Run both backend and frontend

echo "============================================================"
echo "Starting ATS Resume Scorer Servers"
echo "============================================================"
echo ""

# Kill any existing processes
echo "🧹 Cleaning up old processes..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "vitest" 2>/dev/null
sleep 3

echo ""
echo "🚀 Starting Backend (Port 8000)..."
cd /Users/sabuj.mondal/ats-resume-scorer/backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 3

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is healthy!"
else
    echo "   ⚠️  Backend not responding yet, give it a few seconds..."
fi

echo ""
echo "🚀 Starting Frontend (Port 5173)..."
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
sleep 5

# Check which port frontend is on
if lsof -i :5173 > /dev/null 2>&1; then
    FRONTEND_PORT=5173
elif lsof -i :5174 > /dev/null 2>&1; then
    FRONTEND_PORT=5174
elif lsof -i :5175 > /dev/null 2>&1; then
    FRONTEND_PORT=5175
else
    FRONTEND_PORT="unknown"
fi

if [ "$FRONTEND_PORT" != "unknown" ]; then
    echo "   ✅ Frontend is running on port $FRONTEND_PORT!"
else
    echo "   ⚠️  Frontend not detected, check logs: tail -f /tmp/frontend.log"
fi

echo ""
echo "============================================================"
echo "✅ SERVERS STARTED"
echo "============================================================"
echo ""
echo "📍 Access Points:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "📋 View Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 Stop Servers:"
echo "   ./cleanup_processes.sh"
echo ""
