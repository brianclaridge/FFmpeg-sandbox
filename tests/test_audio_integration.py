"""Integration tests for audio filters with actual FFmpeg execution.

These tests validate that filter chains produce correct audio output,
not just correct filter strings. They use synthetic audio fixtures
and measure actual output properties (duration, file existence, etc.).
"""

from pathlib import Path

import pytest

from app.services.filters_audio import (
    build_noise_reduction_filter,
    build_pitch_filter,
    build_speed_filter,
)
from tests.conftest import get_audio_duration, run_ffmpeg_filter


# =============================================================================
# Speed Filter Integration Tests
# =============================================================================


class TestSpeedFilterIntegration:
    """Test speed filter with actual FFmpeg execution."""

    def test_4x_speed_quarters_duration(self, test_audio_file, output_dir):
        """10s input at 4x speed = 2.5s output."""
        output_path = output_dir / "speed_4x.wav"
        audio_filter = build_speed_filter(4.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration / 4.0

        assert abs(output_duration - expected_duration) < 0.1, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    def test_quarter_speed_quadruples_duration(self, test_audio_file, output_dir):
        """10s input at 0.25x speed = 40s output."""
        output_path = output_dir / "speed_025x.wav"
        audio_filter = build_speed_filter(0.25)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration * 4.0

        assert abs(output_duration - expected_duration) < 0.2, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    def test_2x_speed_halves_duration(self, test_audio_file, output_dir):
        """10s input at 2x speed = 5s output."""
        output_path = output_dir / "speed_2x.wav"
        audio_filter = build_speed_filter(2.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration / 2.0

        assert abs(output_duration - expected_duration) < 0.1, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    def test_half_speed_doubles_duration(self, test_audio_file, output_dir):
        """10s input at 0.5x speed = 20s output."""
        output_path = output_dir / "speed_05x.wav"
        audio_filter = build_speed_filter(0.5)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration * 2.0

        assert abs(output_duration - expected_duration) < 0.1, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    @pytest.mark.parametrize(
        "speed,expected_ratio",
        [
            (0.25, 4.0),
            (0.5, 2.0),
            (1.5, 1 / 1.5),
            (2.0, 0.5),
            (3.0, 1 / 3.0),
            (4.0, 0.25),
        ],
    )
    def test_speed_duration_ratios(
        self, test_audio_file, output_dir, speed, expected_ratio
    ):
        """Parametrized test for various speed values."""
        output_path = output_dir / f"speed_{speed}x.wav"
        audio_filter = build_speed_filter(speed)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration * expected_ratio

        # Wider tolerance for extreme speeds
        tolerance = 0.2 if speed <= 0.5 or speed >= 3.0 else 0.1

        assert abs(output_duration - expected_duration) < tolerance, (
            f"Speed {speed}x: expected ~{expected_duration:.2f}s, "
            f"got {output_duration:.2f}s"
        )


# =============================================================================
# Pitch Filter Integration Tests
# =============================================================================


class TestPitchFilterIntegration:
    """Test pitch filter with actual FFmpeg execution."""

    def test_octave_up_executes(self, test_audio_file, output_dir):
        """Pitch +12 semitones runs without error."""
        output_path = output_dir / "pitch_up12.wav"
        audio_filter = build_pitch_filter(12.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_octave_down_executes(self, test_audio_file, output_dir):
        """Pitch -12 semitones runs without error."""
        output_path = output_dir / "pitch_down12.wav"
        audio_filter = build_pitch_filter(-12.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_pitch_up_preserves_duration(self, test_audio_file, output_dir):
        """Pitch shift up with tempo compensation maintains duration."""
        output_path = output_dir / "pitch_up_duration.wav"
        audio_filter = build_pitch_filter(4.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)

        # Duration should be preserved (within tolerance)
        assert abs(output_duration - input_duration) < 0.2, (
            f"Duration changed: {input_duration:.2f}s -> {output_duration:.2f}s"
        )

    def test_pitch_down_preserves_duration(self, test_audio_file, output_dir):
        """Pitch shift down with tempo compensation maintains duration."""
        output_path = output_dir / "pitch_down_duration.wav"
        audio_filter = build_pitch_filter(-4.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.2, (
            f"Duration changed: {input_duration:.2f}s -> {output_duration:.2f}s"
        )

    def test_octave_up_preserves_duration(self, test_audio_file, output_dir):
        """Pitch +12 semitones preserves duration."""
        output_path = output_dir / "pitch_12_duration.wav"
        audio_filter = build_pitch_filter(12.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.3, (
            f"Duration changed: {input_duration:.2f}s -> {output_duration:.2f}s"
        )

    def test_octave_down_preserves_duration(self, test_audio_file, output_dir):
        """Pitch -12 semitones preserves duration."""
        output_path = output_dir / "pitch_minus12_duration.wav"
        audio_filter = build_pitch_filter(-12.0)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.3, (
            f"Duration changed: {input_duration:.2f}s -> {output_duration:.2f}s"
        )

    @pytest.mark.parametrize("semitones", [-12, -8, -4, 4, 8, 12])
    def test_pitch_preset_values_execute(
        self, test_audio_file, output_dir, semitones
    ):
        """Test all preset pitch values execute successfully."""
        output_path = output_dir / f"pitch_{semitones}.wav"
        audio_filter = build_pitch_filter(float(semitones))

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()


# =============================================================================
# Speed + Pitch Interaction Tests
# =============================================================================


class TestSpeedPitchInteraction:
    """Test combined speed and pitch filters."""

    def test_4x_speed_with_octave_up(self, test_audio_file, output_dir):
        """Extreme combo: 4x speed + 12 semitones."""
        output_path = output_dir / "combo_4x_octave_up.wav"

        speed_filter = build_speed_filter(4.0)
        pitch_filter = build_pitch_filter(12.0)
        combined_filter = f"{speed_filter},{pitch_filter}"

        assert run_ffmpeg_filter(test_audio_file, output_path, combined_filter)
        assert output_path.exists()

        # Duration should be ~1/4 of input
        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration / 4.0

        assert abs(output_duration - expected_duration) < 0.2, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    def test_quarter_speed_with_octave_down(self, test_audio_file, output_dir):
        """Extreme combo: 0.25x speed - 12 semitones."""
        output_path = output_dir / "combo_025x_octave_down.wav"

        speed_filter = build_speed_filter(0.25)
        pitch_filter = build_pitch_filter(-12.0)
        combined_filter = f"{speed_filter},{pitch_filter}"

        assert run_ffmpeg_filter(test_audio_file, output_path, combined_filter)
        assert output_path.exists()

        # Duration should be ~4x of input
        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration * 4.0

        assert abs(output_duration - expected_duration) < 0.5, (
            f"Expected ~{expected_duration:.2f}s, got {output_duration:.2f}s"
        )

    def test_2x_speed_with_pitch_up(self, test_audio_file, output_dir):
        """2x speed with +4 semitones."""
        output_path = output_dir / "combo_2x_pitch4.wav"

        speed_filter = build_speed_filter(2.0)
        pitch_filter = build_pitch_filter(4.0)
        combined_filter = f"{speed_filter},{pitch_filter}"

        assert run_ffmpeg_filter(test_audio_file, output_path, combined_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration / 2.0

        assert abs(output_duration - expected_duration) < 0.2

    def test_half_speed_with_pitch_down(self, test_audio_file, output_dir):
        """0.5x speed with -4 semitones."""
        output_path = output_dir / "combo_05x_pitchminus4.wav"

        speed_filter = build_speed_filter(0.5)
        pitch_filter = build_pitch_filter(-4.0)
        combined_filter = f"{speed_filter},{pitch_filter}"

        assert run_ffmpeg_filter(test_audio_file, output_path, combined_filter)

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)
        expected_duration = input_duration * 2.0

        assert abs(output_duration - expected_duration) < 0.2

    def test_speed_pitch_filter_order(self, test_audio_file, output_dir):
        """Verify both speed and pitch filters apply correctly in chain."""
        # Speed first, then pitch
        output_sp = output_dir / "order_speed_then_pitch.wav"
        speed_filter = build_speed_filter(2.0)
        pitch_filter = build_pitch_filter(4.0)

        assert run_ffmpeg_filter(
            test_audio_file, output_sp, f"{speed_filter},{pitch_filter}"
        )

        # Pitch first, then speed
        output_ps = output_dir / "order_pitch_then_speed.wav"
        assert run_ffmpeg_filter(
            test_audio_file, output_ps, f"{pitch_filter},{speed_filter}"
        )

        # Both should produce valid output
        assert output_sp.exists()
        assert output_ps.exists()

        # Both should have similar duration (speed is the determining factor)
        duration_sp = get_audio_duration(output_sp)
        duration_ps = get_audio_duration(output_ps)

        input_duration = get_audio_duration(test_audio_file)
        expected = input_duration / 2.0

        assert abs(duration_sp - expected) < 0.2
        assert abs(duration_ps - expected) < 0.2


# =============================================================================
# Noise Reduction Integration Tests
# =============================================================================


class TestNoiseReductionIntegration:
    """Test noise reduction filter with actual FFmpeg execution."""

    def test_noise_reduction_executes(self, test_audio_with_noise, output_dir):
        """afftdn filter runs without error."""
        output_path = output_dir / "nr_basic.wav"
        audio_filter = build_noise_reduction_filter(-50.0, 0.5)

        assert run_ffmpeg_filter(test_audio_with_noise, output_path, audio_filter)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_light_noise_reduction(self, test_audio_with_noise, output_dir):
        """0.5 reduction level processes correctly."""
        output_path = output_dir / "nr_light.wav"
        audio_filter = build_noise_reduction_filter(-50.0, 0.5)

        assert run_ffmpeg_filter(test_audio_with_noise, output_path, audio_filter)
        assert output_path.exists()

        # Duration should be preserved
        input_duration = get_audio_duration(test_audio_with_noise)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.1

    def test_heavy_noise_reduction(self, test_audio_with_noise, output_dir):
        """0.9 reduction level processes correctly."""
        output_path = output_dir / "nr_heavy.wav"
        audio_filter = build_noise_reduction_filter(-50.0, 0.9)

        assert run_ffmpeg_filter(test_audio_with_noise, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_with_noise)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.1

    def test_maximum_noise_reduction(self, test_audio_with_noise, output_dir):
        """0.97 (97%) reduction level processes correctly (ffmpeg max is 97)."""
        output_path = output_dir / "nr_max.wav"
        # Note: ffmpeg afftdn nr parameter max is 97, so use 0.97 not 1.0
        audio_filter = build_noise_reduction_filter(-50.0, 0.97)

        assert run_ffmpeg_filter(test_audio_with_noise, output_path, audio_filter)
        assert output_path.exists()

    @pytest.mark.parametrize("noise_floor", [-30, -50, -70])
    def test_noise_floor_variations(
        self, test_audio_with_noise, output_dir, noise_floor
    ):
        """Test different noise floor dB levels."""
        output_path = output_dir / f"nr_floor_{abs(noise_floor)}.wav"
        audio_filter = build_noise_reduction_filter(float(noise_floor), 0.7)

        assert run_ffmpeg_filter(test_audio_with_noise, output_path, audio_filter)
        assert output_path.exists()

    def test_noise_reduction_with_clean_audio(self, test_audio_file, output_dir):
        """Noise reduction on clean audio should not fail."""
        output_path = output_dir / "nr_clean_input.wav"
        audio_filter = build_noise_reduction_filter(-50.0, 0.5)

        assert run_ffmpeg_filter(test_audio_file, output_path, audio_filter)
        assert output_path.exists()

        input_duration = get_audio_duration(test_audio_file)
        output_duration = get_audio_duration(output_path)

        assert abs(output_duration - input_duration) < 0.1
