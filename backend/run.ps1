# Start the CycloneWatch AI / ReliefSense FastAPI backend
$ErrorActionPreference = "Stop"
Write-Host "Starting ReliefSense / CycloneWatch AI Backend..." -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
