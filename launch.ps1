# launch.ps1
# Automates starting the server and running inference for Email Triage OpenEnv

Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host " 🚀 Email Triage OpenEnv — Automation Launcher" -ForegroundColor Cyan
Write-Host ("="*60) + "`n" -ForegroundColor Cyan

# 1. Check for Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python not found. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# 2. Install dependencies
Write-Host "📦 Step 1: Checking/Installing requirements..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# 3. Start the Environment Server in the background
Write-Host "🌐 Step 2: Starting Environment Server on http://localhost:7860..." -ForegroundColor Yellow
$serverProcess = Start-Process python -ArgumentList "app.py" -PassThru -NoNewWindow

# 4. Wait for Server to be healthy
Write-Host "⏳ Step 3: Waiting for server to initialize..." -ForegroundColor Yellow
$maxRetries = 15
$retryCount = 0
$healthy = $false

while (-not $healthy -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:7860/health" -Method Get
        if ($response.status -eq "ok") {
            $healthy = $true
            Write-Host "✅ Server is UP and healthy!" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
    }
}

if (-not $healthy) {
    Write-Host "`n❌ Error: Server failed to start within timeout. Check app.py for errors." -ForegroundColor Red
    if ($serverProcess) { Stop-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue }
    exit 1
}

# 5. Run the Inference Script
Write-Host "`n🧠 Step 4: Starting Inference (LLM Agent)..." -ForegroundColor Yellow
Write-Host ("-"*40) -ForegroundColor Gray

# Run inference.py and capture/stream output
# We use -PassThru to ensure it stays in this terminal
python inference.py > inference_result.txt

Write-Host ("-"*40) -ForegroundColor Gray

# 6. Cleanup
Write-Host "🧹 Step 5: Shutting down server process..." -ForegroundColor Yellow
if ($serverProcess) {
    Stop-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue
    Write-Host "✅ Server stopped." -ForegroundColor Green
}

Write-Host "`n✨ Pipeline completed successfully!" -ForegroundColor Cyan
Write-Host ("="*60) + "`n" -ForegroundColor Cyan
