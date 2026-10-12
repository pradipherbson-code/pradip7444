@echo off
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

echo =========================================================
echo    Launching OmniStream Social Media & MP3 Downloader
echo =========================================================

uv run --python 3.12 --with fastapi --with uvicorn --with yt-dlp --with requests --with python-multipart --with instaloader --with beautifulsoup4 python run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server exited with an error.
    pause
)
