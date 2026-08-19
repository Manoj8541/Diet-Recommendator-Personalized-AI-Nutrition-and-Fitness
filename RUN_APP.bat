@echo off
title Diet Recommendator - One-Click Launcher
color 0A

echo ================================================================
echo        🥗 DIET RECOMMENDATOR - ONE-CLICK LAUNCHER
echo ================================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

:: 2. Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js is not installed or not in your system PATH.
    echo Please install Node.js (LTS) from https://nodejs.org/
    echo.
    pause
    exit /b
)

echo [1/4] Checking and installing Backend dependencies...
cd backend
python -m pip install -r requirements.txt >nul 2>&1
cd ..

echo [2/4] Checking and installing Frontend dependencies...
cd frontend
if not exist node_modules (
    echo       Installing npm packages (first time setup)...
    call npm install
)
cd ..

echo [3/4] Starting FastAPI Backend (Port 8000)...
start "Diet Recommendator - Backend" cmd /k "cd /d ""%~dp0backend"" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [4/4] Starting React/Vite Frontend (Port 5173)...
start "Diet Recommendator - Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 4 /nobreak >nul

echo.
echo Opening Diet Recommendator in your browser...
start http://localhost:5173

color 0B
echo.
echo ================================================================
echo  ✅ Application is now RUNNING!
echo.
echo  • Frontend: http://localhost:5173
echo  • Backend API & Docs: http://127.0.0.1:8000/docs
echo.
echo  To stop the application, simply close the two backend/frontend
echo  terminal windows.
echo ================================================================
echo.
pause
