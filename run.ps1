# CycloneAI - One-Click Launcher for Windows PowerShell

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting CycloneAI — Tropical Cyclone Intelligence     " -ForegroundColor White
Write-Host "   Smart India Hackathon (SIH) Prototype                   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Add Node and Python to PATH if needed
$nodeBin = "C:\Users\shaan\AppData\Local\OpenAI\Codex\runtimes\cua_node\b474a88d5d105afa\bin"
if (Test-Path $nodeBin) {
    $env:Path = "$nodeBin;C:\Users\shaan\AppData\Local\Programs\Python\Python312;C:\Users\shaan\AppData\Local\Programs\Python\Python312\Scripts;" + $env:Path
}

# 2. Check Python
$pythonCmd = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\Users\shaan\AppData\Local\Programs\Python\Python312\python.exe") {
        $pythonCmd = "C:\Users\shaan\AppData\Local\Programs\Python\Python312\python.exe"
    }
}

Write-Host "`n[1/3] Initializing SQLite database & Demo Scenario..." -ForegroundColor Yellow
& $pythonCmd -c "from backend.services.demo_service import init_demo_data; init_demo_data()"

Write-Host "[2/3] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath $pythonCmd -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -PassThru

Write-Host "[3/3] Launching React Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Set-Location frontend
$frontendJob = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -PassThru
Set-Location ..

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "`nCycloneAI is ONLINE!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend API: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C or close this terminal to stop services." -ForegroundColor Gray

# Keep script alive to monitor jobs
try {
    Wait-Process -Id $backendJob.Id, $frontendJob.Id
} finally {
    Stop-Process -Id $backendJob.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendJob.Id -ErrorAction SilentlyContinue
}
