"""History management router."""

import json

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.services.history import load_history, delete_history_entry, get_history_entry
from app.services.settings import load_user_settings, update_category_preset
from app.services.presets import (
    get_volume_presets,
    get_tunnel_presets,
    get_frequency_presets,
)
from app.models import UserSettings, CategorySettings

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


def _get_accordion_context(user_settings, filename: str | None = None) -> dict:
    """Build context dict for accordion template."""
    # Get preset dictionaries from YAML
    volume_presets = get_volume_presets()
    tunnel_presets = get_tunnel_presets()
    frequency_presets = get_frequency_presets()

    # Get current preset configs (with fallbacks)
    volume_current = volume_presets.get(user_settings.volume.preset) or volume_presets["none"]
    tunnel_current = tunnel_presets.get(user_settings.tunnel.preset) or tunnel_presets["none"]
    frequency_current = frequency_presets.get(user_settings.frequency.preset) or frequency_presets["none"]

    return {
        "user_settings": user_settings,
        "volume_presets": volume_presets,
        "tunnel_presets": tunnel_presets,
        "frequency_presets": frequency_presets,
        "volume_current": volume_current,
        "tunnel_current": tunnel_current,
        "frequency_current": frequency_current,
        "current_filename": filename,
    }


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

    response = templates.TemplateResponse("partials/effect_chain_accordion.html", context)

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
