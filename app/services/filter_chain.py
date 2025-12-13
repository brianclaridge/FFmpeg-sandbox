"""Filter chain builders that aggregate individual filters."""

from app.services.filters_audio import (
    build_speed_filter,
    build_pitch_filter,
    build_noise_reduction_filter,
    build_compressor_filter,
)
from app.services.filters_video import (
    build_eq_filter,
    build_blur_filter,
    build_sharpen_filter,
    build_transform_filter,
)


def build_audio_filter_chain(
    volume: float = 1.0,
    highpass: int = 20,
    lowpass: int = 20000,
    delays: str = "",
    decays: str = "",
    speed: float = 1.0,
    pitch_semitones: float = 0.0,
    noise_floor: float = -25.0,
    noise_reduction: float = 0.0,
    comp_threshold: float = 0.0,
    comp_ratio: float = 1.0,
    comp_attack: float = 20.0,
    comp_release: float = 250.0,
    comp_makeup: float = 0.0,
) -> str | None:
    """
    Build complete audio filter chain from all audio effect settings.

    Returns None if no effects are active.
    """
    filters = []

    # Volume
    if volume != 1.0:
        filters.append(f"volume={volume}")

    # Frequency (highpass/lowpass)
    if highpass > 20:
        filters.append(f"highpass=f={highpass}")
    if lowpass < 20000:
        filters.append(f"lowpass=f={lowpass}")

    # Tunnel/echo
    if delays and decays:
        decay_values = [float(d) for d in decays.split("|") if d.strip()]
        if any(d > 0 for d in decay_values):
            filters.append(f"aecho=0.8:0.85:{delays}:{decays}")

    # Speed
    speed_filter = build_speed_filter(speed)
    if speed_filter:
        filters.append(speed_filter)

    # Pitch
    pitch_filter = build_pitch_filter(pitch_semitones)
    if pitch_filter:
        filters.append(pitch_filter)

    # Noise reduction
    nr_filter = build_noise_reduction_filter(noise_floor, noise_reduction)
    if nr_filter:
        filters.append(nr_filter)

    # Compressor
    comp_filter = build_compressor_filter(
        comp_threshold, comp_ratio, comp_attack, comp_release, comp_makeup
    )
    if comp_filter:
        filters.append(comp_filter)

    return ",".join(filters) if filters else None


def build_video_filter_chain(
    brightness: float = 0.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    blur_sigma: float = 0.0,
    sharpen_amount: float = 0.0,
    transform: str = "",
    speed: float = 1.0,
) -> str | None:
    """
    Build complete video filter chain from all video effect settings.

    Returns None if no effects are active.
    """
    filters = []

    # EQ (brightness/contrast/saturation)
    eq_filter = build_eq_filter(brightness, contrast, saturation)
    if eq_filter:
        filters.append(eq_filter)

    # Blur
    blur_filter = build_blur_filter(blur_sigma)
    if blur_filter:
        filters.append(blur_filter)

    # Sharpen
    sharpen_filter = build_sharpen_filter(sharpen_amount)
    if sharpen_filter:
        filters.append(sharpen_filter)

    # Transform
    transform_filter = build_transform_filter(transform)
    if transform_filter:
        filters.append(transform_filter)

    # Speed (video uses setpts)
    if speed != 1.0:
        pts_factor = 1 / speed
        filters.append(f"setpts={pts_factor}*PTS")

    return ",".join(filters) if filters else None
