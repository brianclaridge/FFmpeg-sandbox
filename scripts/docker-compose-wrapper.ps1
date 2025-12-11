#!/usr/bin/env pwsh
# Docker Compose wrapper - requires HOST_PWD environment variable

param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$ComposeArgs
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir

# Check HOST_PWD
if (-not $env:HOST_PWD) {
    Write-Host "ERROR: HOST_PWD environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it to your Windows project path, e.g.:" -ForegroundColor Yellow
    Write-Host '  $env:HOST_PWD = "C:/Users/you/projects/audio-clip-helper"'
    Write-Host ""
    exit 1
}

Write-Host "HOST_PWD: $env:HOST_PWD" -ForegroundColor Cyan
Write-Host ""

# Ensure directories exist on host
$dirs = @(".data/input", ".data/output", ".data/logs")
foreach ($dir in $dirs) {
    $fullPath = Join-Path $projectDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Yellow
    }
}

# Run docker-compose
Push-Location $projectDir
try {
    if ($ComposeArgs.Count -eq 0) {
        Write-Host "Usage: docker-compose-wrapper.ps1 <args>"
        exit 1
    }

    Write-Host "Running: docker compose $($ComposeArgs -join ' ')" -ForegroundColor Green
    & docker compose @ComposeArgs
}
finally {
    Pop-Location
}
