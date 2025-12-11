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
