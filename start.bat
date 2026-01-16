@echo off
REM ===========================================
REM DreamSight AI - Startup Script for Windows
REM ===========================================
REM This script starts both the FastAPI backend and Next.js frontend concurrently.

echo.
echo =============================================
echo       DreamSight AI - Starting Servers
echo =============================================
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found!
    echo [INFO] Copying from .env.example...
    if exist ".env.example" (
        copy .env.example backend\.env
        echo [INFO] Created backend\.env - Please edit it with your API keys!
    ) else (
        echo [ERROR] No .env.example found. Please create backend\.env manually.
    )
    echo.
)

REM Start Backend
echo [1/2] Starting FastAPI Backend on http://localhost:8000
echo.
start "DreamSight Backend" cmd /k "cd backend && .\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak > nul

REM Start Frontend
echo [2/2] Starting Next.js Frontend on http://localhost:3000
echo.
start "DreamSight Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo =============================================
echo       Both servers are starting!
echo =============================================
echo.
echo    Backend API:    http://localhost:8000
echo    API Docs:       http://localhost:8000/docs
echo    Frontend:       http://localhost:3000
echo.
echo    Press any key to close this window...
echo    (The servers will continue running)
echo.
pause > nul
