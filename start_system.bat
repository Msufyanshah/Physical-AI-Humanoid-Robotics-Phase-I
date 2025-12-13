@echo off
echo Starting Physical AI & Humanoid Robotics RAG System...

REM Set environment variables from .env file
for /f "tokens=*" %%i in ('type .env ^| findstr /v "^#"') do (
    for /f "tokens=1,* delims==" %%j in ("%%i") do (
        set "%%j=%%k"
    )
)

REM Start the backend server
echo Starting backend server...
cd backend
start /min python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak >nul

REM Start the frontend server (if needed)
echo Starting frontend server...
cd ..
cd frontend
if not exist node_modules call npm install
call npm run build
start /min cmd /c "npx serve -s build -l 3000"
timeout /t 3 /nobreak >nul

echo Both servers started:
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo Press any key to stop
pause >nul

REM Cleanup
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im node.exe 2>nul