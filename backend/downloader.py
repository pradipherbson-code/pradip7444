import os
import uuid
import glob
import time
from typing import Dict, Any, Optional, List
import requests
import yt_dlp

from backend.config import DOWNLOADS_DIR, FFMPEG_PATH, FFPROBE_PATH
from backend.extractors import (
    detect_platform,
    sanitize_filename,
    parse_direct_image_url,
    parse_instagram_custom,
    parse_reddit_custom
)
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path

def sanitize_media_url(url: str) -> str:
    """Removes tracking query parameters like ?si=... from YouTube/social URLs."""
    clean = url.strip()
    if "youtu.be/" in clean or "youtube.com/" in clean:
        parsed = urlparse(clean)
        qs = parse_qs(parsed.query)
        for param in ["si", "feature", "pp"]:
            qs.pop(param, None)
        new_query = urlencode(qs, doseq=True)
        clean = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    return clean

def get_ydl_base_opts(fallback_client: bool = False) -> Dict[str, Any]:
    """Base options for yt-dlp extraction and downloading with challenge solver and anti-bot bypass."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "ffmpeg_location": FFMPEG_PATH,
        "socket_timeout": 20,
        "retries": 5,
        "remote_components": ["ejs:github"],
    }

    # Auto-load cookies.txt if present
    cookie_paths = [
        Path(__file__).resolve().parent.parent / "cookies.txt",
        Path(__file__).resolve().parent / "cookies.txt",
        Path.cwd() / "cookies.txt"
    ]
    for cp in cookie_paths:
        if cp.exists():
            opts["cookiefile"] = str(cp)
            break

    if fallback_client:
        # Client that bypasses "Sign in to confirm you're not a bot"
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["android", "ios", "mweb"],
                "player_skip": ["webpage", "configs"]
            }
        }
    else:
        # Robust multi-client list
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["web", "tv_embedded", "android", "ios", "mweb"]
            }
        }

    return opts

def extract_media_info(url: str, requested_platform: Optional[str] = None) -> Dict[str, Any]:
    """
    Extracts all metadata, video quality options, audio/MP3 stream options,
    and image attachments from any supported URL.
    """
    clean_url = sanitize_media_url(url)
    platform = requested_platform or detect_platform(clean_url)

    # 1. Check for direct image or Reddit media link first
    direct_img = parse_direct_image_url(clean_url)
    if direct_img:
        return direct_img

    # 2. Check for Instagram posts (photos, carousels, reels) using Instaloader first
    if platform == "instagram" or "instagram.com" in clean_url or "instagr.am" in clean_url:
        ig_custom = parse_instagram_custom(clean_url)
        if ig_custom:
            return ig_custom

    # 3. Check for direct Reddit gallery / image post
    if platform == "reddit" or "reddit.com" in clean_url or "redd.it" in clean_url:
        custom_reddit = parse_reddit_custom(clean_url)
        if custom_reddit:
            return custom_reddit

    # 4. Standard yt-dlp extraction with anti-bot fallback
    ydl_opts = get_ydl_base_opts(fallback_client=False)
    ydl_opts["skip_download"] = True

    try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
        except Exception as first_err:
            err_str = str(first_err).lower()
            if any(k in err_str for k in ["sign in", "not a bot", "bot", "sabr", "429"]):
                # Fallback to Android/iOS client which bypasses bot challenges
                fb_opts = get_ydl_base_opts(fallback_client=True)
                fb_opts["skip_download"] = True
                with yt_dlp.YoutubeDL(fb_opts) as ydl:
                    info = ydl.extract_info(clean_url, download=False)
            else:
                raise first_err

        if not info:
            raise ValueError("Could not retrieve media info from this link.")

        # Check if it returned a multi-entry playlist/carousel
        if "entries" in info and info["entries"]:
            entries = list(info["entries"])
            items = []
            for idx, entry in enumerate(entries):
                if not entry:
                    continue
                item_type = "video" if entry.get("vcodec") and entry.get("vcodec") != "none" else "image"
                items.append({
                    "index": idx + 1,
                    "type": item_type,
                    "url": (entry.get("url") or entry.get("webpage_url") or "").replace("&amp;", "&"),
                    "thumbnail": (entry.get("thumbnail") or "").replace("&amp;", "&"),
                    "title": entry.get("title") or f"Item {idx + 1}"
                })
            
            title = info.get("title") or entries[0].get("title") or f"{platform.capitalize()} Post"
            thumb = (entries[0].get("thumbnail") or info.get("thumbnail") or "").replace("&amp;", "&")
            author = entries[0].get("uploader") or info.get("uploader") or f"{platform.capitalize()} User"

            return {
                "success": True,
                "platform": platform,
                "title": title,
                "author": author,
                "thumbnail": thumb,
                "media_type": "carousel",
                "is_video": any(i["type"] == "video" for i in items),
                "items": items,
                "duration": entries[0].get("duration"),
                "formats": build_quality_formats(entries[0], platform)
            }

        # Single media item
        is_video = (
            info.get("vcodec") is not None and info.get("vcodec") != "none"
        ) or (
            any(f.get("vcodec") not in (None, "none") for f in info.get("formats", []))
        )

        title = info.get("title") or f"{platform.capitalize()} Media"
        thumbnail = (info.get("thumbnail") or (info.get("thumbnails")[-1]["url"] if info.get("thumbnails") else None) or "").replace("&amp;", "&")
        author = info.get("uploader") or info.get("channel") or info.get("creator") or f"{platform.capitalize()} Creator"
        duration = info.get("duration")

        # Check for direct image or single photo post
        if not is_video and thumbnail:
            return {
                "success": True,
                "platform": platform,
                "title": title,
                "author": author,
                "thumbnail": thumbnail,
                "media_type": "image",
                "is_video": False,
                "items": [{"type": "image", "url": (info.get("url") or thumbnail).replace("&amp;", "&"), "width": info.get("width"), "height": info.get("height")}],
                "duration": None,
                "formats": []
            }

        formats = build_quality_formats(info, platform)

        # Direct preview stream URL if available
        preview_url = None
        if is_video:
            for f in reversed(info.get("formats", [])):
                if f.get("vcodec") != "none" and f.get("acodec") != "none" and f.get("url"):
                    if "m3u8" not in f.get("url", ""):
                        preview_url = f.get("url")
                        break

        # Always provide thumbnail as an image item so the user can download it
        items = []
        if thumbnail:
            items.append({
                "index": 1,
                "type": "image",
                "url": thumbnail,
                "thumbnail": thumbnail,
                "title": f"{title} - Cover / Thumbnail"
            })

        return {
            "success": True,
            "platform": platform,
            "title": title,
            "author": author,
            "thumbnail": thumbnail,
            "media_type": "video" if is_video else "image",
            "is_video": is_video,
            "duration": duration,
            "preview_url": preview_url,
            "items": items,
            "formats": formats
        }

    except Exception as e:
        error_msg = str(e)
        # If yt-dlp threw "There is no video in this post", try Instagram custom parser
        if "no video" in error_msg.lower() and ("instagram.com" in clean_url or platform == "instagram"):
            ig_custom = parse_instagram_custom(clean_url)
            if ig_custom:
                return ig_custom

        if "ERROR:" in error_msg:
            error_msg = error_msg.split("ERROR:", 1)[1].strip()
        return {
            "success": False,
            "platform": platform,
            "error": error_msg or "Failed to extract media. Please verify the URL is public and valid."
        }

def build_quality_formats(info: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
    """Generates clean quality options for video and MP3 audio."""
    formats = []
    raw_formats = info.get("formats", [])

    # Always provide Best Quality Video
    formats.append({
        "id": "best",
        "label": "Best Quality (MP4)",
        "quality": "Best Available",
        "type": "video",
        "ext": "mp4",
        "recommended": True
    })

    # Available resolutions
    heights_found = set()
    for f in raw_formats:
        h = f.get("height")
        if h and h in (2160, 1440, 1080, 720, 480, 360, 240) and h not in heights_found:
            heights_found.add(h)

    # Sort resolutions descending
    for h in sorted(heights_found, reverse=True):
        label_text = f"{h}p Full HD" if h >= 1080 else f"{h}p HD" if h >= 720 else f"{h}p SD"
        formats.append({
            "id": f"res_{h}",
            "label": f"{label_text} (MP4)",
            "quality": f"{h}p",
            "height": h,
            "type": "video",
            "ext": "mp4",
            "recommended": False
        })

    # If heights weren't granularly reported, provide standard presets
    if len(heights_found) == 0:
        formats.extend([
            {"id": "res_1080", "label": "1080p Full HD (MP4)", "quality": "1080p", "type": "video", "ext": "mp4", "recommended": False},
            {"id": "res_720", "label": "720p HD (MP4)", "quality": "720p", "type": "video", "ext": "mp4", "recommended": False},
            {"id": "res_480", "label": "480p SD (MP4)", "quality": "480p", "type": "video", "ext": "mp4", "recommended": False},
        ])

    # Pure Audio / MP3 Option
    formats.append({
        "id": "mp3_320",
        "label": "Audio Only - High Quality MP3 (320 kbps)",
        "quality": "320 kbps MP3",
        "type": "audio",
        "ext": "mp3",
        "is_audio_only": True,
        "recommended": False
    })
    formats.append({
        "id": "mp3_192",
        "label": "Audio Only - Standard MP3 (192 kbps)",
        "quality": "192 kbps MP3",
        "type": "audio",
        "ext": "mp3",
        "is_audio_only": True,
        "recommended": False
    })

    return formats

def perform_download(
    url: str,
    download_type: str = "video",
    quality: str = "best",
    custom_title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Downloads video or extracts audio as MP3, returning the local file path and filename.
    """
    file_id = uuid.uuid4().hex[:10]
    out_template = str(DOWNLOADS_DIR / f"{file_id}_%(title).60s.%(ext)s")

    ydl_opts = get_ydl_base_opts()
    ydl_opts["outtmpl"] = out_template

    is_audio = (download_type == "audio" or "mp3" in quality or download_type == "mp3")

    if is_audio:
        # Extract audio and convert to MP3 using ffmpeg
        bitrate = "320" if "320" in quality else "192"
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": bitrate,
        }]
    else:
        # Video download
        ydl_opts["merge_output_format"] = "mp4"
        if quality.startswith("res_"):
            height = quality.replace("res_", "")
            ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        elif quality in ("1080", "720", "480", "360"):
            ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        else:
            ydl_opts["format"] = "bestvideo+bestaudio/best"

    clean_download_url = sanitize_media_url(url)

    try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(clean_download_url, download=True)
        except Exception as first_dl_err:
            err_str = str(first_dl_err).lower()
            if any(k in err_str for k in ["sign in", "not a bot", "bot", "sabr", "429"]):
                # Retry download with Android/iOS fallback client
                fb_opts = get_ydl_base_opts(fallback_client=True)
                fb_opts["outtmpl"] = out_template
                if is_audio:
                    bitrate = "320" if "320" in quality else "192"
                    fb_opts["format"] = "bestaudio/best"
                    fb_opts["postprocessors"] = [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate,
                    }]
                else:
                    fb_opts["merge_output_format"] = "mp4"
                    fb_opts["format"] = "best/bestvideo+bestaudio"

                with yt_dlp.YoutubeDL(fb_opts) as ydl:
                    meta = ydl.extract_info(clean_download_url, download=True)
            else:
                raise first_dl_err

        title = custom_title or (meta.get("title") if meta else "media")
        sanitized = sanitize_filename(title)
        ext = "mp3" if is_audio else "mp4"

        pattern = str(DOWNLOADS_DIR / f"{file_id}_*")
        matches = glob.glob(pattern)
        if not matches:
            raise FileNotFoundError("Downloaded file could not be located on disk.")
        
        filepath = matches[0]
        actual_ext = os.path.splitext(filepath)[1].lstrip(".") or ext
        final_filename = f"{sanitized}.{actual_ext}"

        return {
            "success": True,
            "filepath": filepath,
            "filename": final_filename,
            "title": title,
            "size_bytes": os.path.getsize(filepath),
            "type": "audio" if is_audio else "video"
        }
    except Exception as e:
        error_msg = str(e)
        if "ERROR:" in error_msg:
            error_msg = error_msg.split("ERROR:", 1)[1].strip()
        return {
            "success": False,
            "error": error_msg or "Failed to download media."
        }

