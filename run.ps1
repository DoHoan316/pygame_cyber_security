$ErrorActionPreference = 'Stop'
if (-not (Test-Path .\.venv\Scripts\python.exe)) { throw 'Virtual environment missing. Run .\setup.ps1 first.' }
if (-not (Test-Path .env)) { throw '.env missing. Run .\setup.ps1 first.' }
& .\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Check DATABASE_URL in .env.' }
& .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 --env-file .env
