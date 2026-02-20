#!/bin/bash
# Status Check Script - Show What's Currently Running

echo "============================================================"
echo "ATS RESUME SCORER - STATUS CHECK"
echo "============================================================"
echo ""

# Check Backend (Port 8000)
echo "🔍 Backend API (Port 8000):"
if lsof -i :8000 >/dev/null 2>&1; then
    BACKEND_PID=$(lsof -ti :8000 | head -1)
    echo "   ✅ Running (PID: $BACKEND_PID)"
    echo "   🌐 http://localhost:8000"
    curl -s http://localhost:8000/health >/dev/null 2>&1 && echo "   ✅ Health check: OK" || echo "   ⚠️  Health check: FAILED"
else
    echo "   ❌ Not running"
fi
echo ""

# Check Frontend (Port 5173)
echo "🔍 Frontend UI (Port 5173):"
if lsof -i :5173 >/dev/null 2>&1; then
    FRONTEND_PID=$(lsof -ti :5173 | head -1)
    echo "   ✅ Running (PID: $FRONTEND_PID)"
    echo "   🌐 http://localhost:5173"
else
    echo "   ❌ Not running"
fi
echo ""

# Check for duplicate processes
echo "🔍 Process Count:"
BACKEND_COUNT=$(pgrep -f "uvicorn.*8000" | wc -l | tr -d ' ')
FRONTEND_COUNT=$(pgrep -f "vite" | wc -l | tr -d ' ')
VITEST_COUNT=$(pgrep -f "vitest" | wc -l | tr -d ' ')

echo "   Backend processes: $BACKEND_COUNT"
[ "$BACKEND_COUNT" -gt 2 ] && echo "   ⚠️  Multiple backend processes detected (recommend cleanup)"

echo "   Frontend processes: $FRONTEND_COUNT"
[ "$FRONTEND_COUNT" -gt 2 ] && echo "   ⚠️  Multiple frontend processes detected (recommend cleanup)"

echo "   Test runner: $VITEST_COUNT"
[ "$VITEST_COUNT" -gt 0 ] && echo "   ℹ️  Test runner is active (safe to stop if not testing)"

echo ""
echo "============================================================"

# Recommendations
if [ "$BACKEND_COUNT" -gt 2 ] || [ "$FRONTEND_COUNT" -gt 2 ]; then
    echo "💡 Recommendation: Run ./cleanup_processes.sh to remove duplicates"
    echo ""
fi

# Quick actions
echo "Quick Actions:"
echo "  Stop all:    ./cleanup_processes.sh"
echo "  Restart backend:  cd backend && python3 -m uvicorn main:app --reload"
echo "  Restart frontend: cd frontend && npm run dev"
echo "  View logs:   tail -f /private/tmp/claude-*/tasks/*.output"
echo ""
