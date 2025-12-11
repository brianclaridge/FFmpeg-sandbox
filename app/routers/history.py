"""History management router."""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from loguru import logger

from app.services.history import load_history, delete_history_entry, get_history_entry
from app.models import PRESETS, PresetLevel

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
async def apply_history(request: Request, entry_id: str):
    """Apply settings from a history entry to the form."""
    entry = get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Get preset config for defaults
    try:
        preset_level = PresetLevel(entry.preset)
        preset_config = PRESETS[preset_level]
    except ValueError:
        preset_level = PresetLevel.MEDIUM
        preset_config = PRESETS[preset_level]

    return templates.TemplateResponse(
        "partials/slider_form.html",
        {
            "request": request,
            "preset": preset_config,
            "volume": entry.volume,
            "highpass": entry.highpass,
            "lowpass": entry.lowpass,
            "delays": entry.delays,
            "decays": entry.decays,
            "start_time": entry.start_time,
            "end_time": entry.end_time,
        },
    )
