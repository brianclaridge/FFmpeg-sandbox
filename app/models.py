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
    NONE = "none"
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
    VolumePreset.NONE: VolumeConfig(
        name="None",
        description="No effect (original)",
        volume=1.0,
    ),
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

# ============ CATEGORY: SPEED ============
class SpeedPreset(str, Enum):
    """Playback speed presets."""
    NONE = "none"
    X0_5 = "0.5x"
    X0_75 = "0.75x"
    X1 = "1x"
    X1_25 = "1.25x"
    X1_5 = "1.5x"
    X2 = "2x"


class SpeedConfig(BaseModel):
    """Configuration for speed preset."""
    name: str
    description: str
    speed: float  # atempo value


SPEED_PRESETS: dict[SpeedPreset, SpeedConfig] = {
    SpeedPreset.NONE: SpeedConfig(
        name="None",
        description="No speed change",
        speed=1.0,
    ),
    SpeedPreset.X0_5: SpeedConfig(
        name="0.5x",
        description="Half speed (slow)",
        speed=0.5,
    ),
    SpeedPreset.X0_75: SpeedConfig(
        name="0.75x",
        description="Slightly slower",
        speed=0.75,
    ),
    SpeedPreset.X1: SpeedConfig(
        name="1x",
        description="Normal speed",
        speed=1.0,
    ),
    SpeedPreset.X1_25: SpeedConfig(
        name="1.25x",
        description="Slightly faster",
        speed=1.25,
    ),
    SpeedPreset.X1_5: SpeedConfig(
        name="1.5x",
        description="Faster",
        speed=1.5,
    ),
    SpeedPreset.X2: SpeedConfig(
        name="2x",
        description="Double speed",
        speed=2.0,
    ),
}


# ============ CATEGORY: PITCH ============
class PitchPreset(str, Enum):
    """Pitch shift presets."""
    NONE = "none"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CHIPMUNK = "chipmunk"


class PitchConfig(BaseModel):
    """Configuration for pitch preset."""
    name: str
    description: str
    semitones: float  # Pitch shift in semitones


PITCH_PRESETS: dict[PitchPreset, PitchConfig] = {
    PitchPreset.NONE: PitchConfig(
        name="None",
        description="No pitch change",
        semitones=0.0,
    ),
    PitchPreset.LOW: PitchConfig(
        name="Low",
        description="Lower pitch (-4 semitones)",
        semitones=-4.0,
    ),
    PitchPreset.NORMAL: PitchConfig(
        name="Normal",
        description="Original pitch",
        semitones=0.0,
    ),
    PitchPreset.HIGH: PitchConfig(
        name="High",
        description="Higher pitch (+4 semitones)",
        semitones=4.0,
    ),
    PitchPreset.CHIPMUNK: PitchConfig(
        name="Chipmunk",
        description="Very high pitch (+8 semitones)",
        semitones=8.0,
    ),
}


