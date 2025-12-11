#!/usr/bin/env pwsh
# Debug script to show path calculation

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir

Write-Host "=== Path Debug ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Script directory: $scriptDir"
Write-Host "Project directory: $projectDir"
Write-Host ""

# Check environment
Write-Host "=== Environment ===" -ForegroundColor Cyan
Write-Host "OS: $([System.Environment]::OSVersion.Platform)"
Write-Host "PSVersion: $($PSVersionTable.PSVersion)"
Write-Host "WSL_DISTRO_NAME: $env:WSL_DISTRO_NAME"
Write-Host ""

# Resolve path
$resolvedPath = Resolve-Path $projectDir -ErrorAction SilentlyContinue
Write-Host "Resolved path: $($resolvedPath.Path)"
Write-Host ""

# Test different path formats
Write-Host "=== Path formats ===" -ForegroundColor Cyan
Write-Host "As-is: $projectDir"
Write-Host "Forward slashes: $($projectDir -replace '\\', '/')"

# If on Windows, show the path Docker Desktop expects
if ($IsWindows -or [System.Environment]::OSVersion.Platform -eq 'Win32NT') {
    Write-Host ""
    Write-Host "=== Windows Docker Desktop path ===" -ForegroundColor Yellow
    # Docker Desktop expects /c/Users/... format or C:/Users/... format
    $dockerPath = $projectDir -replace '\\', '/'
    Write-Host "Docker path: $dockerPath"
}

# Show what docker-compose will see
Write-Host ""
Write-Host "=== Testing with docker compose ===" -ForegroundColor Cyan
$env:BASE_HOST_PATH = $projectDir -replace '\\', '/'
Write-Host "BASE_HOST_PATH = $env:BASE_HOST_PATH"
Write-Host ""
Write-Host "Running: docker compose config (volumes section)"
Push-Location $projectDir
docker compose config 2>&1 | Select-String -Pattern "volumes:" -Context 0,12
Pop-Location
