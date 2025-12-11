"""Application configuration loaded from config.yml."""

from pathlib import Path
from dataclasses import dataclass, field

import yaml


BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.yml"
DATA_DIR = BASE_DIR / ".data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = DATA_DIR / "logs"
HISTORY_FILE = DATA_DIR / "history.json"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    version: str = "0.1.0"
    reload: bool = True


@dataclass
class LoggingConfig:
    rotation: str = "10 MB"
    retention: str = "7 days"
    stderr_level: str = "INFO"
    file_level: str = "DEBUG"


@dataclass
class HistoryConfig:
    max_entries: int = 50


@dataclass
class DownloadConfig:
    filename_max_length: int = 50
    format: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"


@dataclass
class AudioConfig:
    allowed_extensions: list[str] = field(default_factory=lambda: [
        ".mp4", ".mkv", ".avi", ".mov", ".webm",
        ".mp3", ".wav", ".flac", ".m4a", ".ogg"
    ])
    preview_timeout: int = 30
    mp3_quality: str = "4"
    default_preset: str = "none"
    default_start_time: str = "00:00:00"
    default_end_time: str = "00:00:06"


@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)


def load_config() -> AppConfig:
    """Load configuration from config.yml."""
    if not CONFIG_FILE.exists():
        return AppConfig()

    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f) or {}

    return AppConfig(
        server=ServerConfig(**data.get("server", {})),
        logging=LoggingConfig(**data.get("logging", {})),
        history=HistoryConfig(**data.get("history", {})),
        download=DownloadConfig(**data.get("download", {})),
        audio=AudioConfig(**data.get("audio", {})),
    )


config = load_config()
