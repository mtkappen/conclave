# D&D Tabletop App - Server Startup Script (PowerShell)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting D&D Tabletop Application" -ForegroundColor White
Write-Host "  Port: 8020 | Database: SQLite" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Create directories if needed
if (-not (Test-Path "media")) { New-Item -ItemType Directory -Force -Path "media" | Out-Null }
if (-not (Test-Path "static")) { New-Item -ItemType Directory -Force -Path "static" | Out-Null }

# Run migrations
Write-Host "[1/2] Running database migrations..." -ForegroundColor Green
python manage.py migrate --quiet 2>$null
if ($LASTEXITCODE -ne 0) { python manage.py migrate }

# Get local IP (try multiple methods)
$ip = $null

# Method 1: Get-NetIPAddress
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -match "^10\.|^192\.168\.|^172\.(1[6-9]|2[0-9]|3[01])"} | Select-Object -First 1).IPAddress

# Method 2: Fallback to ipconfig parsing
if (-not $ip) {
    $ipInfo = ipconfig | Select-String "IPv4 Address" -Context 0,1
    if ($ipInfo) {
        $ip = ($ipInfo.Context.Display -match "\d+\.\d+\.\d+\.\d+") -replace ".*(\d+\.\d+\.\d+\.\d+).*", '$1'
    }
}

# Method 3: Last resort fallback
if (-not $ip) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -match "^10\.|^192\.168\.|^172\."} | Select-Object -First 1).IPAddress
}

# Final fallback
if (-not $ip) { $ip = "YOUR_IP" }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SERVER STARTING..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Local Access:   http://127.0.0.1:8020/" -ForegroundColor White
Write-Host "  Network Access: http://${ip}:8020/" -ForegroundColor Green
Write-Host ""
Write-Host "  Default Admin Account:" -ForegroundColor Yellow
Write-Host "    Username: admin" -ForegroundColor White
Write-Host "    Password: admin123" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[!] If Windows Firewall asks, click 'Allow access' for Private networks" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server..." -ForegroundColor Gray
Write-Host ""

# Start server (binds to all interfaces)
python manage.py runserver 0.0.0.0:8020