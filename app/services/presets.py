"""Presets loader service - loads effect presets from YAML file."""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from pydantic import ValidationError

from app.models import (
    # Audio configs
    VolumeConfig,
    TunnelConfig,
    FrequencyConfig,
    SpeedConfig,
    PitchConfig,
    NoiseReductionConfig,
    CompressorConfig,
    # Video configs
    BrightnessConfig,
    ContrastConfig,
    SaturationConfig,
    BlurConfig,
    SharpenConfig,
    TransformConfig,
)


# Global preset storage (populated on load)
_presets: dict[str, dict[str, Any]] = {}

# Config class mapping for validation
CONFIG_CLASSES = {
    "audio": {
        "volume": VolumeConfig,
        "tunnel": TunnelConfig,
        "frequency": FrequencyConfig,
        "speed": SpeedConfig,
        "pitch": PitchConfig,
        "noise_reduction": NoiseReductionConfig,
        "compressor": CompressorConfig,
    },
    "video": {
        "brightness": BrightnessConfig,
        "contrast": ContrastConfig,
        "saturation": SaturationConfig,
        "blur": BlurConfig,
        "sharpen": SharpenConfig,
        "transform": TransformConfig,
    },
}


def load_presets(presets_file: Path | str = "presets.yml") -> dict[str, dict[str, Any]]:
    """Load and validate presets from YAML file.

    Args:
        presets_file: Path to the presets YAML file

    Returns:
        Dictionary with validated presets organized by category

    Raises:
        FileNotFoundError: If presets file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        ValidationError: If preset data doesn't match schema
    """
    global _presets

    presets_path = Path(presets_file)
    if not presets_path.exists():
        raise FileNotFoundError(f"Presets file not found: {presets_path}")

    logger.info(f"Loading presets from {presets_path}")

    with open(presets_path, "r") as f:
        raw_data = yaml.safe_load(f)

    validated_presets = {"audio": {}, "video": {}}

    # Validate audio presets
    for category, config_class in CONFIG_CLASSES["audio"].items():
        if category not in raw_data.get("audio", {}):
            logger.warning(f"Missing audio category: {category}")
            validated_presets["audio"][category] = {}
            continue

        category_presets = {}
        for preset_key, preset_data in raw_data["audio"][category].items():
            try:
                validated = config_class(**preset_data)
                category_presets[preset_key] = validated
            except ValidationError as e:
                logger.error(f"Invalid preset {category}/{preset_key}: {e}")
                raise

        validated_presets["audio"][category] = category_presets
        logger.debug(f"Loaded {len(category_presets)} {category} presets")

    # Validate video presets
    for category, config_class in CONFIG_CLASSES["video"].items():
        if category not in raw_data.get("video", {}):
            logger.warning(f"Missing video category: {category}")
            validated_presets["video"][category] = {}
            continue

        category_presets = {}
        for preset_key, preset_data in raw_data["video"][category].items():
            try:
                validated = config_class(**preset_data)
                category_presets[preset_key] = validated
            except ValidationError as e:
                logger.error(f"Invalid preset {category}/{preset_key}: {e}")
                raise

        validated_presets["video"][category] = category_presets
        logger.debug(f"Loaded {len(category_presets)} {category} presets")

    _presets = validated_presets

    total = sum(
        len(presets)
        for group in validated_presets.values()
        for presets in group.values()
    )
    logger.info(f"Loaded {total} presets from {presets_path}")

    return validated_presets


def get_presets() -> dict[str, dict[str, Any]]:
    """Get the loaded presets dictionary."""
    if not _presets:
        load_presets()
    return _presets


def get_audio_presets(category: str) -> dict[str, Any]:
    """Get presets for a specific audio category.

    Args:
        category: Category name (volume, tunnel, frequency, etc.)

    Returns:
        Dictionary of preset_key -> config for the category
    """
    presets = get_presets()
    return presets.get("audio", {}).get(category, {})


def get_video_presets(category: str) -> dict[str, Any]:
    """Get presets for a specific video category.

    Args:
        category: Category name (brightness, contrast, etc.)

    Returns:
        Dictionary of preset_key -> config for the category
    """
    presets = get_presets()
    return presets.get("video", {}).get(category, {})


# Convenience accessors for common use
def get_volume_presets() -> dict[str, VolumeConfig]:
    return get_audio_presets("volume")


def get_tunnel_presets() -> dict[str, TunnelConfig]:
    return get_audio_presets("tunnel")


def get_frequency_presets() -> dict[str, FrequencyConfig]:
    return get_audio_presets("frequency")


def get_speed_presets() -> dict[str, SpeedConfig]:
    return get_audio_presets("speed")


def get_pitch_presets() -> dict[str, PitchConfig]:
    return get_audio_presets("pitch")


def get_noise_reduction_presets() -> dict[str, NoiseReductionConfig]:
    return get_audio_presets("noise_reduction")


def get_compressor_presets() -> dict[str, CompressorConfig]:
    return get_audio_presets("compressor")


def get_brightness_presets() -> dict[str, BrightnessConfig]:
    return get_video_presets("brightness")


def get_contrast_presets() -> dict[str, ContrastConfig]:
    return get_video_presets("contrast")


def get_saturation_presets() -> dict[str, SaturationConfig]:
    return get_video_presets("saturation")


def get_blur_presets() -> dict[str, BlurConfig]:
    return get_video_presets("blur")


def get_sharpen_presets() -> dict[str, SharpenConfig]:
    return get_video_presets("sharpen")


def get_transform_presets() -> dict[str, TransformConfig]:
    return get_video_presets("transform")
