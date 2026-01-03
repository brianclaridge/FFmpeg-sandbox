"""Tests for filter chain aggregation."""

import pytest

from app.services.filter_chain import build_audio_filter_chain


class TestBuildAudioFilterChain:
    """Tests for build_audio_filter_chain function."""

    def test_no_effects_returns_none(self):
        """Test default parameters return None."""
        result = build_audio_filter_chain()
        assert result is None

    def test_single_volume_effect(self):
        """Test volume-only filter chain."""
        result = build_audio_filter_chain(volume=2.0)
        assert result == "volume=2.0"

    def test_filter_order_preserved(self):
        """Test filters are applied in correct order."""
        result = build_audio_filter_chain(
            volume=1.5,
            speed=2.0,
            pitch_semitones=4.0,
            noise_reduction=0.5,
        )
        # Verify all expected filters are present
        assert "volume=" in result
        assert "atempo=" in result
        assert "asetrate=" in result
        assert "afftdn=" in result

        # Check relative positions in the filter string
        volume_pos = result.index("volume=")
        asetrate_pos = result.index("asetrate=")
        afftdn_pos = result.index("afftdn=")

        # Volume should come before pitch (asetrate), which should come before noise reduction
        assert volume_pos < asetrate_pos
        assert asetrate_pos < afftdn_pos

    def test_speed_and_pitch_interaction(self):
        """Test combined speed and pitch effects."""
        result = build_audio_filter_chain(
            speed=2.0,
            pitch_semitones=12.0,
        )
        # Both should be present
        assert "atempo=" in result
        assert "asetrate=" in result
        assert "aresample=" in result

    def test_extreme_speed_4x(self):
        """Test 4x speed in filter chain."""
        result = build_audio_filter_chain(speed=4.0)
        # Should have chained atempo filters
        assert result.count("atempo") == 2

    def test_combined_speed_4x_and_pitch(self):
        """Test 4x speed combined with pitch shift."""
        result = build_audio_filter_chain(
            speed=4.0,
            pitch_semitones=8.0,
        )
        # Speed: 2 atempo filters for 4x
        # Pitch: asetrate + atempo + aresample
        # Total atempo count: 2 (speed) + 1 (pitch compensation) = 3
        assert result.count("atempo") == 3
        assert "asetrate=" in result

    def test_frequency_filters(self):
        """Test highpass and lowpass filters."""
        result = build_audio_filter_chain(highpass=200, lowpass=4000)
        assert "highpass=f=200" in result
        assert "lowpass=f=4000" in result

    def test_full_chain_all_effects(self):
        """Test chain with all effects active."""
        result = build_audio_filter_chain(
            volume=1.5,
            highpass=100,
            lowpass=6000,
            delays="20|40",
            decays="0.3|0.2",
            speed=1.5,
            pitch_semitones=4.0,
            noise_floor=-40.0,
            noise_reduction=0.7,
            comp_threshold=-18.0,
            comp_ratio=4.0,
            comp_attack=10.0,
            comp_release=150.0,
            comp_makeup=4.0,
        )
        # All filter types should be present
        assert "volume=" in result
        assert "highpass=" in result
        assert "lowpass=" in result
        assert "aecho=" in result
        assert "atempo=" in result
        assert "asetrate=" in result
        assert "afftdn=" in result
        assert "acompressor=" in result


class TestSpeedPitchInteraction:
    """Specific tests for speed + pitch interaction."""

    def test_double_speed_with_pitch_up(self):
        """Test 2x speed with positive pitch."""
        result = build_audio_filter_chain(speed=2.0, pitch_semitones=4.0)
        # Speed adds atempo=2.0
        # Pitch adds asetrate, atempo (compensation), aresample
        filters = result.split(",")
        assert any("atempo=2.0" in f or "atempo=2" in f for f in filters)

    def test_half_speed_with_pitch_down(self):
        """Test 0.5x speed with negative pitch."""
        result = build_audio_filter_chain(speed=0.5, pitch_semitones=-4.0)
        filters = result.split(",")
        assert any("atempo=0.5" in f for f in filters)

    def test_extreme_combo_4x_speed_octave_up(self):
        """Test extreme: 4x speed + octave up."""
        result = build_audio_filter_chain(speed=4.0, pitch_semitones=12.0)
        # This is a stress test for the filter chain
        assert result is not None
        # Should have multiple atempo filters
        # Speed: 2 atempo (2.0 * 2.0)
        # Pitch: 1 atempo (compensation for octave shift)
        assert result.count("atempo") >= 3

    def test_extreme_combo_quarter_speed_octave_down(self):
        """Test extreme: 0.25x speed + octave down."""
        result = build_audio_filter_chain(speed=0.25, pitch_semitones=-12.0)
        assert result is not None
        # Speed: 2 atempo (0.5 * 0.5)
        # Pitch: 1 atempo (compensation)
        assert result.count("atempo") >= 3


class TestNoiseReductionInChain:
    """Tests for noise reduction in filter chain."""

    def test_noise_reduction_light(self):
        """Test light noise reduction preset values."""
        result = build_audio_filter_chain(
            noise_floor=-30.0,
            noise_reduction=0.5,
        )
        assert "afftdn=nf=-30.0:nr=50" in result

    def test_noise_reduction_with_other_filters(self):
        """Test noise reduction combined with other filters."""
        result = build_audio_filter_chain(
            volume=1.5,
            noise_floor=-40.0,
            noise_reduction=0.7,
        )
        assert "volume=1.5" in result
        assert "afftdn=" in result
        # Volume should come before noise reduction
        volume_idx = result.index("volume")
        noise_idx = result.index("afftdn")
        assert volume_idx < noise_idx
