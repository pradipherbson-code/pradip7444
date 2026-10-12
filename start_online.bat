@echo off
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

echo ================================================================
echo    Launching OmniStream with Live Public HTTPS Internet Access
echo ================================================================

start "OmniStream Backend Server" cmd /c "uv run --python 3.12 --with fastapi --with uvicorn --with yt-dlp --with requests --with python-multipart --with instaloader --with beautifulsoup4 python run.py"

echo Waiting for backend server to initialize...
timeout /t 3 /nobreak >nul

echo.
echo ================================================================
echo  Your Public HTTPS Link will appear below. Share or open on mobile!
echo ================================================================
echo.

cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
