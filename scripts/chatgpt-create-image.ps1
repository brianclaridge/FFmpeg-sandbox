<#
.SYNOPSIS
    Generate an image using ChatGPT web interface via Claude MCP browser automation.

.DESCRIPTION
    Automates ChatGPT's DALL-E image generation through the web interface using
    Claude Code's chrome MCP integration. Downloads the generated image to .data/gpt-images/.

.PARAMETER Prompt
    The image generation prompt to send to ChatGPT.

.PARAMETER OutputDir
    Output directory for generated images. Defaults to .data/gpt-images/

.EXAMPLE
    .\chatgpt-create-image.ps1 -Prompt "A cyberpunk city at sunset"

.EXAMPLE
    .\chatgpt-create-image.ps1 "A forest with bioluminescent mushrooms"
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Prompt,

    [Parameter(Mandatory = $false)]
    [string]$OutputDir = ".data/gpt-images"
)

$ErrorActionPreference = "Stop"

# Ensure output directory exists
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $RepoRoot $OutputDir
}
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created output directory: $OutputDir" -ForegroundColor Cyan
}

# Generate timestamp for unique filename
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$CleanedPrompt = $Prompt -replace '[^\w\s-]', '' -replace '\s+', '-'
$SafePrompt = $CleanedPrompt.Substring(0, [Math]::Min(50, $CleanedPrompt.Length))
$OutputFile = Join-Path $OutputDir "${Timestamp}_${SafePrompt}.png"

Write-Host "Generating image with ChatGPT..." -ForegroundColor Yellow
Write-Host "Prompt: $Prompt" -ForegroundColor Cyan
Write-Host "Output: $OutputFile" -ForegroundColor Cyan

# Claude Code prompt for browser automation
$ClaudePrompt = @"
Use the browser to generate an image with ChatGPT:

1. Navigate to https://chat.openai.com
2. If not logged in, wait for user to log in (pause and inform)
3. Start a new chat if needed
4. Enter this prompt: "$Prompt"
5. Wait for the image to be generated (may take 30-60 seconds)
6. Once the image appears, right-click and save it, or use the download button
7. Save the image to: $OutputFile

Important:
- If ChatGPT asks to confirm image generation, confirm it
- Wait for the full image to render before downloading
- Report success or failure with the file path
"@

# Invoke Claude with chrome MCP
try {
    $Result = claude --chrome -p $ClaudePrompt 2>&1
    Write-Host $Result

    if (Test-Path $OutputFile) {
        Write-Host "`nImage saved successfully: $OutputFile" -ForegroundColor Green
        return $OutputFile
    } else {
        Write-Warning "Image file not found at expected location: $OutputFile"
        Write-Host "Check if Claude saved it to a different location." -ForegroundColor Yellow
    }
} catch {
    Write-Error "Failed to generate image: $_"
    exit 1
}
