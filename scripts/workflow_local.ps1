[CmdletBinding()]
param(
    [switch]$Fix,
    [switch]$WithDocker,
    [switch]$SkipAudit,
    [switch]$SkipBandit
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "--> $Message" -ForegroundColor Yellow
}

function Resolve-RepoRoot {
    $scriptDir = $PSScriptRoot
    return (Resolve-Path (Join-Path $scriptDir "..")).Path
}

function Get-CommandPath {
    param(
        [string]$PreferredPath,
        [string]$FallbackCommand
    )

    if ($PreferredPath -and (Test-Path $PreferredPath)) {
        return $PreferredPath
    }

    $fallback = Get-Command $FallbackCommand -ErrorAction SilentlyContinue
    if ($fallback) {
        return $fallback.Source
    }

    throw "Commande introuvable : $FallbackCommand"
}

function Invoke-External {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Echec de la commande : $FilePath $($Arguments -join ' ')"
    }
}

function Test-ToolInstalled {
    param([string]$CommandName)
    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

$repoRoot = Resolve-RepoRoot
Set-Location $repoRoot

Write-Section "Workflow local pre-push"
Write-Host "Repository : $repoRoot"
Write-Host "Mode correction : $Fix"
Write-Host "Verification Docker : $WithDocker"

$venvPython = Join-Path $repoRoot "mon_env\Scripts\python.exe"
$venvRuff = Join-Path $repoRoot "mon_env\Scripts\ruff.exe"
$venvBlack = Join-Path $repoRoot "mon_env\Scripts\black.exe"
$venvPytest = Join-Path $repoRoot "mon_env\Scripts\pytest.exe"
$venvBandit = Join-Path $repoRoot "mon_env\Scripts\bandit.exe"
$venvPipAudit = Join-Path $repoRoot "mon_env\Scripts\pip-audit.exe"

$pythonCmd = Get-CommandPath -PreferredPath $venvPython -FallbackCommand "python"
$ruffCmd = Get-CommandPath -PreferredPath $venvRuff -FallbackCommand "ruff"
$blackCmd = Get-CommandPath -PreferredPath $venvBlack -FallbackCommand "black"
$pytestCmd = Get-CommandPath -PreferredPath $venvPytest -FallbackCommand "pytest"

if (-not $SkipBandit) {
    $banditCmd = Get-CommandPath -PreferredPath $venvBandit -FallbackCommand "bandit"
}

if (-not $SkipAudit) {
    $pipAuditCmd = Get-CommandPath -PreferredPath $venvPipAudit -FallbackCommand "pip-audit"
}

Write-Section "Preparation"
Write-Step "Verification des dossiers d'artefacts attendus par les tests"
New-Item -ItemType Directory -Force artifacts\models | Out-Null
New-Item -ItemType Directory -Force artifacts\metrics | Out-Null

if ($Fix) {
    Write-Section "Corrections automatiques"
    Write-Step "Ruff auto-fix"
    Invoke-External -FilePath $ruffCmd -Arguments @("check", ".", "--fix")

    Write-Step "Ruff format"
    Invoke-External -FilePath $ruffCmd -Arguments @("format", ".")

    Write-Step "Black format"
    Invoke-External -FilePath $blackCmd -Arguments @(".")
}

Write-Section "Controles Python"

Write-Step "Ruff lint"
Invoke-External -FilePath $ruffCmd -Arguments @("check", ".")

Write-Step "Ruff format check"
Invoke-External -FilePath $ruffCmd -Arguments @("format", "--check", ".")

Write-Step "Black format check"
Invoke-External -FilePath $blackCmd -Arguments @("--check", ".")

Write-Step "Pytest avec couverture"
Invoke-External -FilePath $pytestCmd -Arguments @("-v", "--cov=src")

if (-not $SkipBandit) {
    Write-Step "Bandit security scan"
    Invoke-External -FilePath $banditCmd -Arguments @(
        "-r",
        "src/prediction/",
        "src/common/",
        "backend/",
        "frontend/"
    )
}
else {
    Write-Host "Bandit ignore a la demande." -ForegroundColor DarkYellow
}

if (-not $SkipAudit) {
    Write-Step "pip-audit dependency scan"
    Invoke-External -FilePath $pipAuditCmd -Arguments @()
}
else {
    Write-Host "pip-audit ignore a la demande." -ForegroundColor DarkYellow
}

if ($WithDocker) {
    Write-Section "Controles Docker"

    if (-not (Test-ToolInstalled "docker")) {
        throw "Docker n'est pas installe ou n'est pas dans le PATH."
    }

    Write-Step "Build image backend"
    Invoke-External -FilePath "docker" -Arguments @(
        "build",
        "-t",
        "housing-backend:local-check",
        "-f",
        "backend/Dockerfile",
        "."
    )

    Write-Step "Build image frontend"
    Invoke-External -FilePath "docker" -Arguments @(
        "build",
        "-t",
        "housing-frontend:local-check",
        "-f",
        "frontend/Dockerfile",
        "."
    )

    Write-Step "Smoke test backend image"
    & docker rm -f backend-smoke-local *> $null
    & docker run -d --rm --name backend-smoke-local -e SKIP_MINIO_STARTUP=1 -p 8000:8000 housing-backend:local-check | Out-Null
    try {
        $backendReady = $false
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Seconds 2
            try {
                $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
                if ($response.status -eq "ok") {
                    $backendReady = $true
                    break
                }
            }
            catch {
            }
        }
        if (-not $backendReady) {
            docker logs backend-smoke-local
            throw "Smoke test backend echoue."
        }
    }
    finally {
        & docker rm -f backend-smoke-local *> $null
    }

    Write-Step "Smoke test frontend image"
    & docker rm -f frontend-smoke-local *> $null
    & docker run -d --rm --name frontend-smoke-local -e BACKEND_URL=http://127.0.0.1:8000 -p 8501:8501 housing-frontend:local-check | Out-Null
    try {
        $frontendReady = $false
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Seconds 2
            try {
                Invoke-WebRequest -Uri "http://127.0.0.1:8501" -UseBasicParsing | Out-Null
                $frontendReady = $true
                break
            }
            catch {
            }
        }
        if (-not $frontendReady) {
            docker logs frontend-smoke-local
            throw "Smoke test frontend echoue."
        }
    }
    finally {
        & docker rm -f frontend-smoke-local *> $null
    }

    if (Test-ToolInstalled "trivy") {
        Write-Step "Trivy scan backend image"
        Invoke-External -FilePath "trivy" -Arguments @(
            "image",
            "--severity",
            "HIGH,CRITICAL",
            "--ignore-unfixed",
            "--exit-code",
            "1",
            "housing-backend:local-check"
        )

        Write-Step "Trivy scan frontend image"
        Invoke-External -FilePath "trivy" -Arguments @(
            "image",
            "--severity",
            "HIGH,CRITICAL",
            "--ignore-unfixed",
            "--exit-code",
            "1",
            "housing-frontend:local-check"
        )
    }
    else {
        Write-Host "Trivy non installe localement : scan images saute." -ForegroundColor DarkYellow
    }
}

Write-Section "Termine"
Write-Host "Tous les controles demandes sont passes avec succes." -ForegroundColor Green
Write-Host "Tu peux push en confiance." -ForegroundColor Green
