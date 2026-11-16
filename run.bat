@echo off
set PYTHON="%USERPROFILE%\.python311\python.exe"
if not exist %PYTHON% (
    echo Python executable not found in %USERPROFILE%\.python311.
    pause
    exit /b 1
)
cd /d "%~dp0"
echo Starting FastAPI Automated Multi-Platform Posting System on port 4000...
echo Swagger UI will be available at: http://localhost:4000/docs
%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
pause
