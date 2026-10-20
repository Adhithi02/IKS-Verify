param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("setup", "dev", "serve", "test", "lint")]
    [string]$Target
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Npm = "C:\Program Files\nodejs\npm.cmd"

if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Run: py -3.11 -m venv .venv"
}

switch ($Target) {
    "setup" {
        & $Python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
        Push-Location (Join-Path $ProjectRoot "web")
        try { & $Npm install } finally { Pop-Location }
    }
    "dev" {
        Write-Host "Start the API in one PowerShell window:"
        Write-Host "  .\scripts\dev.ps1 serve"
        Write-Host "Then start Vite in another:"
        Write-Host "  Set-Location .\web; & 'C:\Program Files\nodejs\npm.cmd' run dev"
    }
    "serve" { & $Python -m iks_verify.serve }
    "test" {
        $env:LLM_PROVIDER = "mock"
        $env:CORPUS_PATH = "tests/fixtures/corpus.jsonl"
        # Keep pytest's temporary files inside the repository. This avoids
        # protected Windows AppContainer temp folders used by some terminals.
        & $Python -m pytest -q -p no:cacheprovider --basetemp (Join-Path $ProjectRoot ".pytest_tmp")
        Push-Location (Join-Path $ProjectRoot "web")
        try { & $Npm test } finally { Pop-Location }
    }
    "lint" {
        & $Python -m ruff check $ProjectRoot
        Push-Location (Join-Path $ProjectRoot "web")
        try { & $Npm run lint } finally { Pop-Location }
    }
}
