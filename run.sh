#!/bin/bash
# ===========================================
# DreamSight AI - Startup Script for Unix/Mac
# ===========================================
# This script starts both the FastAPI backend and Next.js frontend concurrently.

echo ""
echo "============================================="
echo "      DreamSight AI - Starting Servers"
echo "============================================="
echo ""

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "[WARNING] backend/.env not found!"
    if [ -f ".env.example" ]; then
        echo "[INFO] Copying from .env.example..."
        cp .env.example backend/.env
        echo "[INFO] Created backend/.env - Please edit it with your API keys!"
    else
        echo "[ERROR] No .env.example found. Please create backend/.env manually."
    fi
    echo ""
fi

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "[1/2] Starting FastAPI Backend on http://localhost:8000"
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to initialize
sleep 3

# Start Frontend
echo "[2/2] Starting Next.js Frontend on http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================="
echo "      Both servers are running!"
echo "============================================="
echo ""
echo "   Backend API:    http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   Frontend:       http://localhost:3000"
echo ""
echo "   Press Ctrl+C to stop all servers"
echo ""

# Wait for background processes
wait
