"""Pydantic models for audio processing."""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class PresetLevel(str, Enum):
    """Tunnel effect intensity presets."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    EXTREME = "extreme"


class PresetConfig(BaseModel):
    """Configuration for a preset effect level."""
    name: str
    description: str
    volume: float
    highpass: int
    lowpass: int
    delays: list[int]
    decays: list[float]


PRESETS: dict[PresetLevel, PresetConfig] = {
    PresetLevel.NONE: PresetConfig(
        name="No Effect",
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
        description="Strong cave effect, slightly distant voice",
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


# ============ CATEGORY: VOLUME ============
class VolumePreset(str, Enum):
    """Volume/gain presets."""
    X1 = "1x"
    X1_5 = "1.5x"
    X2 = "2x"
    X3 = "3x"
    X4 = "4x"


class VolumeConfig(BaseModel):
    """Configuration for volume preset."""
    name: str
    description: str
    volume: float


VOLUME_PRESETS: dict[VolumePreset, VolumeConfig] = {
    VolumePreset.X1: VolumeConfig(
        name="1x",
        description="Original volume",
        volume=1.0,
    ),
    VolumePreset.X1_5: VolumeConfig(
        name="1.5x",
        description="Slight boost",
        volume=1.5,
    ),
    VolumePreset.X2: VolumeConfig(
        name="2x",
        description="Double volume",
        volume=2.0,
    ),
    VolumePreset.X3: VolumeConfig(
        name="3x",
        description="Triple volume",
        volume=3.0,
    ),
    VolumePreset.X4: VolumeConfig(
        name="4x",
        description="Maximum boost",
        volume=4.0,
    ),
}


# ============ CATEGORY: TUNNEL ============
class TunnelPreset(str, Enum):
    """Tunnel/echo effect presets."""
    NONE = "none"
    SUBTLE = "subtle"
    MEDIUM = "medium"
    HEAVY = "heavy"
    EXTREME = "extreme"


class TunnelConfig(BaseModel):
    """Configuration for tunnel preset."""
    name: str
    description: str
    delays: list[int]
    decays: list[float]


TUNNEL_PRESETS: dict[TunnelPreset, TunnelConfig] = {
    TunnelPreset.NONE: TunnelConfig(
        name="None",
        description="No echo effect",
        delays=[1],
        decays=[0.0],
    ),
    TunnelPreset.SUBTLE: TunnelConfig(
        name="Subtle",
        description="Light ambience",
        delays=[10, 20],
        decays=[0.2, 0.15],
    ),
    TunnelPreset.MEDIUM: TunnelConfig(
        name="Medium",
        description="Noticeable reverb",
        delays=[15, 25, 35, 50],
        decays=[0.35, 0.3, 0.25, 0.2],
    ),
    TunnelPreset.HEAVY: TunnelConfig(
        name="Heavy",
        description="Strong cave effect",
        delays=[20, 35, 55, 80],
        decays=[0.4, 0.35, 0.3, 0.25],
    ),
    TunnelPreset.EXTREME: TunnelConfig(
        name="Extreme",
        description="Deep bunker sound",
        delays=[25, 45, 70, 100, 140],
        decays=[0.45, 0.4, 0.35, 0.3, 0.25],
    ),
}


# ============ CATEGORY: FREQUENCY ============
class FrequencyPreset(str, Enum):
    """Frequency/EQ presets."""
    FLAT = "flat"
    BASS_CUT = "bass_cut"
    TREBLE_CUT = "treble_cut"
    NARROW = "narrow"
    VOICE = "voice"


class FrequencyConfig(BaseModel):
    """Configuration for frequency preset."""
    name: str
    description: str
    highpass: int
    lowpass: int


FREQUENCY_PRESETS: dict[FrequencyPreset, FrequencyConfig] = {
    FrequencyPreset.FLAT: FrequencyConfig(
        name="Flat",
        description="Full spectrum",
        highpass=20,
        lowpass=20000,
    ),
    FrequencyPreset.BASS_CUT: FrequencyConfig(
        name="Bass Cut",
        description="Remove low frequencies",
        highpass=200,
        lowpass=20000,
    ),
    FrequencyPreset.TREBLE_CUT: FrequencyConfig(
        name="Treble Cut",
        description="Remove high frequencies",
        highpass=20,
        lowpass=4000,
    ),
    FrequencyPreset.NARROW: FrequencyConfig(
        name="Narrow Band",
        description="Voice-focused range",
        highpass=150,
        lowpass=3500,
    ),
    FrequencyPreset.VOICE: FrequencyConfig(
        name="Voice Clarity",
        description="Optimal for speech",
        highpass=100,
        lowpass=6000,
    ),
}

# String-keyed dictionaries for Jinja template access
VOLUME_PRESETS_BY_STR: dict[str, VolumeConfig] = {p.value: c for p, c in VOLUME_PRESETS.items()}
TUNNEL_PRESETS_BY_STR: dict[str, TunnelConfig] = {p.value: c for p, c in TUNNEL_PRESETS.items()}
FREQUENCY_PRESETS_BY_STR: dict[str, FrequencyConfig] = {p.value: c for p, c in FREQUENCY_PRESETS.items()}


# ============ USER SETTINGS ============
class CategorySettings(BaseModel):
    """Settings for a single effect category."""
    preset: str
    custom_values: dict = {}


class UserSettings(BaseModel):
    """Complete user settings for all categories."""
    volume: CategorySettings = CategorySettings(preset="2x")
    tunnel: CategorySettings = CategorySettings(preset="none")
    frequency: CategorySettings = CategorySettings(preset="flat")
    active_category: str = "volume"


class ProcessRequest(BaseModel):
    """Request model for audio processing."""
    input_file: str
    start_time: str = "00:00:00"
    end_time: str = "00:00:06"
    preset: PresetLevel = PresetLevel.NONE
    volume: float = Field(default=2.0, ge=0.5, le=4.0)
    highpass: int = Field(default=100, ge=50, le=500)
    lowpass: int = Field(default=4500, ge=2000, le=8000)
    delays: str = "15|25|35|50"
    decays: str = "0.35|0.3|0.25|0.2"


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
