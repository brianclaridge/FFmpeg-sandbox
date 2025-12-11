"""User settings persistence service.

Settings are now stored per-file in YAML metadata files alongside input files.
When no file is selected, default settings are returned.
"""

from loguru import logger

from app.models import UserSettings, CategorySettings
from app.services.file_metadata import (
    load_file_metadata,
    get_file_settings,
    update_file_settings as update_metadata_settings,
    update_active_category as update_metadata_category,
    get_default_settings,
)


def load_user_settings(filename: str | None = None) -> UserSettings:
    """Load user settings for a specific file or defaults if no file."""
    if not filename:
        return UserSettings()

    try:
        settings_data = get_file_settings(filename)

        return UserSettings(
            volume=CategorySettings(**settings_data.get("volume", {"preset": "2x"})),
            tunnel=CategorySettings(**settings_data.get("tunnel", {"preset": "none"})),
            frequency=CategorySettings(**settings_data.get("frequency", {"preset": "flat"})),
            active_category=settings_data.get("active_category", "volume"),
        )
    except Exception as e:
        logger.warning(f"Failed to load settings for {filename}: {e}")
        return UserSettings()


def update_category_preset(category: str, preset: str, filename: str | None = None) -> UserSettings:
    """Update a single category's preset and save."""
    if not filename:
        # Return default settings with the updated preset (no persistence)
        settings = UserSettings()
        if category == "volume":
            settings.volume.preset = preset
        elif category == "tunnel":
            settings.tunnel.preset = preset
        elif category == "frequency":
            settings.frequency.preset = preset
        return settings

    # Update in file metadata
    update_metadata_settings(filename, category, preset)
    return load_user_settings(filename)


def update_active_category(category: str, filename: str | None = None) -> UserSettings:
    """Update which category panel is displayed."""
    if not filename:
        # Return default settings with updated active category (no persistence)
        settings = UserSettings()
        settings.active_category = category
        return settings

    # Update in file metadata
    update_metadata_category(filename, category)
    return load_user_settings(filename)
