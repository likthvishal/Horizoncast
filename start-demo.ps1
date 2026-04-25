#!/usr/bin/env pwsh
# HorizonCast — local demo launcher (Windows / PowerShell)
# Starts the FastAPI backend on :8000 and the Next.js frontend on :3000.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  HorizonCast — Local Demo" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Python venv -----------------------------------------------------
if (-not (Test-Path ".venv")) {
    Write-Host "[1/4] Creating Python venv..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/4] Python venv already exists." -ForegroundColor Green
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"

# 2. Backend deps ----------------------------------------------------
Write-Host "[2/4] Installing backend deps (fastapi, uvicorn)..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r requirements-demo.txt --quiet

# 3. Frontend deps ---------------------------------------------------
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[3/4] Installing frontend deps (npm install)..." -ForegroundColor Yellow
    Push-Location frontend
    npm install --silent
    Pop-Location
} else {
    Write-Host "[3/4] Frontend node_modules already installed." -ForegroundColor Green
}

# 4. Launch ----------------------------------------------------------
Write-Host "[4/4] Starting backend (:8000) and frontend (:3000)..." -ForegroundColor Yellow
Write-Host ""

$backendCmd = "Set-Location '$root'; & '$venvPython' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
$frontendCmd = "Set-Location '$root\frontend'; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Start-Sleep -Seconds 4
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  HorizonCast is starting up!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  API:       http://localhost:8000" -ForegroundColor White
Write-Host "  API docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  (Two new PowerShell windows are running the servers.)" -ForegroundColor DarkGray
Write-Host "  Close them to stop." -ForegroundColor DarkGray
Write-Host ""
