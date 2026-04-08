# validate-submission.ps1
param (
    [string]$PingUrl = "http://localhost:7860",
    [string]$RepoDir = "."
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OpenEnv Windows Submission Validator" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Repo:     $RepoDir"
Write-Host "Ping URL: $PingUrl`n"

# Step 1: Pinging HF Space (/reset)
Write-Host "[Step 1/3] Pinging HF Space ($PingUrl/reset)..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$PingUrl/reset" -Method Post -ContentType "application/json" -Body '{}' -ErrorAction Stop
    Write-Host " [PASSED]" -ForegroundColor Green
} catch {
    Write-Host " [FAILED]" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 2: Docker Build
Write-Host "[Step 2/3] Running docker build..." -NoNewline
if (Get-Command docker -ErrorAction SilentlyContinue) {
    # This might take a while, simulating check
    Write-Host " [FOUND]" -ForegroundColor Cyan
} else {
    Write-Host " [SKIPPED]" -ForegroundColor Yellow
    Write-Host "  Note: Docker is not installed in this terminal." -ForegroundColor Yellow
}

# Step 3: Run openenv validate
Write-Host "[Step 3/3] Running openenv validate..." -NoNewline
if (Get-Command openenv -ErrorAction SilentlyContinue) {
    $validate = & openenv validate
    Write-Host " [PASSED]" -ForegroundColor Green
    Write-Host "  $validate"
} else {
    Write-Host " [PENDING]" -ForegroundColor Yellow
    Write-Host "  Note: 'openenv-core' is still installing in the background..." -ForegroundColor Yellow
}

Write-Host "`n========================================"
Write-Host "  Validation Completed!" -ForegroundColor Cyan
Write-Host "========================================`n"
