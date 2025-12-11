"""Processing history service.

History is now stored per-file in YAML metadata files alongside input files.
This module provides backward-compatible functions that delegate to file_metadata.
"""

import uuid
from datetime import datetime
from pathlib import Path

from loguru import logger

from app.config import OUTPUT_DIR, INPUT_DIR
from app.models import HistoryEntry
from app.services.file_metadata import (
    add_history_entry as add_metadata_history,
    delete_history_entry as delete_metadata_history,
    get_history_entry as get_metadata_history,
    get_file_history,
    load_file_metadata,
)


def load_history(input_file: str | None = None) -> list[HistoryEntry]:
    """Load processing history for a specific file or all files.

    Args:
        input_file: If provided, load history for this file only.
                   If None, aggregates history from all input files.
    """
    if input_file:
        # Load history for specific file
        history_data = get_file_history(input_file)
        return _convert_to_entries(history_data, input_file)

    # Aggregate history from all files with metadata
    all_entries = []
    for meta_file in INPUT_DIR.glob("*.yml"):
        stem = meta_file.stem
        # Find corresponding media file
        media_files = [f for f in INPUT_DIR.glob(f"{stem}.*") if f.suffix != ".yml"]
        if media_files:
            filename = media_files[0].name
            history_data = get_file_history(filename)
            all_entries.extend(_convert_to_entries(history_data, filename))

    # Sort by timestamp descending
    all_entries.sort(key=lambda e: e.timestamp, reverse=True)
    return all_entries[:50]  # Limit to 50 most recent


def _convert_to_entries(history_data: list[dict], input_file: str) -> list[HistoryEntry]:
    """Convert metadata history format to HistoryEntry models."""
    entries = []
    for h in history_data:
        params = h.get("params", {})
        try:
            entries.append(HistoryEntry(
                id=h.get("id", ""),
                timestamp=datetime.fromisoformat(h.get("timestamp", datetime.now().isoformat())),
                input_file=input_file,
                output_file=h.get("output_file", ""),
                start_time=params.get("start_time", "00:00:00"),
                end_time=params.get("end_time", "00:00:06"),
                preset="custom",
                volume=params.get("volume", 2.0),
                highpass=params.get("highpass", 100),
                lowpass=params.get("lowpass", 4500),
                delays=params.get("delays", "15|25|35|50"),
                decays=params.get("decays", "0.35|0.3|0.25|0.2"),
                volume_preset=params.get("volume_preset", "2x"),
                tunnel_preset=params.get("tunnel_preset", "none"),
                frequency_preset=params.get("frequency_preset", "flat"),
            ))
        except Exception as e:
            logger.warning(f"Failed to convert history entry: {e}")
    return entries


def add_history_entry(
    input_file: str,
    output_file: str,
    start_time: str,
    end_time: str,
    preset: str,
    volume: float,
    highpass: int,
    lowpass: int,
    delays: str,
    decays: str,
    volume_preset: str = "2x",
    tunnel_preset: str = "none",
    frequency_preset: str = "flat",
) -> HistoryEntry:
    """Add a new entry to processing history for a file."""
    entry_id = str(uuid.uuid4())[:8]

    # Store in per-file metadata
    add_metadata_history(
        filename=input_file,
        entry_id=entry_id,
        output_file=output_file,
        start_time=start_time,
        end_time=end_time,
        volume=volume,
        highpass=highpass,
        lowpass=lowpass,
        delays=delays,
        decays=decays,
        volume_preset=volume_preset,
        tunnel_preset=tunnel_preset,
        frequency_preset=frequency_preset,
    )

    # Return HistoryEntry for compatibility
    entry = HistoryEntry(
        id=entry_id,
        timestamp=datetime.now(),
        input_file=input_file,
        output_file=output_file,
        start_time=start_time,
        end_time=end_time,
        preset=preset,
        volume=volume,
        highpass=highpass,
        lowpass=lowpass,
        delays=delays,
        decays=decays,
        volume_preset=volume_preset,
        tunnel_preset=tunnel_preset,
        frequency_preset=frequency_preset,
    )

    logger.info(f"Added history entry: {entry.id} for {input_file}")
    return entry


def delete_history_entry(entry_id: str, input_file: str | None = None) -> bool:
    """Delete a history entry and its associated output file.

    Args:
        entry_id: The ID of the history entry to delete.
        input_file: If provided, search only this file's history.
                   If None, search all files.
    """
    # If input_file provided, delete from that file
    if input_file:
        entry_data = get_metadata_history(input_file, entry_id)
        if entry_data:
            output_file = entry_data.get("output_file", "")
            if output_file:
                output_path = OUTPUT_DIR / output_file
                if output_path.exists():
                    output_path.unlink()
                    logger.info(f"Deleted file: {output_file}")

            delete_metadata_history(input_file, entry_id)
            return True
        return False

    # Search all files for the entry
    for meta_file in INPUT_DIR.glob("*.yml"):
        stem = meta_file.stem
        media_files = [f for f in INPUT_DIR.glob(f"{stem}.*") if f.suffix != ".yml"]
        if media_files:
            filename = media_files[0].name
            entry_data = get_metadata_history(filename, entry_id)
            if entry_data:
                output_file = entry_data.get("output_file", "")
                if output_file:
                    output_path = OUTPUT_DIR / output_file
                    if output_path.exists():
                        output_path.unlink()
                        logger.info(f"Deleted file: {output_file}")

                delete_metadata_history(filename, entry_id)
                return True

    return False


def get_history_entry(entry_id: str, input_file: str | None = None) -> HistoryEntry | None:
    """Get a specific history entry by ID.

    Args:
        entry_id: The ID of the history entry.
        input_file: If provided, search only this file's history.
    """
    if input_file:
        entry_data = get_metadata_history(input_file, entry_id)
        if entry_data:
            entries = _convert_to_entries([entry_data], input_file)
            return entries[0] if entries else None
        return None

    # Search all files
    for meta_file in INPUT_DIR.glob("*.yml"):
        stem = meta_file.stem
        media_files = [f for f in INPUT_DIR.glob(f"{stem}.*") if f.suffix != ".yml"]
        if media_files:
            filename = media_files[0].name
            entry_data = get_metadata_history(filename, entry_id)
            if entry_data:
                entries = _convert_to_entries([entry_data], filename)
                return entries[0] if entries else None

    return None
