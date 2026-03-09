#!/usr/bin/env pwsh
# start.ps1 — Kill any stale process on port 8000, then start the FastAPI backend.
# Usage:  .\start.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "=== PathFinder AI Backend Launcher ===" -ForegroundColor Cyan
Write-Host ""

# ── Kill stale process on port 8000 ─────────────────────────────────────────
$conn = Get-NetTCPConnection -LocalPort 8000 | Select-Object -First 1
if ($conn) {
    $procId = $conn.OwningProcess
    Write-Host "Found process $procId occupying port 8000. Killing it..." -ForegroundColor Yellow
    Stop-Process -Id $procId -Force
    Start-Sleep -Milliseconds 700
    Write-Host "Done." -ForegroundColor Green
} else {
    Write-Host "Port 8000 is free." -ForegroundColor Green
}

# ── Paths ────────────────────────────────────────────────────────────────────
$root      = $PSScriptRoot
$venvPy    = Join-Path $root ".venv\Scripts\python.exe"
$uvicorn   = Join-Path $root ".venv\Scripts\uvicorn.exe"
$backend   = Join-Path $root "backend"

if (-not (Test-Path $uvicorn)) {
    Write-Host "ERROR: uvicorn not found at $uvicorn" -ForegroundColor Red
    Write-Host "Run:  pip install uvicorn  inside your .venv" -ForegroundColor Red
    exit 1
}

# ── Start Uvicorn ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting backend at http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

Push-Location $backend
& $uvicorn app.main:app --port 8000 --reload
Pop-Location
