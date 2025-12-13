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
    update_active_tab as update_metadata_tab,
    get_default_settings,
)


def load_user_settings(filename: str | None = None) -> UserSettings:
    """Load user settings for a specific file or defaults if no file."""
    if not filename:
        return UserSettings()

    try:
        settings_data = get_file_settings(filename)

        return UserSettings(
            volume=CategorySettings(**settings_data.get("volume", {"preset": "none"})),
            tunnel=CategorySettings(**settings_data.get("tunnel", {"preset": "none"})),
            frequency=CategorySettings(**settings_data.get("frequency", {"preset": "none"})),
            speed=CategorySettings(**settings_data.get("speed", {"preset": "none"})),
            pitch=CategorySettings(**settings_data.get("pitch", {"preset": "none"})),
            noise_reduction=CategorySettings(**settings_data.get("noise_reduction", {"preset": "none"})),
            compressor=CategorySettings(**settings_data.get("compressor", {"preset": "none"})),
            # Video effects
            brightness=CategorySettings(**settings_data.get("brightness", {"preset": "none"})),
            contrast=CategorySettings(**settings_data.get("contrast", {"preset": "none"})),
            saturation=CategorySettings(**settings_data.get("saturation", {"preset": "none"})),
            blur=CategorySettings(**settings_data.get("blur", {"preset": "none"})),
            sharpen=CategorySettings(**settings_data.get("sharpen", {"preset": "none"})),
            transform=CategorySettings(**settings_data.get("transform", {"preset": "none"})),
            active_category=settings_data.get("active_category", "volume"),
            active_tab=settings_data.get("active_tab", "audio"),
        )
    except Exception as e:
        logger.warning(f"Failed to load settings for {filename}: {e}")
        return UserSettings()


def update_category_preset(category: str, preset: str, filename: str | None = None) -> UserSettings:
    """Update a single category's preset and save."""
    if not filename:
        # Return default settings with the updated preset (no persistence)
        settings = UserSettings()
        settings.active_category = category  # Keep accordion expanded on this category
        if category == "volume":
            settings.volume.preset = preset
        elif category == "tunnel":
            settings.tunnel.preset = preset
        elif category == "frequency":
            settings.frequency.preset = preset
        elif category == "speed":
            settings.speed.preset = preset
        elif category == "pitch":
            settings.pitch.preset = preset
        elif category == "noise_reduction":
            settings.noise_reduction.preset = preset
        elif category == "compressor":
            settings.compressor.preset = preset
        # Video effects
        elif category == "brightness":
            settings.brightness.preset = preset
        elif category == "contrast":
            settings.contrast.preset = preset
        elif category == "saturation":
            settings.saturation.preset = preset
        elif category == "blur":
            settings.blur.preset = preset
        elif category == "sharpen":
            settings.sharpen.preset = preset
        elif category == "transform":
            settings.transform.preset = preset
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


def update_active_tab(tab: str, filename: str | None = None) -> UserSettings:
    """Update which effects tab (audio/video) is displayed."""
    if not filename:
        # Return default settings with updated active tab (no persistence)
        settings = UserSettings()
        settings.active_tab = tab
        return settings

    # Update in file metadata
    update_metadata_tab(filename, tab)
    return load_user_settings(filename)