# ============ CATEGORY: NOISE REDUCTION ============
class NoiseReductionPreset(str, Enum):
    """Noise reduction presets."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class NoiseReductionConfig(BaseModel):
    """Configuration for noise reduction preset."""
    name: str
    description: str
    noise_floor: float  # afftdn nr parameter (-20 to -80 dB)
    noise_reduction: float  # afftdn nf parameter (0.0 to 1.0)


NOISE_REDUCTION_PRESETS: dict[NoiseReductionPreset, NoiseReductionConfig] = {
    NoiseReductionPreset.NONE: NoiseReductionConfig(
        name="None",
        description="No noise reduction",
        noise_floor=-25.0,
        noise_reduction=0.0,
    ),
    NoiseReductionPreset.LIGHT: NoiseReductionConfig(
        name="Light",
        description="Subtle noise reduction",
        noise_floor=-30.0,
        noise_reduction=0.5,
    ),
    NoiseReductionPreset.MEDIUM: NoiseReductionConfig(
        name="Medium",
        description="Moderate noise reduction",
        noise_floor=-40.0,
        noise_reduction=0.7,
    ),
    NoiseReductionPreset.HEAVY: NoiseReductionConfig(
        name="Heavy",
        description="Aggressive noise reduction",
        noise_floor=-50.0,
        noise_reduction=0.9,
    ),
}


# ============ CATEGORY: COMPRESSOR ============
class CompressorPreset(str, Enum):
    """Audio compressor presets."""
    NONE = "none"
    LIGHT = "light"
    PODCAST = "podcast"
    BROADCAST = "broadcast"


class CompressorConfig(BaseModel):
    """Configuration for compressor preset."""
    name: str
    description: str
    threshold: float  # dB level where compression kicks in
    ratio: float  # Compression ratio (e.g., 4 = 4:1)
    attack: float  # Attack time in ms
    release: float  # Release time in ms
    makeup: float  # Makeup gain in dB


COMPRESSOR_PRESETS: dict[CompressorPreset, CompressorConfig] = {
    CompressorPreset.NONE: CompressorConfig(
        name="None",
        description="No compression",
        threshold=0.0,
        ratio=1.0,
        attack=20.0,
        release=250.0,
        makeup=0.0,
    ),
    CompressorPreset.LIGHT: CompressorConfig(
        name="Light",
        description="Subtle dynamic control",
        threshold=-20.0,
        ratio=2.0,
        attack=20.0,
        release=200.0,
        makeup=2.0,
    ),
    CompressorPreset.PODCAST: CompressorConfig(
        name="Podcast",
        description="Voice-optimized compression",
        threshold=-18.0,
        ratio=4.0,
        attack=10.0,
        release=150.0,
        makeup=4.0,
    ),
    CompressorPreset.BROADCAST: CompressorConfig(
        name="Broadcast",
        description="Broadcast-style limiting",
        threshold=-12.0,
        ratio=8.0,
        attack=5.0,
        release=100.0,
        makeup=6.0,
    ),
}


# ============ VIDEO EFFECTS ============

# ============ VIDEO: BRIGHTNESS ============
class BrightnessPreset(str, Enum):
    """Brightness presets."""
    NONE = "none"
    DARK = "dark"
    NORMAL = "normal"
    BRIGHT = "bright"


class BrightnessConfig(BaseModel):
    """Configuration for brightness preset."""
    name: str
    description: str
    brightness: float  # eq brightness (-1.0 to 1.0)


BRIGHTNESS_PRESETS: dict[BrightnessPreset, BrightnessConfig] = {
    BrightnessPreset.NONE: BrightnessConfig(
        name="None",
        description="No brightness change",
        brightness=0.0,
    ),
    BrightnessPreset.DARK: BrightnessConfig(
        name="Dark",
        description="Darker image (-0.2)",
        brightness=-0.2,
    ),
    BrightnessPreset.NORMAL: BrightnessConfig(
        name="Normal",
        description="Original brightness",
        brightness=0.0,
    ),
    BrightnessPreset.BRIGHT: BrightnessConfig(
        name="Bright",
        description="Brighter image (+0.2)",
        brightness=0.2,
    ),
}


# ============ VIDEO: CONTRAST ============
class ContrastPreset(str, Enum):
    """Contrast presets."""
    NONE = "none"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ContrastConfig(BaseModel):
    """Configuration for contrast preset."""
    name: str
    description: str
    contrast: float  # eq contrast (0.0 to 2.0, 1.0 is normal)


CONTRAST_PRESETS: dict[ContrastPreset, ContrastConfig] = {
    ContrastPreset.NONE: ContrastConfig(
        name="None",
        description="No contrast change",
        contrast=1.0,
    ),
    ContrastPreset.LOW: ContrastConfig(
        name="Low",
        description="Reduced contrast",
        contrast=0.8,
    ),
    ContrastPreset.NORMAL: ContrastConfig(
        name="Normal",
        description="Original contrast",
        contrast=1.0,
    ),
    ContrastPreset.HIGH: ContrastConfig(
        name="High",
        description="Increased contrast",
        contrast=1.3,
    ),
}


# ============ VIDEO: SATURATION ============
class SaturationPreset(str, Enum):
    """Saturation presets."""
    NONE = "none"
    GRAYSCALE = "grayscale"
    MUTED = "muted"
    NORMAL = "normal"
    VIVID = "vivid"


class SaturationConfig(BaseModel):
    """Configuration for saturation preset."""
    name: str
    description: str
    saturation: float  # eq saturation (0.0 to 3.0, 1.0 is normal)


SATURATION_PRESETS: dict[SaturationPreset, SaturationConfig] = {
    SaturationPreset.NONE: SaturationConfig(
        name="None",
        description="No saturation change",
        saturation=1.0,
    ),
    SaturationPreset.GRAYSCALE: SaturationConfig(
        name="Grayscale",
        description="Black and white",
        saturation=0.0,
    ),
    SaturationPreset.MUTED: SaturationConfig(
        name="Muted",
        description="Reduced colors",
        saturation=0.5,
    ),
    SaturationPreset.NORMAL: SaturationConfig(
        name="Normal",
        description="Original saturation",
        saturation=1.0,
    ),
    SaturationPreset.VIVID: SaturationConfig(
        name="Vivid",
        description="Enhanced colors",
        saturation=1.5,
    ),
}


# ============ VIDEO: BLUR ============
class BlurPreset(str, Enum):
    """Blur presets."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class BlurConfig(BaseModel):
    """Configuration for blur preset."""
    name: str
    description: str
    sigma: float  # gblur sigma (0 = no blur)


