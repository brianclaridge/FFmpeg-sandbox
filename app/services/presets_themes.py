"""Theme presets service - loads themed transformation presets from YAML."""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from pydantic import ValidationError

from app.models import ThemePreset, FilterStep


# Global theme preset storage
_theme_presets: dict[str, dict[str, ThemePreset]] = {}


def load_theme_presets(presets_file: Path | str = "presets_themes.yml") -> dict[str, dict[str, ThemePreset]]:
    """Load and validate theme presets from YAML file.

    Args:
        presets_file: Path to the theme presets YAML file

    Returns:
        Dictionary with validated presets organized by media type (audio/video)
    """
    global _theme_presets

    presets_path = Path(presets_file)
    if not presets_path.exists():
        logger.warning(f"Theme presets file not found: {presets_path}")
        return {"audio": {}, "video": {}}

    logger.info(f"Loading theme presets from {presets_path}")

    with open(presets_path, "r") as f:
        raw_data = yaml.safe_load(f) or {}

    validated_presets = {"audio": {}, "video": {}}

    # Validate video presets
    for preset_key, preset_data in raw_data.get("video", {}).items():
        try:
            # Convert filter dicts to FilterStep objects
            filters = [
                FilterStep(type=f["type"], params=f["params"])
                for f in preset_data.get("filters", [])
            ]
            preset_data["filters"] = filters
            validated = ThemePreset(**preset_data)
            validated_presets["video"][preset_key] = validated
        except (ValidationError, KeyError) as e:
            logger.error(f"Invalid video theme preset {preset_key}: {e}")
            continue

    # Validate audio presets
    for preset_key, preset_data in raw_data.get("audio", {}).items():
        try:
            filters = [
                FilterStep(type=f["type"], params=f["params"])
                for f in preset_data.get("filters", [])
            ]
            preset_data["filters"] = filters
            validated = ThemePreset(**preset_data)
            validated_presets["audio"][preset_key] = validated
        except (ValidationError, KeyError) as e:
            logger.error(f"Invalid audio theme preset {preset_key}: {e}")
            continue

    _theme_presets = validated_presets

    video_count = len(validated_presets["video"])
    audio_count = len(validated_presets["audio"])
    logger.info(f"Loaded {video_count} video and {audio_count} audio theme presets")

    return validated_presets


def get_theme_presets() -> dict[str, dict[str, ThemePreset]]:
    """Get the loaded theme presets dictionary."""
    if not _theme_presets:
        load_theme_presets()
    return _theme_presets


def get_video_theme_presets() -> dict[str, ThemePreset]:
    """Get video theme presets."""
    presets = get_theme_presets()
    return presets.get("video", {})


def get_audio_theme_presets() -> dict[str, ThemePreset]:
    """Get audio theme presets."""
    presets = get_theme_presets()
    return presets.get("audio", {})


def get_theme_preset(media_type: str, preset_key: str) -> ThemePreset | None:
    """Get a specific theme preset.

    Args:
        media_type: "audio" or "video"
        preset_key: The preset key

    Returns:
        ThemePreset if found, None otherwise
    """
    presets = get_theme_presets()
    return presets.get(media_type, {}).get(preset_key)


def build_theme_filter_params(preset: ThemePreset) -> dict[str, Any]:
    """Extract filter parameters from a theme preset.

    Converts the theme preset's filter chain into individual
    filter parameters that can be used by the processing pipeline.

    Args:
        preset: The theme preset

    Returns:
        Dictionary mapping filter types to their parameters
    """
    params = {}
    for filter_step in preset.filters:
        params[filter_step.type] = filter_step.params
    return params
