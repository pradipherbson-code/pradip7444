import os
import sys
import shutil
import webbrowser
import subprocess
from pathlib import Path

# Add local bin to PATH for FFmpeg and Deno
LOCAL_BIN = Path(os.path.expanduser(r"~\.local\bin"))
if LOCAL_BIN.exists():
    os.environ["PATH"] = str(LOCAL_BIN) + os.pathsep + os.environ.get("PATH", "")

# Current directory
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def main():
    print("=" * 65)
    print("  [*] Starting OmniStream Multi-Platform Downloader Server")
    print("=" * 65)
    
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        print(f"  [+] FFmpeg located: {ffmpeg_bin}")
    else:
        print("  [!] Warning: FFmpeg not detected on PATH. Audio MP3 conversions may fail.")

    port = 5000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    print(f"  [+] Web App URL: {url}")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server anytime.\n")

    # Open browser after a brief delay
    def open_web():
        import time
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    import threading
    threading.Thread(target=open_web, daemon=True).start()

    import uvicorn
    uvicorn.run("backend.app:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
