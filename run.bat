@echo off
title MetonymyStudio
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Download from https://python.org
    echo Tick "Add Python to PATH" during installation.
    pause & exit /b 1
)

pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo Installing PySide6 and openpyxl...
    pip install PySide6 openpyxl --quiet
)

python -m app.main
if errorlevel 1 ( pause )
