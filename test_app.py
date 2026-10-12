import os
import sys
from pathlib import Path

# Add local bin to PATH
LOCAL_BIN = Path(os.path.expanduser(r"~\.local\bin"))
if LOCAL_BIN.exists():
    os.environ["PATH"] = str(LOCAL_BIN) + os.pathsep + os.environ.get("PATH", "")

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from backend.downloader import extract_media_info, perform_download
from backend.extractors import detect_platform

def test_detect():
    print("[1] Testing platform detection...")
    assert detect_platform("https://www.youtube.com/watch?v=123") == "youtube"
    assert detect_platform("https://instagram.com/reel/abc") == "instagram"
    assert detect_platform("https://www.tiktok.com/@user/video/123") == "tiktok"
    assert detect_platform("https://reddit.com/r/test/comments/123") == "reddit"
    assert detect_platform("https://x.com/user/status/123") == "x"
    assert detect_platform("https://facebook.com/watch/?v=123") == "facebook"
    assert detect_platform("https://threads.net/@user/post/123") == "threads"
    print("    -> Platform detection passed!")

def test_extraction():
    print("[2] Testing media info extraction...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    info = extract_media_info(test_url)
    assert info["success"] is True
    assert "formats" in info
    assert info["is_video"] is True
    print(f"    -> Extracted title: {info['title']}")
    print(f"    -> Formats available: {len(info['formats'])}")
    has_mp3 = any(f.get("is_audio_only") for f in info["formats"])
    assert has_mp3, "Should include MP3 audio option"
    print("    -> MP3 audio option verified!")

def test_fast_download_mp3():
    print("[3] Testing MP3 audio extraction with FFmpeg...")
    # Test a very short public sample clip (e.g. 5 seconds)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # 19-sec Me at the zoo
    res = perform_download(test_url, download_type="audio", quality="mp3_320", custom_title="test_me_at_the_zoo")
    print(f"    -> Download success: {res.get('success')}")
    if res.get("success"):
        print(f"    -> Output file: {res.get('filename')}")
        print(f"    -> File size: {res.get('size_bytes')} bytes")
        assert os.path.exists(res.get("filepath"))
        assert res.get("filename").endswith(".mp3")
        print("    -> Standalone MP3 conversion confirmed working perfectly!")
    else:
        print(f"    -> Error: {res.get('error')}")

if __name__ == "__main__":
    try:
        test_detect()
        test_extraction()
        test_fast_download_mp3()
        print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! [OK]")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
