$ErrorActionPreference = 'Stop'
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (Test-Path $Python) {
    & $Python -m venv .venv
} else {
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $Launcher) { throw 'Python 3.12 was not found. Install Python 3.12 first.' }
    & py -3.12 -m venv .venv
}
if ($LASTEXITCODE -ne 0) { throw 'Could not create the virtual environment.' }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Could not upgrade pip.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host 'Created .env. Edit JWT_SECRET_KEY and ADMIN_PASSWORD before deployment.' -ForegroundColor Yellow
}
Write-Host 'Setup completed. Run .\run.ps1 to start the backend.' -ForegroundColor Green
