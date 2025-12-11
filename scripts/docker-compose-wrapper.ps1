#!/usr/bin/env pwsh
# Docker Compose wrapper that calculates correct host path for bind mounts
# Handles Windows Docker Desktop path translation

param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$ComposeArgs
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir

# Determine the correct path format for Docker
function Get-DockerHostPath {
    param([string]$Path)

    $resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
    if (-not $resolvedPath) {
        return $Path
    }

    $fullPath = $resolvedPath.Path

    # Check if running in WSL
    if ($env:WSL_DISTRO_NAME) {
        # In WSL, convert to Windows path for Docker Desktop
        $winPath = wsl.exe wslpath -w $fullPath 2>$null
        if ($LASTEXITCODE -eq 0 -and $winPath) {
            return $winPath.Trim()
        }
    }

    # On native Windows, use the path as-is
    # Convert backslashes to forward slashes for Docker
    return $fullPath -replace '\\', '/'
}

# Calculate the base host path
$env:BASE_HOST_PATH = Get-DockerHostPath $projectDir

Write-Host "Project directory: $projectDir" -ForegroundColor Cyan
Write-Host "Docker host path: $env:BASE_HOST_PATH" -ForegroundColor Cyan
Write-Host ""

# Ensure directories exist on host
$dirs = @("data/input", "data/output", "logs")
foreach ($dir in $dirs) {
    $fullPath = Join-Path $projectDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Yellow
    }
}

# Change to project directory and run docker-compose
Push-Location $projectDir
try {
    if ($ComposeArgs.Count -eq 0) {
        Write-Host "Usage: docker-compose-wrapper.ps1 <docker-compose args>"
        Write-Host "Example: docker-compose-wrapper.ps1 up -d"
        exit 1
    }

    Write-Host "Running: docker compose $($ComposeArgs -join ' ')" -ForegroundColor Green
    Write-Host ""

    & docker compose @ComposeArgs
    $exitCode = $LASTEXITCODE

    # If 'up' was run, show mount verification
    if ($ComposeArgs -contains 'up') {
        Start-Sleep -Seconds 2
        $container = docker ps --filter "name=audio-processor" --format "{{.Names}}" 2>$null
        if ($container) {
            Write-Host ""
            Write-Host "=== Volume mount verification ===" -ForegroundColor Cyan
            docker inspect $container --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
        }
    }

    exit $exitCode
}
finally {
    Pop-Location
}
