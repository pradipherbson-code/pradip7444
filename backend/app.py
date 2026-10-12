import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import PLATFORMS, DOWNLOADS_DIR, FFMPEG_PATH
from backend.downloader import (
    extract_media_info,
    perform_download,
    download_image_direct,
    cleanup_old_files
)

# Initialize FastAPI
app = FastAPI(
    title="OmniStream Social Media Downloader API",
    description="Universal Multi-Platform Media & MP3 Downloader",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class FetchInfoRequest(BaseModel):
    url: str
    platform: Optional[str] = None

class DownloadRequest(BaseModel):
    url: str
    type: str = "video"  # 'video', 'audio', 'image'
    quality: str = "best"
    title: Optional[str] = None
    image_url: Optional[str] = None

# In-memory tracking for download files
download_registry = {}

@app.get("/api/health")
def health_check():
    """Verify backend status and media tool availability."""
    cleanup_old_files()
    return {
        "status": "healthy",
        "ffmpeg_available": bool(FFMPEG_PATH and os.path.exists(FFMPEG_PATH)),
        "supported_platforms": list(PLATFORMS.keys()),
        "downloads_dir": str(DOWNLOADS_DIR)
    }

@app.get("/api/platforms")
def get_platforms():
    """Returns platform metadata, supported features, and sample links."""
    return PLATFORMS

@app.post("/api/fetch-info")
def fetch_info(req: FetchInfoRequest):
    """
    Inspects URL and extracts title, thumbnails, preview streams,
    video quality resolutions, MP3 options, and multi-media items.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
    
    result = extract_media_info(url, req.platform)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    
    return result

@app.post("/api/download")
def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Downloads media, converts to MP3 if audio is requested, and prepares it for browser download.
    """
    cleanup_old_files()

    if req.type == "image":
        target_img_url = req.image_url or req.url
        res = download_image_direct(target_img_url, req.title)
    else:
        res = perform_download(
            url=req.url,
            download_type=req.type,
            quality=req.quality,
            custom_title=req.title
        )

    if not res.get("success"):
        return JSONResponse(status_code=400, content=res)

    file_key = os.path.basename(res["filepath"])
    download_registry[file_key] = {
        "filepath": res["filepath"],
        "filename": res["filename"],
        "size": res.get("size_bytes", 0),
        "type": res.get("type", req.type)
    }

    return {
        "success": True,
        "download_id": file_key,
        "filename": res["filename"],
        "size": res.get("size_bytes", 0),
        "type": res.get("type", req.type),
        "download_url": f"/api/file/{file_key}"
    }

@app.get("/api/file/{file_key}")
def get_download_file(file_key: str, background_tasks: BackgroundTasks):
    """
    Streams the downloaded file as a browser attachment download.
    """
    record = download_registry.get(file_key)
    target_path = DOWNLOADS_DIR / file_key

    if not target_path.exists():
        if record and os.path.exists(record["filepath"]):
            target_path = Path(record["filepath"])
        else:
            raise HTTPException(status_code=404, detail="File not found or has expired.")

    filename = record["filename"] if record else target_path.name
    
    # Determine media mime type
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".mp4": "video/mp4",
        ".mp3": "audio/mpeg",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".webm": "video/webm",
        ".gif": "image/gif"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(target_path),
        filename=filename,
        media_type=media_type
    )

# Static frontend directory setup
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
