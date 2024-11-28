@echo off
REM Check if Python is installed
where python >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in your PATH.
    pause
    exit /b
)

REM Run Tracker.py without creating a new console window
cd PythonScripts
start /b python Tracker.py
pause
