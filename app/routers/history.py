"""History management router."""

import json

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.services.history import load_history, delete_history_entry, get_history_entry
from app.services.settings import load_user_settings, update_category_preset
from app.services.presets_themes import get_video_theme_presets, get_audio_theme_presets
from app.models import UserSettings, CategorySettings
from app.routers.audio import _get_accordion_context

router = APIRouter(prefix="/history")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def get_history(request: Request):
    """Get processing history partial."""
    history = load_history()
    return templates.TemplateResponse(
        "partials/history.html",
        {
            "request": request,
            "history": history,
        },
    )


@router.delete("/{entry_id}", response_class=HTMLResponse)
async def remove_history(request: Request, entry_id: str):
    """Delete a history entry."""
    if not delete_history_entry(entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")

    history = load_history()
    return templates.TemplateResponse(
        "partials/history.html",
        {
            "request": request,
            "history": history,
        },
    )


@router.get("/{entry_id}/apply", response_class=HTMLResponse)
async def apply_history(request: Request, entry_id: str, filename: str = ""):
    """Apply settings from a history entry to the effect chain."""
    entry = get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Update settings for current file if one is selected
    if filename:
        update_category_preset("volume", entry.volume_preset, filename)
        update_category_preset("tunnel", entry.tunnel_preset, filename)
        update_category_preset("frequency", entry.frequency_preset, filename)

    # Load updated settings
    user_settings = load_user_settings(filename) if filename else UserSettings(
        volume=CategorySettings(preset=entry.volume_preset),
        tunnel=CategorySettings(preset=entry.tunnel_preset),
        frequency=CategorySettings(preset=entry.frequency_preset),
    )

    context = _get_accordion_context(user_settings, filename)
    context["request"] = request
    context["video_theme_presets"] = get_video_theme_presets()
    context["audio_theme_presets"] = get_audio_theme_presets()

    response = templates.TemplateResponse("partials/filters_tabs.html", context)

    # Trigger clip range update via HX-Trigger
    response.headers["HX-Trigger"] = json.dumps({
        "historyApplied": {
            "startTime": entry.start_time,
            "endTime": entry.end_time
        }
    })

    return response


@router.get("/{entry_id}/preview", response_class=HTMLResponse)
async def preview_history(request: Request, entry_id: str):
    """Preview a history entry's output file."""
    entry = get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return templates.TemplateResponse(
        "partials/history_preview.html",
        {
            "request": request,
            "entry": entry,
        },
    )
