@echo off
REM NAS Auto Sync Manager - Windows Launcher
REM Double-click this file to start the application

echo Starting NAS Auto Sync Manager...
python nas_sync_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start the application.
    echo Please make sure Python is installed and in your PATH.
    echo.
    pause
)
