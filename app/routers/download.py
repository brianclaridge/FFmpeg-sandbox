"""Video download router."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.config import INPUT_DIR
from app.services.downloader import download_video, validate_url, get_video_info
from app.services.processor import get_input_files

router = APIRouter(prefix="/download")
templates = Jinja2Templates(directory="app/templates")


@router.post("/validate", response_class=HTMLResponse)
async def validate_download_url(request: Request, download_url: str = Form(...)):
    """Validate URL and return video info preview."""
    url = download_url.strip()

    if not url:
        return templates.TemplateResponse(
            "partials/download_status.html",
            {
                "request": request,
                "error": "Please enter a URL",
                "status": "error",
            },
        )

    is_valid, error = validate_url(url)
    if not is_valid:
        return templates.TemplateResponse(
            "partials/download_status.html",
            {
                "request": request,
                "error": error,
                "status": "error",
            },
        )

    info = get_video_info(url)
    if not info:
        return templates.TemplateResponse(
            "partials/download_status.html",
            {
                "request": request,
                "error": "Could not retrieve video information",
                "status": "error",
            },
        )

    duration = info['duration'] or 0
    duration_mins = duration // 60
    duration_secs = duration % 60
    duration_str = f"{duration_mins}:{duration_secs:02d}"

    return templates.TemplateResponse(
        "partials/download_status.html",
        {
            "request": request,
            "status": "ready",
            "video_info": {
                "title": info['title'],
                "duration": duration_str,
                "uploader": info['uploader'],
                "source": info['extractor'],
            },
            "url": url,
        },
    )


@router.post("", response_class=HTMLResponse)
async def download_from_url(request: Request, url: str = Form(...)):
    """Download video from URL and return updated file selector."""
    url = url.strip()
    logger.info(f"Download request for: {url}")

    result = download_video(url)

    if result.success:
        input_files = get_input_files(INPUT_DIR)

        return templates.TemplateResponse(
            "partials/download_complete.html",
            {
                "request": request,
                "success": True,
                "filename": result.filename,
                "title": result.title,
                "input_files": input_files,
            },
        )
    else:
        return templates.TemplateResponse(
            "partials/download_status.html",
            {
                "request": request,
                "status": "error",
                "error": result.error,
            },
        )
