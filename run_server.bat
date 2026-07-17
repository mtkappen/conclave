@echo off
REM ========================================
REM D&D Tabletop App - Server Startup Script (Windows)
REM ========================================

echo.
echo ========================================
echo  Starting D&D Tabletop Application
echo  Port: 8020 | Database: SQLite
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Create necessary directories if they don't exist
if not exist "media" mkdir media
if not exist "static" mkdir static
if not exist "templates" mkdir templates

REM Check if database exists, create migrations if needed
python manage.py migrate --quiet 2>nul || python manage.py migrate

REM Get local IP address for network access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4 Address"') do (
    set LOCAL_IP=%%a
)

REM Start the development server on port 8020
echo.
echo ========================================
echo  SERVER STARTING...
echo ========================================
echo  Local Access:   http://127.0.0.1:8020/
echo  Network Access: http://%LOCAL_IP%:8020/
echo.
echo  Default Admin Account:
echo    Username: admin
echo    Password: admin123
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 0.0.0.0:8020