def download_image_direct(image_url: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Downloads any direct image, CDN URL, or photo stream, saving it with proper extension.
    """
    if not image_url or not image_url.strip():
        return {"success": False, "error": "No image URL provided."}

    clean_img_url = image_url.strip().replace("&amp;", "&")
    file_id = uuid.uuid4().hex[:10]
    sanitized = sanitize_filename(title or "image")
    
    # Infer default extension
    ext = "jpg"
    lower_url = clean_img_url.split("?")[0].lower()
    if ".png" in lower_url:
        ext = "png"
    elif ".webp" in lower_url:
        ext = "webp"
    elif ".gif" in lower_url:
        ext = "gif"
    elif ".svg" in lower_url:
        ext = "svg"
    elif ".jpeg" in lower_url or ".jpg" in lower_url:
        ext = "jpg"

    # Set appropriate referer and user-agent
    referer = "https://www.google.com/"
    if "fbcdn.net" in clean_img_url or "cdninstagram.com" in clean_img_url:
        referer = "https://www.instagram.com/"
    elif "redd.it" in clean_img_url or "reddit.com" in clean_img_url:
        referer = "https://www.reddit.com/"
    elif "twimg.com" in clean_img_url or "twitter.com" in clean_img_url or "x.com" in clean_img_url:
        referer = "https://twitter.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": referer,
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
    }

    try:
        resp = requests.get(clean_img_url, headers=headers, stream=True, timeout=25)
        resp.raise_for_status()

        # Check content-type header for true image format
        content_type = resp.headers.get("content-type", "").lower()
        if "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"
        elif "gif" in content_type:
            ext = "gif"
        elif "jpeg" in content_type or "jpg" in content_type:
            ext = "jpg"

        filename = f"{sanitized}_{file_id}.{ext}"
        filepath = DOWNLOADS_DIR / filename

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        final_filename = f"{sanitized}.{ext}"
        return {
            "success": True,
            "filepath": str(filepath),
            "filename": final_filename,
            "size_bytes": os.path.getsize(filepath),
            "type": "image"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to download image: {str(e)}"
        }

def cleanup_old_files(max_age_seconds: int = 1800):
    """Clean up downloaded files older than max_age_seconds (30 minutes)."""
    now = time.time()
    try:
        for p in DOWNLOADS_DIR.iterdir():
            if p.is_file() and (now - p.stat().st_mtime > max_age_seconds):
                try:
                    p.unlink()
                except Exception:
                    pass
    except Exception:
        pass
