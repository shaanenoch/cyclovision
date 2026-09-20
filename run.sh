#!/bin/bash
# CycloneAI - One-Click Launcher for Linux / macOS

echo "=========================================================="
echo "   Starting CycloneAI — Tropical Cyclone Intelligence     "
echo "   Smart India Hackathon (SIH) Prototype                   "
echo "=========================================================="

# 1. Initialize demo data
python3 -c "from backend.services.demo_service import init_demo_data; init_demo_data()"

# 2. Launch backend
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# 3. Launch frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "CycloneAI is ONLINE!"
echo "  Frontend:     http://localhost:5173"
echo "  Backend API:  http://127.0.0.1:8000"
echo "  Swagger Docs: http://127.0.0.1:8000/docs"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
