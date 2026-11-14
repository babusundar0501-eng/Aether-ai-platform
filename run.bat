@echo off
title BLACKTIDE - Operation Breakwater
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "" http://localhost:8000
  py -m http.server 8000
) else (
  echo Python was not found. Install Python 3 or run a static web server.
  pause
)
