"""Service modules for audio/video processing."""

# Metadata and file operations
from app.services.metadata import (
    format_duration_ms,
    format_file_size,
    format_bitrate,
    get_file_duration,
    get_input_files,
    get_file_metadata,
)

# Audio filter builders
from app.services.filters_audio import (
    build_speed_filter,
    build_pitch_filter,
    build_noise_reduction_filter,
    build_compressor_filter,
)

# Video filter builders
from app.services.filters_video import (
    build_eq_filter,
    build_blur_filter,
    build_sharpen_filter,
    build_transform_filter,
)

# Filter chain aggregators
from app.services.filter_chain import (
    build_audio_filter_chain,
    build_video_filter_chain,
)

# FFmpeg execution
from app.services.ffmpeg_executor import (
    FFmpegError,
    run_ffmpeg_command,
    run_ffprobe_command,
)

# Processing functions
from app.services.processor import (
    process_audio,
    process_audio_with_effects,
    process_video_with_effects,
)

__all__ = [
    # Metadata
    "format_duration_ms",
    "format_file_size",
    "format_bitrate",
    "get_file_duration",
    "get_input_files",
    "get_file_metadata",
    # Audio filters
    "build_speed_filter",
    "build_pitch_filter",
    "build_noise_reduction_filter",
    "build_compressor_filter",
    # Video filters
    "build_eq_filter",
    "build_blur_filter",
    "build_sharpen_filter",
    "build_transform_filter",
    # Filter chains
    "build_audio_filter_chain",
    "build_video_filter_chain",
    # FFmpeg execution
    "FFmpegError",
    "run_ffmpeg_command",
    "run_ffprobe_command",
    # Processing
    "process_audio",
    "process_audio_with_effects",
    "process_video_with_effects",
]
