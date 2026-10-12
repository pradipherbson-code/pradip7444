---
title: OmniStream By Pradip
emoji: ⚡
colorFrom: indigo
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# ⚡ OmniStream By Pradip — Multi-Platform Social Media & MP3 Downloader

A full-stack, responsive web application to download videos, images, and audio from all major social platforms, featuring dedicated sections for each platform and high-fidelity MP3 audio conversion.

---

## 🌟 Supported Platforms & Features

| Platform | Video Download | Image / Carousel | MP3 Audio Only | Special Capabilities |
| :--- | :---: | :---: | :---: | :--- |
| **YouTube** | ✅ Up to 4K / 1080p | ❌ | ✅ 320 kbps / 192 kbps | Regular Videos, Shorts, MP3 Music |
| **Instagram** | ✅ Reels & Videos | ✅ Posts & Carousels | ✅ Audio Track | Single reels, carousel photo albums |
| **TikTok** | ✅ HD No Watermark | ✅ Slideshows | ✅ Viral Audio | Clean MP4, direct original soundtrack |
| **Reddit** | ✅ Full Sound Merged | ✅ Image Galleries | ✅ Audio | Audio/video streams merged via FFmpeg |
| **Facebook** | ✅ 1080p / 720p HD | ✅ Photos | ✅ MP3 Soundtrack | Facebook Watch, Reels, Page Videos |
| **X / Twitter** | ✅ Highest Bitrate | ✅ Attached Photos | ✅ Audio | Videos, loopable GIFs, multi-images |
| **Threads** | ✅ Video Clips | ✅ Photo Galleries | ✅ Audio | Threads posts, reels, and photos |
| **Universal Mode**| ✅ Auto-detected | ✅ Auto-detected | ✅ Universal | Paste any URL; engine routes automatically |

---

## 🚀 Key Highlights

1. **Dedicated Sections per App**:
   - Easily switch between **YouTube**, **Instagram**, **TikTok**, **Facebook**, **Reddit**, **X (Twitter)**, **Threads**, or the **Universal** tab.
2. **"Only MP3 in Videos" Audio Extraction**:
   - Integrated FFmpeg audio processor converts any video into high-fidelity standalone MP3 audio (320 kbps HQ or 192 kbps standard).
3. **Multi-Resolution Video Selector**:
   - Download videos in Best Available, 1080p Full HD, 720p HD, 480p, or 360p.
4. **Gallery & Carousel Viewer**:
   - Multi-item posts (Reddit galleries, Instagram carousels, TikTok slideshows) display thumbnails and allow downloading individual items.
5. **Download History**:
   - Sliding side drawer keeps track of recent downloads with file sizes, timestamps, and one-click re-download.
6. **Zero Client Setup Needed**:
   - Single-file backend with fast streaming and automated temporary file cleanup.

---

## 💻 How to Run

### Method 1: Windows 1-Click Launch (Recommended)
Double-click `start.bat` inside the `social-media-downloader` directory.

### Method 2: Command Line (using `uv`)
```powershell
cd "social-media-downloader"
$env:PATH = "$HOME\.local\bin;" + $env:PATH
uv run --python 3.12 --with fastapi --with uvicorn --with yt-dlp --with requests --with python-multipart python run.py
```

The application will start at **`http://localhost:5000`** and automatically open your default browser.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, yt-dlp, FFmpeg
- **Frontend**: Responsive HTML5, Tailwind CSS, Lucide Icons, Glassmorphic UI, Vanilla ES6+
- **Audio Processing**: FFmpeg with `libmp3lame` encoder

---

## 📡 API Reference

- `POST /api/fetch-info` — Extracts title, duration, author, thumbnail, format options, and image attachments.
- `POST /api/download` — Prepares video download, MP3 conversion, or photo extraction.
- `GET /api/file/{file_key}` — Streams the file as a browser attachment download.
- `GET /api/platforms` — Lists supported platforms and metadata.
- `GET /api/health` — Checks backend and FFmpeg status.
