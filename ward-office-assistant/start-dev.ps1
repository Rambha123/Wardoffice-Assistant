docker compose up -d postgres chromadb
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$PSScriptRoot\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$PSScriptRoot\frontend'; npm run dev"
