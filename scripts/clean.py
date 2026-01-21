#!/usr/bin/env python3
"""Clean up generated files and directories.

Usage:
    python scripts/clean.py all        # Purge entire .data directory
    python scripts/clean.py output     # Remove processed files
    python scripts/clean.py logs       # Remove log files
    python scripts/clean.py history    # Remove history.json
    python scripts/clean.py metadata   # Remove per-file .yml configs
    python scripts/clean.py downloads  # Remove downloaded videos
    python scripts/clean.py venv       # Remove .venv directory
    python scripts/clean.py pycache    # Remove __pycache__ and .pyc files
"""

import argparse
import shutil
import sys
from pathlib import Path

# Directories relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / ".data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = DATA_DIR / "logs"
VENV_DIR = PROJECT_ROOT / ".venv"


def remove_by_patterns(directory: Path, patterns: list[str]) -> int:
    """Remove files matching patterns in directory. Returns count removed."""
    if not directory.exists():
        return 0
    count = 0
    for pattern in patterns:
        for f in directory.glob(pattern):
            try:
                f.unlink()
                count += 1
            except Exception:
                pass
    return count


def remove_directory(path: Path) -> bool:
    """Remove directory recursively. Returns True if removed."""
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
        return True
    return False


def ensure_dirs(*dirs: Path) -> None:
    """Create directories if they don't exist."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def clean_all() -> None:
    """Purge entire .data directory and recreate structure."""
    remove_directory(DATA_DIR)
    ensure_dirs(INPUT_DIR, OUTPUT_DIR, LOGS_DIR)
    print("Purged .data/ directory")


def clean_output() -> None:
    """Remove processed audio/video files."""
    patterns = ["*.mp3", "*.mp4", "*.webm", "*.mkv", "*.wav", "*.flac", "*.txt"]
    count = remove_by_patterns(OUTPUT_DIR, patterns)
    print(f"Cleaned output directory ({count} files)")


def clean_logs() -> None:
    """Remove log files."""
    count = remove_by_patterns(LOGS_DIR, ["*.log"])
    print(f"Cleaned logs directory ({count} files)")


def clean_history() -> None:
    """Remove processing history."""
    history_file = DATA_DIR / "history.json"
    if history_file.exists():
        history_file.unlink()
        print("Cleared processing history")
    else:
        print("No history file found")


def clean_metadata() -> None:
    """Remove per-file metadata configs."""
    count = remove_by_patterns(INPUT_DIR, ["*.yml"])
    print(f"Cleaned per-file metadata ({count} files)")


def clean_downloads() -> None:
    """Remove downloaded video files from input."""
    patterns = ["*.mp4", "*.mkv", "*.webm", "*.avi", "*.mov"]
    count = remove_by_patterns(INPUT_DIR, patterns)
    print(f"Cleaned downloaded videos ({count} files)")


def clean_venv() -> None:
    """Remove Python virtual environment."""
    if remove_directory(VENV_DIR):
        print("Removed .venv directory")
    else:
        print("No .venv directory found")


def clean_pycache() -> None:
    """Remove Python cache files."""
    count = 0
    # Remove __pycache__ directories
    for cache_dir in PROJECT_ROOT.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
            count += 1
    # Remove .pyc files
    for pyc in PROJECT_ROOT.rglob("*.pyc"):
        try:
            pyc.unlink()
            count += 1
        except Exception:
            pass
    print(f"Cleaned Python cache ({count} items)")


COMMANDS = {
    "all": clean_all,
    "output": clean_output,
    "logs": clean_logs,
    "history": clean_history,
    "metadata": clean_metadata,
    "downloads": clean_downloads,
    "venv": clean_venv,
    "pycache": clean_pycache,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean up generated files")
    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        help="What to clean",
    )
    args = parser.parse_args()

    COMMANDS[args.command]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
