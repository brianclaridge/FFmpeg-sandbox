#!/usr/bin/env pwsh
# Diagnose Docker volume mount issues for logs

Write-Host "=== Log Diagnostics ===" -ForegroundColor Cyan
Write-Host ""

# Check if container is running
$container = docker ps --filter "name=audio-processor" --format "{{.Names}}" 2>$null
if (-not $container) {
    Write-Host "ERROR: Container not running" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d"
    exit 1
}

Write-Host "Container: $container" -ForegroundColor Green

# Check logs inside container
Write-Host ""
Write-Host "=== Container logs directory ===" -ForegroundColor Cyan
docker exec $container ls -la /app/logs/

# Check logs on host
Write-Host ""
Write-Host "=== Host logs directory ===" -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsDir = Join-Path (Split-Path -Parent $scriptDir) "logs"
Write-Host "Path: $logsDir"

if (Test-Path $logsDir) {
    Get-ChildItem $logsDir -Force | Format-Table Name, Length, LastWriteTime
} else {
    Write-Host "Directory does not exist!" -ForegroundColor Red
}

# Check volume mount
Write-Host ""
Write-Host "=== Docker volume mount ===" -ForegroundColor Cyan
docker inspect $container --format '{{range .Mounts}}{{if eq .Destination "/app/logs"}}Source: {{.Source}}{{"\n"}}Destination: {{.Destination}}{{"\n"}}Type: {{.Type}}{{end}}{{end}}'

# Suggestion
Write-Host ""
Write-Host "=== Fix attempt ===" -ForegroundColor Yellow
Write-Host "Copying logs from container to host..."
docker cp "${container}:/app/logs/app.log" $logsDir/app.log 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Copied successfully. Check: $logsDir\app.log" -ForegroundColor Green
} else {
    Write-Host "Copy failed" -ForegroundColor Red
}
