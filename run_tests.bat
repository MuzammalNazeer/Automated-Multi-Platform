@echo off
set PYTHON="%USERPROFILE%\.python311\python.exe"
cd /d "%~dp0"
echo Running test suite...
%PYTHON% -m pytest tests/ -v
pause