BLUR_PRESETS: dict[BlurPreset, BlurConfig] = {
    BlurPreset.NONE: BlurConfig(
        name="None",
        description="No blur",
        sigma=0.0,
    ),
    BlurPreset.LIGHT: BlurConfig(
        name="Light",
        description="Subtle blur",
        sigma=1.0,
    ),
    BlurPreset.MEDIUM: BlurConfig(
        name="Medium",
        description="Moderate blur",
        sigma=3.0,
    ),
    BlurPreset.HEAVY: BlurConfig(
        name="Heavy",
        description="Strong blur",
        sigma=6.0,
    ),
}


# ============ VIDEO: SHARPEN ============
class SharpenPreset(str, Enum):
    """Sharpen presets."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    STRONG = "strong"


class SharpenConfig(BaseModel):
    """Configuration for sharpen preset."""
    name: str
    description: str
    amount: float  # unsharp luma_amount (0-3, 1 is moderate)


SHARPEN_PRESETS: dict[SharpenPreset, SharpenConfig] = {
    SharpenPreset.NONE: SharpenConfig(
        name="None",
        description="No sharpening",
        amount=0.0,
    ),
    SharpenPreset.LIGHT: SharpenConfig(
        name="Light",
        description="Subtle sharpening",
        amount=0.5,
    ),
    SharpenPreset.MEDIUM: SharpenConfig(
        name="Medium",
        description="Moderate sharpening",
        amount=1.0,
    ),
    SharpenPreset.STRONG: SharpenConfig(
        name="Strong",
        description="Strong sharpening",
        amount=1.5,
    ),
}


# ============ VIDEO: TRANSFORM ============
class TransformPreset(str, Enum):
    """Transform presets."""
    NONE = "none"
    FLIP_H = "flip_h"
    FLIP_V = "flip_v"
    ROTATE_90 = "rotate_90"
    ROTATE_180 = "rotate_180"
    ROTATE_270 = "rotate_270"


class TransformConfig(BaseModel):
    """Configuration for transform preset."""
    name: str
    description: str
    filter: str  # FFmpeg filter (hflip, vflip, transpose=1, etc.)


TRANSFORM_PRESETS: dict[TransformPreset, TransformConfig] = {
    TransformPreset.NONE: TransformConfig(
        name="None",
        description="No transform",
        filter="",
    ),
    TransformPreset.FLIP_H: TransformConfig(
        name="Flip H",
        description="Horizontal flip",
        filter="hflip",
    ),
    TransformPreset.FLIP_V: TransformConfig(
        name="Flip V",
        description="Vertical flip",
        filter="vflip",
    ),
    TransformPreset.ROTATE_90: TransformConfig(
        name="90°",
        description="Rotate 90° clockwise",
        filter="transpose=1",
    ),
    TransformPreset.ROTATE_180: TransformConfig(
        name="180°",
        description="Rotate 180°",
        filter="transpose=1,transpose=1",
    ),
    TransformPreset.ROTATE_270: TransformConfig(
        name="270°",
        description="Rotate 270° clockwise",
        filter="transpose=2",
    ),
}


# String-keyed dictionaries for Jinja template access
VOLUME_PRESETS_BY_STR: dict[str, VolumeConfig] = {p.value: c for p, c in VOLUME_PRESETS.items()}
TUNNEL_PRESETS_BY_STR: dict[str, TunnelConfig] = {p.value: c for p, c in TUNNEL_PRESETS.items()}
FREQUENCY_PRESETS_BY_STR: dict[str, FrequencyConfig] = {p.value: c for p, c in FREQUENCY_PRESETS.items()}
SPEED_PRESETS_BY_STR: dict[str, SpeedConfig] = {p.value: c for p, c in SPEED_PRESETS.items()}
PITCH_PRESETS_BY_STR: dict[str, PitchConfig] = {p.value: c for p, c in PITCH_PRESETS.items()}
NOISE_REDUCTION_PRESETS_BY_STR: dict[str, NoiseReductionConfig] = {p.value: c for p, c in NOISE_REDUCTION_PRESETS.items()}
COMPRESSOR_PRESETS_BY_STR: dict[str, CompressorConfig] = {p.value: c for p, c in COMPRESSOR_PRESETS.items()}
# Video effect presets
BRIGHTNESS_PRESETS_BY_STR: dict[str, BrightnessConfig] = {p.value: c for p, c in BRIGHTNESS_PRESETS.items()}
CONTRAST_PRESETS_BY_STR: dict[str, ContrastConfig] = {p.value: c for p, c in CONTRAST_PRESETS.items()}
SATURATION_PRESETS_BY_STR: dict[str, SaturationConfig] = {p.value: c for p, c in SATURATION_PRESETS.items()}
BLUR_PRESETS_BY_STR: dict[str, BlurConfig] = {p.value: c for p, c in BLUR_PRESETS.items()}
SHARPEN_PRESETS_BY_STR: dict[str, SharpenConfig] = {p.value: c for p, c in SHARPEN_PRESETS.items()}
TRANSFORM_PRESETS_BY_STR: dict[str, TransformConfig] = {p.value: c for p, c in TRANSFORM_PRESETS.items()}


# ============ USER SETTINGS ============
class CategorySettings(BaseModel):
    """Settings for a single effect category."""
    preset: str
    custom_values: dict = {}


class UserSettings(BaseModel):
    """Complete user settings for all categories."""
    # Audio effects
    volume: CategorySettings = CategorySettings(preset="none")
    tunnel: CategorySettings = CategorySettings(preset="none")
    frequency: CategorySettings = CategorySettings(preset="flat")
    speed: CategorySettings = CategorySettings(preset="none")
    pitch: CategorySettings = CategorySettings(preset="none")
    noise_reduction: CategorySettings = CategorySettings(preset="none")
    compressor: CategorySettings = CategorySettings(preset="none")
    # Video effects
    brightness: CategorySettings = CategorySettings(preset="none")
    contrast: CategorySettings = CategorySettings(preset="none")
    saturation: CategorySettings = CategorySettings(preset="none")
    blur: CategorySettings = CategorySettings(preset="none")
    sharpen: CategorySettings = CategorySettings(preset="none")
    transform: CategorySettings = CategorySettings(preset="none")
    active_category: str = "volume"
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
    frequency_preset: str = "flat"
