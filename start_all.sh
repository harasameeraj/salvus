#!/bin/bash
# Kill any existing processes on relevant ports to avoid "Address already in use"
lsof -ti:8000,5173,5174,5175 | xargs kill -9 2>/dev/null || true
sleep 2

mkdir -p logs

echo "Starting Backend..."
cd backend
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
cd ..

echo "Starting Dashboard..."
cd frontend-dashboard
npm run dev -- --host > ../logs/dashboard.log 2>&1 &
cd ..

echo "Starting PWA..."
cd frontend-pwa
npm run dev -- --host > ../logs/pwa.log 2>&1 &
cd ..

echo "------------------------------------------------"
echo "CrisisSync AI: ALL SYSTEMS INITIALIZING"
echo "------------------------------------------------"
echo "Backend: http://localhost:8000"
echo "Dashboard: http://localhost:5174"
echo "PWA: http://localhost:5173"
echo "------------------------------------------------"
echo "Checking logs... (Press Ctrl+C to stop servers)"
tail -f logs/backend.log logs/dashboard.log logs/pwa.log
