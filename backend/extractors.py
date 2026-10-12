import re
import urllib.parse
from typing import Dict, Any, Optional, List
import requests
from backend.config import PLATFORMS

def detect_platform(url: str) -> str:
    """Identify platform from the given URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if hostname.startswith("www."):
            hostname = hostname[4:]
        
        for key, pdata in PLATFORMS.items():
            for domain in pdata["domains"]:
                if hostname == domain or hostname.endswith("." + domain):
                    return key
        return "universal"
    except Exception:
        return "universal"

def sanitize_filename(name: str, max_len: int = 60) -> str:
    """Sanitize string to be safe for filenames across Windows/Linux/macOS."""
    if not name:
        return "media_download"
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r'[\r\n\t]+', " ", clean)
    clean = re.sub(r'\s+', "_", clean).strip(" ._")
    if len(clean) > max_len:
        clean = clean[:max_len].rstrip(" ._")
    return clean or "media_download"

def parse_direct_image_url(url: str) -> Optional[Dict[str, Any]]:
    """
    Detects and unpacks direct image links, Reddit media links, and image hosting links.
    e.g. https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2F0volk2nyizuh1.jpeg
    """
    clean = url.strip()
    
    # Check for reddit.com/media?url=...
    if "reddit.com/media" in clean or "media?url=" in clean:
        try:
            parsed = urllib.parse.urlparse(clean)
            qs = urllib.parse.parse_qs(parsed.query)
            if "url" in qs and qs["url"]:
                real_img_url = urllib.parse.unquote(qs["url"][0]).replace("&amp;", "&")
                return {
                    "success": True,
                    "platform": "reddit",
                    "title": "Reddit Image",
                    "author": "Reddit",
                    "thumbnail": real_img_url,
                    "media_type": "image",
                    "is_video": False,
                    "items": [{"type": "image", "url": real_img_url}],
                    "duration": None,
                    "formats": []
                }
        except Exception:
            pass

    # Direct image hosting domains or image extensions
    clean_no_query = clean.split("?")[0].lower()
    is_direct_img = (
        clean_no_query.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg")) or
        "i.redd.it" in clean or
        "preview.redd.it" in clean or
        "pbs.twimg.com/media" in clean or
        "i.imgur.com" in clean
    )

    if is_direct_img:
        platform = detect_platform(clean)
        real_url = clean.replace("&amp;", "&")
        return {
            "success": True,
            "platform": platform if platform != "universal" else "image",
            "title": f"{platform.capitalize()} Image",
            "author": f"{platform.capitalize()} Media",
            "thumbnail": real_url,
            "media_type": "image",
            "is_video": False,
            "items": [{"type": "image", "url": real_url}],
            "duration": None,
            "formats": []
        }

    return None

def parse_instagram_custom(url: str) -> Optional[Dict[str, Any]]:
    """
    Specialized extractor for Instagram photo, carousel, and reel posts using Instaloader.
    Solves 'There is no video in this post' and 'No video formats found'.
    """
    try:
        # Extract shortcode from /p/SHORTCODE/, /reel/SHORTCODE/, /tv/SHORTCODE/
        match = re.search(r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)', url)
        if not match:
            return None
        shortcode = match.group(1)

        import instaloader
        L = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            quiet=True
        )
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        title = (post.caption or "").strip()
        if title:
            # First line of caption as title
            title = title.split("\n")[0][:80]
        else:
            title = f"Instagram Post by @{post.owner_username}"

        author = f"@{post.owner_username}" if post.owner_username else "Instagram User"

        # Check for Carousel / Sidecar
        if post.typename == "GraphSidecar":
            items = []
            for idx, node in enumerate(post.get_sidecar_nodes()):
                item_url = (node.video_url if node.is_video else node.display_url) or node.display_url
                items.append({
                    "index": idx + 1,
                    "type": "video" if node.is_video else "image",
                    "url": item_url.replace("&amp;", "&"),
                    "thumbnail": node.display_url.replace("&amp;", "&"),
                    "title": f"{title} - Item {idx + 1}"
                })
            
            first_thumb = items[0]["thumbnail"] if items else post.url
            return {
                "success": True,
                "platform": "instagram",
                "title": title,
                "author": author,
                "thumbnail": first_thumb,
                "media_type": "carousel",
                "is_video": any(i["type"] == "video" for i in items),
                "items": items,
                "duration": None,
                "formats": []
            }

        # Check if single video post
        if post.is_video:
            video_url = post.video_url
            thumb_url = post.url.replace("&amp;", "&")
            return {
                "success": True,
                "platform": "instagram",
                "title": title,
                "author": author,
                "thumbnail": thumb_url,
                "media_type": "video",
                "is_video": True,
                "preview_url": video_url,
                "duration": getattr(post, "video_duration", None),
                "items": [{"type": "image", "url": thumb_url, "title": "Thumbnail"}],
                "formats": [
                    {
                        "id": "best",
                        "label": "Original Quality (MP4)",
                        "quality": "Best",
                        "type": "video",
                        "ext": "mp4",
                        "recommended": True
                    },
                    {
                        "id": "mp3_320",
                        "label": "Extract MP3 Audio (320 kbps)",
                        "quality": "320 kbps MP3",
                        "type": "audio",
                        "ext": "mp3",
                        "is_audio_only": True,
                        "recommended": False
                    }
                ]
            }

        # Single Photo Post (GraphImage)
        photo_url = post.url.replace("&amp;", "&")
        return {
            "success": True,
            "platform": "instagram",
            "title": title,
            "author": author,
            "thumbnail": photo_url,
            "media_type": "image",
            "is_video": False,
            "items": [{"type": "image", "url": photo_url, "title": "Full Resolution Photo"}],
            "duration": None,
            "formats": []
        }

    except Exception:
        # Fallback to OpenGraph scrape
        try:
            return parse_instagram_opengraph(url)
        except Exception:
            return None

def parse_instagram_opengraph(url: str) -> Optional[Dict[str, Any]]:
    """Fallback scraping for Instagram using OpenGraph meta tags."""
    clean_url = url.split("?")[0].rstrip("/") + "/embed/captioned/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    r = requests.get(clean_url, headers=headers, timeout=8)
    if r.status_code != 200:
        return None

    # Search for embedded image src
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    img_tag = soup.find("img", class_="EmbeddedMediaImage") or soup.find("img")
    if img_tag and img_tag.get("src"):
        img_url = img_tag.get("src").replace("&amp;", "&")
        return {
            "success": True,
            "platform": "instagram",
            "title": "Instagram Photo",
            "author": "Instagram Creator",
            "thumbnail": img_url,
            "media_type": "image",
            "is_video": False,
            "items": [{"type": "image", "url": img_url}],
            "duration": None,
            "formats": []
        }
    return None

def parse_reddit_custom(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch Reddit post json directly to extract full galleries and native images.
    Reddit's public JSON API is fast and doesn't require auth.
    """
    try:
        clean_url = url.split("?")[0].rstrip("/") + ".json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(clean_url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, list) or len(data) == 0:
            return None
        
        post = data[0]["data"]["children"][0]["data"]
        title = post.get("title", "Reddit Post")
        author = post.get("author", "Reddit User")
        media_items: List[Dict[str, Any]] = []

        # Check for gallery
        if post.get("is_gallery") and "media_metadata" in post:
            media_meta = post.get("media_metadata", {})
            gallery_data = post.get("gallery_data", {}).get("items", [])
            for item in gallery_data:
                media_id = item.get("media_id")
                if media_id in media_meta:
                    m = media_meta[media_id]
                    s = m.get("s", {})
                    img_url = s.get("u") or s.get("gif")
                    if img_url:
                        img_url = img_url.replace("&amp;", "&")
                        media_items.append({
                            "type": "image",
                            "url": img_url,
                            "width": s.get("x"),
                            "height": s.get("y")
                        })
        # Check for single image post
        elif post.get("post_hint") == "image" or post.get("url", "").endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            img_url = post.get("url", "").replace("&amp;", "&")
            media_items.append({
                "type": "image",
                "url": img_url,
                "width": post.get("preview", {}).get("images", [{}])[0].get("source", {}).get("width"),
                "height": post.get("preview", {}).get("images", [{}])[0].get("source", {}).get("height")
            })

        if media_items:
            return {
                "success": True,
                "platform": "reddit",
                "title": title,
                "author": f"u/{author}",
                "thumbnail": media_items[0]["url"],
                "media_type": "gallery" if len(media_items) > 1 else "image",
                "is_video": False,
                "items": media_items,
                "duration": None,
                "formats": []
            }
        return None
    except Exception:
        return None
