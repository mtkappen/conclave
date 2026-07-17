@echo off
REM ========================================
REM D&D Tabletop App - Setup Script (Windows)
REM ========================================

echo.
echo ========================================
echo  D&D Tabletop Application Setup
echo  Port: 8020 | Database: SQLite
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [4/4] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Creating project directories...
if not exist "media" mkdir media
if not exist "static" mkdir static
if not exist "templates" mkdir templates

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run 'run_server.bat' to start the application
echo   2. Access http://localhost:8020 in your browser
echo   3. Create a superuser when prompted
echo.
pause