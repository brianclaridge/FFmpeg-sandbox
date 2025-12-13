"""Audio filter builders for FFmpeg."""

import math


def build_speed_filter(speed: float) -> str:
    """
    Build atempo filter for speed adjustment.

    FFmpeg atempo only supports 0.5-2.0 range, so we chain multiple
    filters for values outside this range.
    """
    if speed == 1.0:
        return ""

    filters = []
    remaining = speed

    # Chain atempo filters to achieve desired speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5

    # Add final atempo for remaining adjustment
    if 0.5 <= remaining <= 2.0 and remaining != 1.0:
        filters.append(f"atempo={remaining}")

    return ",".join(filters)


def build_pitch_filter(semitones: float, sample_rate: int = 44100) -> str:
    """
    Build pitch shift filter using asetrate + atempo.

    This shifts pitch without changing playback speed by:
    1. Changing sample rate to shift pitch
    2. Using atempo to compensate for speed change
    """
    if semitones == 0.0:
        return ""

    # Calculate the pitch ratio (2^(semitones/12))
    ratio = math.pow(2, semitones / 12)

    # asetrate changes pitch, atempo compensates speed
    new_rate = int(sample_rate * ratio)
    tempo_compensation = 1 / ratio

    return f"asetrate={new_rate},atempo={tempo_compensation:.6f},aresample={sample_rate}"


def build_noise_reduction_filter(noise_floor: float, noise_reduction: float) -> str:
    """
    Build afftdn (FFT-based denoiser) filter.

    Args:
        noise_floor: Noise floor in dB (-20 to -80)
        noise_reduction: Reduction amount (0.0 to 1.0)
    """
    if noise_reduction == 0.0:
        return ""

    return f"afftdn=nf={noise_floor}:nr={noise_reduction * 100}"


def build_compressor_filter(
    threshold: float,
    ratio: float,
    attack: float,
    release: float,
    makeup: float,
) -> str:
    """
    Build acompressor filter for dynamic range compression.

    Args:
        threshold: dB level where compression starts
        ratio: Compression ratio (e.g., 4 = 4:1)
        attack: Attack time in ms
        release: Release time in ms
        makeup: Makeup gain in dB
    """
    if ratio <= 1.0:
        return ""

    return (
        f"acompressor=threshold={threshold}dB:ratio={ratio}:"
        f"attack={attack}:release={release}:makeup={makeup}dB"
    )
