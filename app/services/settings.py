"""User settings persistence service."""

from loguru import logger
import yaml

from app.config import DATA_DIR
from app.models import UserSettings, CategorySettings

SETTINGS_FILE = DATA_DIR / "user_settings.yml"


def load_user_settings() -> UserSettings:
    """Load user settings from YAML file."""
    if not SETTINGS_FILE.exists():
        return UserSettings()

    try:
        with open(SETTINGS_FILE) as f:
            data = yaml.safe_load(f) or {}

        return UserSettings(
            volume=CategorySettings(**data.get("volume", {"preset": "2x"})),
            tunnel=CategorySettings(**data.get("tunnel", {"preset": "none"})),
            frequency=CategorySettings(**data.get("frequency", {"preset": "flat"})),
            active_category=data.get("active_category", "volume"),
        )
    except Exception as e:
        logger.warning(f"Failed to load user settings: {e}")
        return UserSettings()


def save_user_settings(settings: UserSettings) -> bool:
    """Save user settings to YAML file."""
    try:
        data = {
            "volume": {
                "preset": settings.volume.preset,
                "custom_values": settings.volume.custom_values,
            },
            "tunnel": {
                "preset": settings.tunnel.preset,
                "custom_values": settings.tunnel.custom_values,
            },
            "frequency": {
                "preset": settings.frequency.preset,
                "custom_values": settings.frequency.custom_values,
            },
            "active_category": settings.active_category,
        }

        with open(SETTINGS_FILE, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)

        logger.debug(f"Saved user settings to {SETTINGS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save user settings: {e}")
        return False


def update_category_preset(category: str, preset: str) -> UserSettings:
    """Update a single category's preset and save."""
    settings = load_user_settings()

    if category == "volume":
        settings.volume.preset = preset
    elif category == "tunnel":
        settings.tunnel.preset = preset
    elif category == "frequency":
        settings.frequency.preset = preset

    save_user_settings(settings)
    return settings


def update_active_category(category: str) -> UserSettings:
    """Update which category panel is displayed."""
    settings = load_user_settings()
    settings.active_category = category
    save_user_settings(settings)
    return settings
