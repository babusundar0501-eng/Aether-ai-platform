@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.11 or newer.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto error
)
echo Installing or updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env. Add your model API key there, then run this file again.
  notepad ".env"
  pause
  exit /b 0
)
echo Starting AETHER at http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000
goto end
:error
echo Setup failed. Check the Python installation and internet connection.
pause
:end
endlocal
