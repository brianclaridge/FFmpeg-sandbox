"""Pydantic models for audio processing."""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ============ LEGACY PRESET (used by /partials/sliders endpoint) ============
class PresetLevel(str, Enum):
    """Tunnel filter intensity presets."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    EXTREME = "extreme"


class PresetConfig(BaseModel):
    """Configuration for a preset filter level."""
    name: str
    description: str
    volume: float
    highpass: int
    lowpass: int
    delays: list[int]
    decays: list[float]


PRESETS: dict[PresetLevel, PresetConfig] = {
    PresetLevel.NONE: PresetConfig(
        name="No Filter",
        description="Clean audio, no tunnel processing",
        volume=1.0,
        highpass=20,
        lowpass=20000,
        delays=[1],
        decays=[0.0],
    ),
    PresetLevel.LIGHT: PresetConfig(
        name="Light Tunnel",
        description="Subtle ambience, voice very clear",
        volume=2.0,
        highpass=80,
        lowpass=6000,
        delays=[10, 20],
        decays=[0.2, 0.15],
    ),
    PresetLevel.MEDIUM: PresetConfig(
        name="Medium Tunnel",
        description="Noticeable reverb, voice still clear",
        volume=2.0,
        highpass=100,
        lowpass=4500,
        delays=[15, 25, 35, 50],
        decays=[0.35, 0.3, 0.25, 0.2],
    ),
    PresetLevel.HEAVY: PresetConfig(
        name="Heavy Tunnel",
        description="Strong cave sound, slightly distant voice",
        volume=2.0,
        highpass=120,
        lowpass=3500,
        delays=[20, 35, 55, 80],
        decays=[0.4, 0.35, 0.3, 0.25],
    ),
    PresetLevel.EXTREME: PresetConfig(
        name="Extreme Tunnel",
        description="Deep bunker sound, heavily processed voice",
        volume=2.0,
        highpass=150,
        lowpass=2500,
        delays=[25, 45, 70, 100, 140],
        decays=[0.45, 0.4, 0.35, 0.3, 0.25],
    ),
}


# ============ AUDIO FILTER CONFIG SCHEMAS ============
# These are used by presets.py to validate YAML presets

class VolumeConfig(BaseModel):
    """Configuration for volume preset."""
    name: str
    description: str
    volume: float
    preset_category: str = "General"
    is_user_preset: bool = False


class TunnelConfig(BaseModel):
    """Configuration for tunnel preset."""
    name: str
    description: str
    delays: list[int]
    decays: list[float]
    preset_category: str = "General"
    is_user_preset: bool = False


class FrequencyConfig(BaseModel):
    """Configuration for frequency preset."""
    name: str
    description: str
    highpass: int
    lowpass: int
    preset_category: str = "General"
    is_user_preset: bool = False


class SpeedConfig(BaseModel):
    """Configuration for speed preset."""
    name: str
    description: str
    speed: float = Field(ge=0.25, le=4.0, description="Speed multiplier (0.25-4.0)")
    preset_category: str = "General"
    is_user_preset: bool = False


class PitchConfig(BaseModel):
    """Configuration for pitch preset."""
    name: str
    description: str
    semitones: float = Field(ge=-12.0, le=12.0, description="Pitch shift in semitones (-12 to +12)")
    preset_category: str = "General"
    is_user_preset: bool = False


class NoiseReductionConfig(BaseModel):
    """Configuration for noise reduction preset."""
    name: str
    description: str
    noise_floor: float = Field(ge=-80.0, le=-20.0, description="Noise floor in dB (-80 to -20)")
    noise_reduction: float = Field(ge=0.0, le=1.0, description="Reduction amount (0.0-1.0)")
    preset_category: str = "General"
    is_user_preset: bool = False


class CompressorConfig(BaseModel):
    """Configuration for compressor preset."""
    name: str
    description: str
    threshold: float
    ratio: float
    attack: float
    release: float
    makeup: float
    preset_category: str = "General"
    is_user_preset: bool = False


# ============ VIDEO FILTER CONFIG SCHEMAS ============

class BrightnessConfig(BaseModel):
    """Configuration for brightness preset."""
    name: str
    description: str
    brightness: float
    preset_category: str = "General"
    is_user_preset: bool = False


class ContrastConfig(BaseModel):
    """Configuration for contrast preset."""
    name: str
    description: str
    contrast: float
    preset_category: str = "General"
    is_user_preset: bool = False


class SaturationConfig(BaseModel):
    """Configuration for saturation preset."""
    name: str
    description: str
    saturation: float
    preset_category: str = "General"
    is_user_preset: bool = False


class BlurConfig(BaseModel):
    """Configuration for blur preset."""
    name: str
    description: str
    sigma: float
    preset_category: str = "General"
    is_user_preset: bool = False


class SharpenConfig(BaseModel):
    """Configuration for sharpen preset."""
    name: str
    description: str
    amount: float
    preset_category: str = "General"
    is_user_preset: bool = False


class TransformConfig(BaseModel):
    """Configuration for transform preset."""
    name: str
    description: str
    filter: str
    preset_category: str = "General"
    is_user_preset: bool = False


# ============ USER SETTINGS ============

class CategorySettings(BaseModel):
    """Settings for a single filter category."""
    preset: str
    custom_values: dict = {}


class UserSettings(BaseModel):
    """Complete user settings for all categories."""
    # Audio filters
    volume: CategorySettings = CategorySettings(preset="none")
    tunnel: CategorySettings = CategorySettings(preset="none")
    frequency: CategorySettings = CategorySettings(preset="none")
    speed: CategorySettings = CategorySettings(preset="none")
    pitch: CategorySettings = CategorySettings(preset="none")
    noise_reduction: CategorySettings = CategorySettings(preset="none")
    compressor: CategorySettings = CategorySettings(preset="none")
    # Video filters
    brightness: CategorySettings = CategorySettings(preset="none")
    contrast: CategorySettings = CategorySettings(preset="none")
    saturation: CategorySettings = CategorySettings(preset="none")
    blur: CategorySettings = CategorySettings(preset="none")
    sharpen: CategorySettings = CategorySettings(preset="none")
    transform: CategorySettings = CategorySettings(preset="none")
    active_category: str = ""
    active_tab: str = "audio"


class ProcessRequest(BaseModel):
    """Request model for audio processing."""
    input_file: str
    start_time: str = "00:00:00"
    end_time: str = "00:00:06"
    preset: PresetLevel = PresetLevel.NONE
    volume: float = Field(default=1.0, ge=0.0, le=4.0)
    highpass: int = Field(default=20, ge=20, le=500)
    lowpass: int = Field(default=20000, ge=2000, le=20000)
    delays: str = "1"
    decays: str = "0"


class HistoryEntry(BaseModel):
    """Model for processing history entry."""
    id: str
    timestamp: datetime
    input_file: str
    output_file: str
    start_time: str
    end_time: str
    preset: str
    volume: float
    highpass: int
    lowpass: int
    delays: str
    decays: str
    # Effect chain preset names
    volume_preset: str = "none"
    tunnel_preset: str = "none"
    frequency_preset: str = "none"
