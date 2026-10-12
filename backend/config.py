import os
import shutil
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DOWNLOADS_DIR = Path("/tmp/downloads")
else:
    DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Binary Paths (ffmpeg, yt-dlp, deno)
LOCAL_BIN_DIR = Path(os.path.expanduser(r"~\.local\bin"))
if LOCAL_BIN_DIR.exists():
    os.environ["PATH"] = str(LOCAL_BIN_DIR) + os.pathsep + os.environ.get("PATH", "")

FFMPEG_PATH = shutil.which("ffmpeg") or str(LOCAL_BIN_DIR / "ffmpeg.exe")
FFPROBE_PATH = shutil.which("ffprobe") or str(LOCAL_BIN_DIR / "ffprobe.exe")

# Supported Platform Definitions
PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "icon": "youtube",
        "color": "#FF0000",
        "description": "Download YouTube Videos (4K, 1080p, 720p, 480p), Shorts, and Audio/MP3.",
        "domains": ["youtube.com", "youtu.be", "m.youtube.com"],
        "examples": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": False
    },
    "instagram": {
        "name": "Instagram",
        "icon": "instagram",
        "color": "#E1306C",
        "description": "Download Instagram Reels, Carousel Posts, Stories, Photos & MP3 Audio.",
        "domains": ["instagram.com", "instagr.am"],
        "examples": [
            "https://www.instagram.com/reel/...",
            "https://www.instagram.com/p/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    },
    "facebook": {
        "name": "Facebook",
        "icon": "facebook",
        "color": "#1877F2",
        "description": "Download Facebook Watch Videos, Reels, Public Page Videos & Audio/MP3.",
        "domains": ["facebook.com", "fb.watch", "m.facebook.com", "fb.com"],
        "examples": [
            "https://www.facebook.com/watch/?v=...",
            "https://fb.watch/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    },
    "reddit": {
        "name": "Reddit",
        "icon": "reddit",
        "color": "#FF4500",
        "description": "Download Reddit Videos with full merged audio, Galleries, Images & GIFs.",
        "domains": ["reddit.com", "redd.it", "v.redd.it"],
        "examples": [
            "https://www.reddit.com/r/memes/comments/...",
            "https://v.redd.it/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    },
    "x": {
        "name": "X / Twitter",
        "icon": "twitter",
        "color": "#000000",
        "description": "Download X / Twitter Videos in highest bitrate, GIFs, Photos & MP3.",
        "domains": ["twitter.com", "x.com", "t.co"],
        "examples": [
            "https://x.com/user/status/...",
            "https://twitter.com/user/status/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    },
    "tiktok": {
        "name": "TikTok",
        "icon": "music-2",
        "color": "#00F2FE",
        "description": "Download TikTok HD Videos without watermark, Slideshow photos & MP3 Sound.",
        "domains": ["tiktok.com", "vm.tiktok.com", "vt.tiktok.com"],
        "examples": [
            "https://www.tiktok.com/@user/video/...",
            "https://vm.tiktok.com/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    },
    "threads": {
        "name": "Threads",
        "icon": "at-sign",
        "color": "#101010",
        "description": "Download Threads Videos, Reels, Photos & Carousel posts.",
        "domains": ["threads.net"],
        "examples": [
            "https://www.threads.net/@user/post/..."
        ],
        "supports_mp3": True,
        "supports_video": True,
        "supports_images": True
    }
}
