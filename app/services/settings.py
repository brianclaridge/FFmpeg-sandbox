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
    update_file_applied_theme as update_metadata_applied_theme,
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
            # Theme-only video effects
            crop=CategorySettings(**settings_data.get("crop", {"preset": "none"})),
            colorshift=CategorySettings(**settings_data.get("colorshift", {"preset": "none"})),
            overlay=CategorySettings(**settings_data.get("overlay", {"preset": "none"})),
            active_category=settings_data.get("active_category", ""),
            active_tab=settings_data.get("active_tab", "audio"),
            applied_video_theme=settings_data.get("applied_video_theme", ""),
            applied_audio_theme=settings_data.get("applied_audio_theme", ""),
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
        # Theme-only video effects
        elif category == "crop":
            settings.crop.preset = preset
        elif category == "colorshift":
            settings.colorshift.preset = preset
        elif category == "overlay":
            settings.overlay.preset = preset
        return settings

    # Update in file metadata
    update_metadata_settings(filename, category, preset)
    return load_user_settings(filename)


def update_category_custom_values(
    category: str,
    custom_values: dict,
    filename: str | None = None
) -> UserSettings:
    """Update custom values for a filter category.

    Sets the category preset to 'custom' and stores the actual filter
    parameters in custom_values for use during processing.
    """
    if not filename:
        # Return default settings with custom values (no persistence)
        settings = UserSettings()
        if hasattr(settings, category):
            cat_settings = getattr(settings, category)
            cat_settings.preset = "custom"
            cat_settings.custom_values = custom_values
        return settings

    # Update in file metadata - set preset to "custom" and store values
    from app.services.file_metadata import update_file_custom_values
    update_file_custom_values(filename, category, custom_values)
    return load_user_settings(filename)


def update_active_category(
    category: str,
    filename: str | None = None,
    current_category: str | None = None,
) -> UserSettings:
    """Toggle the active category panel (close if already open)."""
    # Normalize empty string to None for consistent handling
    filename = filename if filename else None
    current_settings = load_user_settings(filename) if filename else UserSettings()

    # Use client-provided current_category for toggle when no file persistence
    active = current_category if current_category is not None else current_settings.active_category

    # Toggle: if clicking the already-open category, close it
    new_category = "" if active == category else category

    if not filename:
        current_settings.active_category = new_category
        return current_settings

    # Update in file metadata
    update_metadata_category(filename, new_category)
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


def update_applied_theme(
    media_type: str,
    preset_key: str,
    filename: str | None = None
) -> UserSettings:
    """Update which theme preset is applied for a media type.

    Args:
        media_type: "video" or "audio"
        preset_key: The preset key, or "" to clear
        filename: Optional file for persistence
    """
    if not filename:
        settings = UserSettings()
        if media_type == "video":
            settings.applied_video_theme = preset_key
        else:
            settings.applied_audio_theme = preset_key
        return settings

    # Update in file metadata
    update_metadata_applied_theme(filename, media_type, preset_key)
    return load_user_settings(filename)
