#!/bin/bash
# Cleanup Script - Stop All ATS Resume Scorer Background Processes

echo "🧹 Cleaning up background processes..."
echo ""

# Kill old uvicorn processes (keep the newest)
echo "Stopping old backend servers..."
pkill -f "uvicorn.*8000" 2>/dev/null
sleep 2

# Kill old vite processes (keep the newest)
echo "Stopping old frontend servers..."
pkill -f "vite" 2>/dev/null
sleep 2

# Kill vitest
echo "Stopping test runner..."
pkill -f "vitest" 2>/dev/null
sleep 2

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To restart the servers:"
echo "  Backend:  cd backend && python3 -m uvicorn main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
