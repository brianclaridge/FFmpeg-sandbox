"""Per-file metadata service for input files.

Each input file gets a companion .yml with source metadata,
processing history, and effect chain settings.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from app.config import INPUT_DIR


def get_metadata_path(filename: str) -> Path:
    """Get the metadata YAML path for a given input file."""
    stem = Path(filename).stem
    return INPUT_DIR / f"{stem}.yml"


def load_file_metadata(filename: str) -> dict[str, Any]:
    """Load metadata for a specific input file.

    Returns default structure if file doesn't exist.
    """
    meta_path = get_metadata_path(filename)

    if not meta_path.exists():
        return get_default_metadata()

    try:
        with open(meta_path) as f:
            data = yaml.safe_load(f) or {}

        # Ensure required sections exist
        if "source" not in data:
            data["source"] = {}
        if "settings" not in data:
            data["settings"] = get_default_settings()
        if "history" not in data:
            data["history"] = []

        return data
    except Exception as e:
        logger.warning(f"Failed to load metadata for {filename}: {e}")
        return get_default_metadata()


def save_file_metadata(filename: str, metadata: dict[str, Any]) -> bool:
    """Save metadata for a specific input file."""
    meta_path = get_metadata_path(filename)

    try:
        with open(meta_path, "w") as f:
            yaml.safe_dump(metadata, f, default_flow_style=False, sort_keys=False)

        logger.debug(f"Saved metadata to {meta_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save metadata for {filename}: {e}")
        return False


def get_default_metadata() -> dict[str, Any]:
    """Return default metadata structure."""
    return {
        "source": {},
        "settings": get_default_settings(),
        "history": [],
    }


def get_default_settings() -> dict[str, Any]:
    """Return default effect chain settings."""
    return {
        "active_category": "volume",
        "volume": {"preset": "2x", "custom_values": {}},
        "tunnel": {"preset": "none", "custom_values": {}},
        "frequency": {"preset": "flat", "custom_values": {}},
    }


def create_file_metadata(
    filename: str,
    url: str,
    title: str,
    uploader: str,
    duration: int,
    extractor: str,
) -> dict[str, Any]:
    """Create initial metadata for a newly downloaded file."""
    metadata = {
        "source": {
            "url": url,
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "extractor": extractor,
            "downloaded_at": datetime.now().isoformat(),
        },
        "settings": get_default_settings(),
        "history": [],
    }

    save_file_metadata(filename, metadata)
    return metadata


def get_display_title(filename: str) -> str:
    """Get the original title for display, or filename if not available."""
    metadata = load_file_metadata(filename)
    title = metadata.get("source", {}).get("title")
    return title if title else filename


def get_file_settings(filename: str) -> dict[str, Any]:
    """Get effect chain settings for a file."""
    metadata = load_file_metadata(filename)
    return metadata.get("settings", get_default_settings())


def update_file_settings(filename: str, category: str, preset: str) -> dict[str, Any]:
    """Update a category's preset for a specific file."""
    metadata = load_file_metadata(filename)
    settings = metadata.get("settings", get_default_settings())

    if category in settings:
        settings[category]["preset"] = preset

    metadata["settings"] = settings
    save_file_metadata(filename, metadata)

    return settings


def update_active_category(filename: str, category: str) -> dict[str, Any]:
    """Update which category panel is active for a file."""
    metadata = load_file_metadata(filename)
    settings = metadata.get("settings", get_default_settings())
    settings["active_category"] = category
    metadata["settings"] = settings
    save_file_metadata(filename, metadata)
    return settings


def add_history_entry(
    filename: str,
    entry_id: str,
    output_file: str,
    start_time: str,
    end_time: str,
    volume: float,
    highpass: int,
    lowpass: int,
    delays: str,
    decays: str,
) -> dict[str, Any]:
    """Add a processing history entry to a file's metadata."""
    metadata = load_file_metadata(filename)

    history_entry = {
        "id": entry_id,
        "output_file": output_file,
        "timestamp": datetime.now().isoformat(),
        "params": {
            "start_time": start_time,
            "end_time": end_time,
            "volume": volume,
            "highpass": highpass,
            "lowpass": lowpass,
            "delays": delays,
            "decays": decays,
        },
    }

    # Add to beginning of history list
    history = metadata.get("history", [])
    history.insert(0, history_entry)

    # Keep only last 50 entries per file
    metadata["history"] = history[:50]

    save_file_metadata(filename, metadata)
    logger.info(f"Added history entry {entry_id} to {filename}")

    return history_entry


def delete_history_entry(filename: str, entry_id: str) -> bool:
    """Delete a history entry from a file's metadata."""
    metadata = load_file_metadata(filename)
    history = metadata.get("history", [])

    for i, entry in enumerate(history):
        if entry.get("id") == entry_id:
            history.pop(i)
            metadata["history"] = history
            save_file_metadata(filename, metadata)
            logger.info(f"Deleted history entry {entry_id} from {filename}")
            return True

    return False


def get_history_entry(filename: str, entry_id: str) -> dict[str, Any] | None:
    """Get a specific history entry from a file's metadata."""
    metadata = load_file_metadata(filename)
    history = metadata.get("history", [])

    for entry in history:
        if entry.get("id") == entry_id:
            return entry

    return None


def get_file_history(filename: str) -> list[dict[str, Any]]:
    """Get all history entries for a file."""
    metadata = load_file_metadata(filename)
    return metadata.get("history", [])


def list_all_files_with_metadata() -> list[dict[str, Any]]:
    """List all input files that have metadata."""
    results = []

    for meta_file in INPUT_DIR.glob("*.yml"):
        # Find corresponding media file
        stem = meta_file.stem
        media_files = list(INPUT_DIR.glob(f"{stem}.*"))
        media_files = [f for f in media_files if f.suffix != ".yml"]

        if media_files:
            metadata = load_file_metadata(media_files[0].name)
            results.append({
                "filename": media_files[0].name,
                "metadata": metadata,
            })

    return results
