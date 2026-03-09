#!/usr/bin/env pwsh
# start.ps1 — One-command launcher: kills stale ports, then starts Ollama + FastAPI + Vite.
# Usage:  .\start.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PathFinder AI  —  Full Stack Launcher  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Kill stale processes on ports 8000 and 8080 ───────────────────────────────
foreach ($port in @(8000, 8080)) {
    $conn = Get-NetTCPConnection -LocalPort $port | Select-Object -First 1
    if ($conn) {
        $procId = $conn.OwningProcess
        Write-Host "  [cleanup] Port $port occupied by PID $procId — killing..." -ForegroundColor Yellow
        Stop-Process -Id $procId -Force
        Start-Sleep -Milliseconds 500
    }
}
Write-Host "  [cleanup] Ports 8000 and 8080 are free." -ForegroundColor Green
Write-Host ""

# ── Paths ────────────────────────────────────────────────────────────────────
$root     = $PSScriptRoot
$uvicorn  = Join-Path $root ".venv\Scripts\uvicorn.exe"
$backend  = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

if (-not (Test-Path $uvicorn)) {
    Write-Host "ERROR: uvicorn not found at $uvicorn" -ForegroundColor Red
    Write-Host "  Run:  .\.venv\Scripts\pip install uvicorn fastapi  (inside project root)" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $frontend)) {
    Write-Host "ERROR: frontend folder not found at $frontend" -ForegroundColor Red
    exit 1
}

# ── 1. Start Ollama (background, hidden) ─────────────────────────────────────
$ollamaExe = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaExe) {
    # Check if ollama is already serving
    $ollamaConn = Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $ollamaConn) {
        Write-Host "  [1/3] Starting Ollama (background)..." -ForegroundColor Cyan
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 2
        Write-Host "        Ollama running at http://localhost:11434" -ForegroundColor DarkGray
    } else {
        Write-Host "  [1/3] Ollama already running on port 11434." -ForegroundColor Green
    }
} else {
    Write-Host "  [1/3] WARNING: 'ollama' not found in PATH. LLM features won't work." -ForegroundColor Yellow
    Write-Host "        Install Ollama from https://ollama.com then run: ollama pull llama3.2:3b" -ForegroundColor DarkGray
}
Write-Host ""

# ── 2. Start FastAPI backend (new PowerShell window) ─────────────────────────
Write-Host "  [2/3] Starting FastAPI backend (new window)..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$backend'; & '$uvicorn' app.main:app --port 8000 --reload; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Write-Host "        Backend will be at http://localhost:8000" -ForegroundColor DarkGray
Write-Host ""

# ── 3. Start Vite frontend (new PowerShell window) ────────────────────────────
Write-Host "  [3/3] Starting Vite dev server (new window)..." -ForegroundColor Cyan
$frontendCmd = "Set-Location '$frontend'; npm run dev; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
Write-Host "        Frontend will be at http://localhost:8080" -ForegroundColor DarkGray
Write-Host ""

# ── Done ──────────────────────────────────────────────────────────────────────
Start-Sleep -Seconds 3
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  All services started!  Open in browser:" -ForegroundColor Green
Write-Host ""
Write-Host "    App   →  http://localhost:8080" -ForegroundColor White
Write-Host "    API   →  http://localhost:8000/docs" -ForegroundColor White
Write-Host "    Ollama→  http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "  Close the two terminal windows to stop backend/frontend." -ForegroundColor DarkGray
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
