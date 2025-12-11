"""Processing history service."""

import json
import uuid
from datetime import datetime
from pathlib import Path

from loguru import logger

from app.config import HISTORY_FILE, OUTPUT_DIR
from app.models import HistoryEntry


def load_history() -> list[HistoryEntry]:
    """Load processing history from JSON file."""
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text())
        return [HistoryEntry(**entry) for entry in data]
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to load history: {e}")
        return []


def save_history(entries: list[HistoryEntry]) -> None:
    """Save processing history to JSON file."""
    data = [entry.model_dump(mode="json") for entry in entries]
    HISTORY_FILE.write_text(json.dumps(data, indent=2, default=str))


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
) -> HistoryEntry:
    """Add a new entry to processing history."""
    entry = HistoryEntry(
        id=str(uuid.uuid4())[:8],
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
    )

    history = load_history()
    history.insert(0, entry)

    # Keep only last 50 entries
    history = history[:50]
    save_history(history)

    logger.info(f"Added history entry: {entry.id}")
    return entry


def delete_history_entry(entry_id: str) -> bool:
    """Delete a history entry and its associated file."""
    history = load_history()

    for i, entry in enumerate(history):
        if entry.id == entry_id:
            # Delete output file if exists
            output_path = OUTPUT_DIR / entry.output_file
            if output_path.exists():
                output_path.unlink()
                logger.info(f"Deleted file: {entry.output_file}")

            history.pop(i)
            save_history(history)
            logger.info(f"Deleted history entry: {entry_id}")
            return True

    return False


def get_history_entry(entry_id: str) -> HistoryEntry | None:
    """Get a specific history entry by ID."""
    history = load_history()
    for entry in history:
        if entry.id == entry_id:
            return entry
    return None
