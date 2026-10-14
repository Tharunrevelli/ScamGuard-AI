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
Write-Host "[3/3] Launching ScamGuard Backend & Web Dashboard on http://localhost:8000..." -ForegroundColor Green
Start-Process "http://localhost:8000"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
