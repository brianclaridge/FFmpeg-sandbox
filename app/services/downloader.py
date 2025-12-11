"""Video download service using yt-dlp."""

import re
from pathlib import Path
from dataclasses import dataclass

import yt_dlp
from loguru import logger

from app.config import INPUT_DIR, config


@dataclass
class DownloadResult:
    """Result of a video download operation."""
    success: bool
    filename: str | None = None
    title: str | None = None
    error: str | None = None


def sanitize_filename(title: str, video_id: str) -> str:
    """Create a safe filename from video title and ID."""
    safe_title = re.sub(r'[^\w\s\-]', '', title)
    safe_title = re.sub(r'[\s_]+', '_', safe_title)
    safe_title = safe_title[:config.download.filename_max_length].strip('_')
    return f"{safe_title}_{video_id}"


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

    safe_name = sanitize_filename(info['title'], info['id'])
    output_template = str(INPUT_DIR / f"{safe_name}.%(ext)s")

    ydl_opts = {
        'format': config.download.format,
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_files = list(INPUT_DIR.glob(f"{safe_name}.*"))
        if downloaded_files:
            final_file = downloaded_files[0]
            logger.info(f"Download complete: {final_file.name}")
            return DownloadResult(
                success=True,
                filename=final_file.name,
                title=info['title'],
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
