#!/usr/bin/env pwsh
# Check if the application is responding
$response = curl -sf http://localhost:8000/ 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Application is running"
} else {
    Write-Host "FAIL: Application not responding"
    exit 1
}
