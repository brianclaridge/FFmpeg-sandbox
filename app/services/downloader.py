"""Video download service using yt-dlp."""

import re
import hashlib
from pathlib import Path
from dataclasses import dataclass

import yt_dlp
from loguru import logger

from app.config import INPUT_DIR, config
from app.services.file_metadata import create_file_metadata


@dataclass
class DownloadResult:
    """Result of a video download operation."""
    success: bool
    filename: str | None = None
    title: str | None = None
    error: str | None = None


def get_source_prefix(extractor: str) -> str:
    """Map yt-dlp extractor to short prefix."""
    prefixes = {
        "youtube": "yt",
        "twitch": "tw",
        "vimeo": "vm",
        "twitter": "x",
        "tiktok": "tt",
        "instagram": "ig",
        "reddit": "rd",
        "dailymotion": "dm",
    }
    # Handle extractors like 'youtube:tab' -> 'youtube'
    base_extractor = extractor.lower().split(":")[0]
    return prefixes.get(base_extractor, "dl")


def sanitize_filename(video_id: str, extractor: str) -> str:
    """Create anonymized filename: {source}-{id}."""
    prefix = get_source_prefix(extractor)

    # For unknown sources or very long IDs, use a hash
    if prefix == "dl" or len(video_id) > 20:
        short_id = hashlib.sha256(video_id.encode()).hexdigest()[:12]
        return f"{prefix}-{short_id}"

    return f"{prefix}-{video_id}"


def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL format and check if yt-dlp can handle it."""
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        return False, "Invalid URL format"

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            ydl.extract_info(url, download=False)
        return True, ""
    except yt_dlp.utils.DownloadError as e:
        return False, f"Unsupported URL or video not found"
    except Exception as e:
        return False, f"Validation error: {str(e)[:100]}"


def get_video_info(url: str) -> dict | None:
    """Get video metadata without downloading."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'id': info.get('id', 'unknown'),
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'extractor': info.get('extractor', 'unknown'),
            }
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return None


def download_video(url: str) -> DownloadResult:
    """Download video from URL to INPUT_DIR."""
    logger.info(f"Starting download: {url}")

    info = get_video_info(url)
    if not info:
        return DownloadResult(
            success=False,
            error="Could not retrieve video information"
        )

    # Use anonymized filename: {source}-{id}
    safe_name = sanitize_filename(info["id"], info["extractor"])
    output_template = str(INPUT_DIR / f"{safe_name}.%(ext)s")

    ydl_opts = {
        "format": config.download.format,
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find downloaded file (exclude .yml metadata files)
        downloaded_files = [
            f for f in INPUT_DIR.glob(f"{safe_name}.*")
            if f.suffix != ".yml"
        ]

        if downloaded_files:
            final_file = downloaded_files[0]
            logger.info(f"Download complete: {final_file.name}")

            # Create per-file metadata YAML
            create_file_metadata(
                filename=final_file.name,
                url=url,
                title=info["title"],
                uploader=info["uploader"],
                duration=info["duration"],
                extractor=info["extractor"],
            )

            return DownloadResult(
                success=True,
                filename=final_file.name,
                title=info["title"],
            )
        else:
            return DownloadResult(
                success=False,
                error="Download completed but file not found"
            )

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download failed: {e}")
        return DownloadResult(
            success=False,
            error=f"Download failed: {str(e)[:200]}"
        )
    except Exception as e:
        logger.exception("Unexpected download error")
        return DownloadResult(
            success=False,
            error=f"Unexpected error: {str(e)[:200]}"
        )
