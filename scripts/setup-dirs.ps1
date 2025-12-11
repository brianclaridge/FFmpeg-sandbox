#!/usr/bin/env pwsh
# Setup directories for Docker volume mounts
# Run this BEFORE docker-compose up

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir

Write-Host "Project directory: $projectDir"

# Create directories if they don't exist
$dirs = @(
    ".data/input",
    ".data/output",
    ".data/logs"
)

foreach ($dir in $dirs) {
    $fullPath = Join-Path $projectDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created: $dir"
    } else {
        Write-Host "Exists: $dir"
    }
}

Write-Host ""
Write-Host "Directory permissions:"
Get-ChildItem $projectDir -Directory -Force | Where-Object { $_.Name -eq ".data" } | ForEach-Object {
    Write-Host "  $($_.FullName)"
}

Write-Host ""
Write-Host "Ready to run: docker-compose up -d"
