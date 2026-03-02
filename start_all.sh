#!/bin/bash
# Start backend
cd backend
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
cd ..

# Start frontend dashboard
cd frontend-dashboard
npm install
npm run dev &
cd ..

# Start frontend PWA
cd frontend-pwa
npm install
npm run dev &
cd ..

wait
