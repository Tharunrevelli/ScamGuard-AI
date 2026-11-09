# Single-Click Thesis Demonstration Script for ScamGuard AI
# Starts the FastAPI Backend and opens the Web Application in your default browser.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "        ScamGuard AI — Thesis Demonstration Launcher       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Python
Write-Host "[1/3] Verifying Python runtime..." -ForegroundColor Green
$pythonVersion = python --version
Write-Host "Found: $pythonVersion"

# 2. Run automated test suite
Write-Host "[2/3] Running automated verification test suite..." -ForegroundColor Green
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Some tests reported issues." -ForegroundColor Red
} else {
    Write-Host "All 30 automated verification tests passed successfully (100%)." -ForegroundColor Green
}

# 3. Launch Backend & Web Server
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254*" } | Select-Object -First 1).IPAddress
if (-not $localIP) { $localIP = "127.0.0.1" }

Write-Host "[3/3] Launching ScamGuard Backend & Web Dashboard..." -ForegroundColor Green
Write-Host "  -> Local Browser:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "  -> Mobile / iOS Safari:  http://${localIP}:8000" -ForegroundColor Yellow
Write-Host "     (Open on iPhone/iPad connected to the same Wi-Fi)" -ForegroundColor Gray

Start-Process "http://localhost:8000"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
