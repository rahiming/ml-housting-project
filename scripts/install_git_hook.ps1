[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "Installation du hook pre-push pour ce depot..." -ForegroundColor Cyan

git config core.hooksPath .githooks
git config alias.workflow-local "!powershell -ExecutionPolicy Bypass -File scripts/workflow_local.ps1"

Write-Host "Hook Git active via .githooks/pre-push" -ForegroundColor Green
Write-Host "Alias Git ajoute : git workflow-local" -ForegroundColor Green
