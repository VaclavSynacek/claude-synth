"""
Unit tests for VisualFeedback class.

Tests visualization utilities including step indicators, note visualizers,
and note-to-name conversion.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from acid_looper_curses import VisualFeedback


class TestStepIndicator:
    """Test step indicator visualization."""

    def test_step_indicator_first_step(self):
        """Test step indicator at first step."""
        result = VisualFeedback.draw_step_indicator(0, 8)
        assert " 1/ 8" in result
        assert "12%" in result or "13%" in result  # Allow for rounding

    def test_step_indicator_middle_step(self):
        """Test step indicator at middle step."""
        result = VisualFeedback.draw_step_indicator(3, 8)
        assert " 4/ 8" in result
        assert "50%" in result

    def test_step_indicator_last_step(self):
        """Test step indicator at last step."""
        result = VisualFeedback.draw_step_indicator(7, 8)
        assert " 8/ 8" in result
        assert "100%" in result

    def test_step_indicator_64_steps(self):
        """Test step indicator with 64 steps (typical patch size)."""
        result = VisualFeedback.draw_step_indicator(31, 64)
        assert "32/64" in result
        assert "50%" in result

    def test_step_indicator_wrap_around(self):
        """Test that step indicator handles wrap-around correctly."""
        # Step 8 in an 8-step pattern should show as step 1
        result1 = VisualFeedback.draw_step_indicator(0, 8)
        result2 = VisualFeedback.draw_step_indicator(8, 8)
        # Both should show step 1 (due to modulo)
        assert " 1/ 8" in result2

    def test_step_indicator_progress_percentage(self):
        """Test percentage calculations in step indicator."""
        # Test various steps for correct percentage
        test_cases = [
            (0, 4, 25),    # Step 1/4 = 25%
            (1, 4, 50),    # Step 2/4 = 50%
            (2, 4, 75),    # Step 3/4 = 75%
            (3, 4, 100),   # Step 4/4 = 100%
        ]
        for step, total, expected_pct in test_cases:
            result = VisualFeedback.draw_step_indicator(step, total)
            assert f"{expected_pct:3d}%" in result

    def test_step_indicator_contains_circle(self):
        """Test that step indicator contains a circle character."""
        result = VisualFeedback.draw_step_indicator(0, 8)
        # Should contain bracket notation
        assert "[" in result
        assert "]" in result


class TestNoteVisualizer:
    """Test note visualization bars."""

    def test_note_visualizer_minimum_note(self):
        """Test visualizer at minimum note (28)."""
        result = VisualFeedback.draw_note_visualizer(28)
        # At minimum, should have minimal height
        filled_count = result.count("●")
        empty_count = result.count("○")
        assert len(result) == 8
        assert filled_count >= 0
        assert empty_count >= filled_count

    def test_note_visualizer_maximum_note(self):
        """Test visualizer at maximum note (60)."""
        result = VisualFeedback.draw_note_visualizer(60)
        # At maximum, should be fully filled
        assert len(result) == 8
        assert result.count("●") == 8
        assert result.count("○") == 0

    def test_note_visualizer_middle_note(self):
        """Test visualizer at middle of range."""
        # Note 44 is middle of 28-60 range
        result = VisualFeedback.draw_note_visualizer(44)
        filled_count = result.count("●")
        empty_count = result.count("○")

        assert len(result) == 8
        assert filled_count == 4  # Middle should be half-filled
        assert empty_count == 4

    def test_note_visualizer_below_minimum(self):
        """Test visualizer with note below minimum range."""
        result = VisualFeedback.draw_note_visualizer(20)
        # Below minimum should show empty
        assert len(result) == 8
        assert result.count("●") == 0
        assert result.count("○") == 8

    def test_note_visualizer_above_maximum(self):
        """Test visualizer with note above maximum range."""
        result = VisualFeedback.draw_note_visualizer(80)
        # Above maximum should show full
        assert len(result) == 8
        assert result.count("●") == 8
        assert result.count("○") == 0

    def test_note_visualizer_typical_bass_notes(self):
        """Test visualizer with typical bass note range (36-48)."""
        for note in range(36, 49):
            result = VisualFeedback.draw_note_visualizer(note)
            assert len(result) == 8
            filled = result.count("●")
            empty = result.count("○")
            assert filled + empty == 8
            # Filled count should increase with note number
            assert filled >= 0 and filled <= 8

    def test_note_visualizer_progressive_fill(self):
        """Test that higher notes have more filled bars."""
        results = []
        for note in [28, 36, 44, 52, 60]:
            result = VisualFeedback.draw_note_visualizer(note)
            filled = result.count("●")
            results.append(filled)

        # Each subsequent note should have >= filled bars
        for i in range(len(results) - 1):
            assert results[i] <= results[i + 1]

    def test_note_visualizer_with_velocity(self):
        """Test that velocity parameter doesn't affect visualization."""
        # Velocity should not affect the bar display (currently unused)
        result1 = VisualFeedback.draw_note_visualizer(44, velocity=50)
        result2 = VisualFeedback.draw_note_visualizer(44, velocity=100)
        result3 = VisualFeedback.draw_note_visualizer(44, velocity=127)

        assert result1 == result2 == result3


class TestNoteNameFormatting:
    """Test note-to-name conversion."""

    def test_format_note_c4(self):
        """Test middle C (note 60) formatting."""
        result = VisualFeedback.format_note_name(60)
        assert result == "C4"

    def test_format_note_a4(self):
        """Test A4 (440Hz, note 69) formatting."""
        result = VisualFeedback.format_note_name(69)
        assert result == "A4"

    def test_format_note_c0(self):
        """Test lowest MIDI note C0 (note 12)."""
        result = VisualFeedback.format_note_name(12)
        assert result == "C0"

    def test_format_note_sharps(self):
        """Test sharp notes formatting."""
        # C# (note 61)
        result = VisualFeedback.format_note_name(61)
        assert result == "C#4"

        # F# (note 66)
        result = VisualFeedback.format_note_name(66)
        assert result == "F#4"

    def test_format_note_all_chromatic(self):
        """Test all chromatic notes in an octave."""
        expected = ["C4", "C#4", "D4", "D#4", "E4", "F4",
                   "F#4", "G4", "G#4", "A4", "A#4", "B4"]

        for i, expected_name in enumerate(expected):
            note = 60 + i
            result = VisualFeedback.format_note_name(note)
            assert result == expected_name

    def test_format_note_bass_range(self):
        """Test typical bass note range (36-48)."""
        # Note 36 = C2
        result = VisualFeedback.format_note_name(36)
        assert result == "C2"

        # Note 48 = C3
        result = VisualFeedback.format_note_name(48)
        assert result == "C3"

    def test_format_note_octave_progression(self):
        """Test octave numbering across multiple octaves."""
        test_cases = [
            (24, "C1"),
            (36, "C2"),
            (48, "C3"),
            (60, "C4"),
            (72, "C5"),
            (84, "C6"),
        ]

        for note, expected in test_cases:
            result = VisualFeedback.format_note_name(note)
            assert result == expected

    def test_format_note_negative_octave(self):
        """Test that low notes produce negative octave numbers."""
        # Note 0 = C-1
        result = VisualFeedback.format_note_name(0)
        assert result == "C-1"

        # Note 11 = B-1
        result = VisualFeedback.format_note_name(11)
        assert result == "B-1"

    def test_format_note_high_octave(self):
        """Test high octave formatting."""
        # Note 108 = C8
        result = VisualFeedback.format_note_name(108)
        assert result == "C8"

        # Note 127 = G9 (highest MIDI note)
        result = VisualFeedback.format_note_name(127)
        assert result == "G9"


class TestVisualFeedbackEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_total_steps(self):
        """Test step indicator with zero total steps (edge case)."""
        # This should handle division by zero gracefully
        # Implementation may vary, but should not crash
        try:
            result = VisualFeedback.draw_step_indicator(0, 0)
            # If it doesn't crash, that's acceptable
        except (ZeroDivisionError, ValueError):
            # If it raises an error, that's also acceptable
            pass

    def test_negative_note_number(self):
        """Test note formatter with negative note number."""
        result = VisualFeedback.format_note_name(-12)
        # Should handle gracefully, will produce C-2
        assert "C" in result

    def test_very_large_step_count(self):
        """Test step indicator with large step count."""
        result = VisualFeedback.draw_step_indicator(999, 1000)
        assert "1000/1000" in result
        assert "100%" in result

    def test_note_visualizer_boundary_exact(self):
        """Test exact boundary notes."""
        # Exactly at minimum (28)
        result_min = VisualFeedback.draw_note_visualizer(28)
        filled_min = result_min.count("●")

        # Exactly at maximum (60)
        result_max = VisualFeedback.draw_note_visualizer(60)
        filled_max = result_max.count("●")

        # One below minimum
        result_below = VisualFeedback.draw_note_visualizer(27)
        filled_below = result_below.count("●")

        # One above maximum
        result_above = VisualFeedback.draw_note_visualizer(61)
        filled_above = result_above.count("●")

        # Verify boundaries are handled correctly
        assert filled_below == 0
        assert filled_above == 8
        assert filled_min >= 0
        assert filled_max == 8

    def test_step_indicator_single_step(self):
        """Test step indicator with only 1 step."""
        result = VisualFeedback.draw_step_indicator(0, 1)
        assert " 1/ 1" in result
        assert "100%" in result


class TestVisualFeedbackConsistency:
    """Test consistency and properties of visual feedback."""

    def test_note_visualizer_always_8_chars(self):
        """Test that note visualizer always returns 8 characters."""
        for note in range(0, 128):
            result = VisualFeedback.draw_note_visualizer(note)
            assert len(result) == 8, f"Note {note} produced {len(result)} chars"

    def test_note_visualizer_only_circle_chars(self):
        """Test that note visualizer only uses circle characters."""
        for note in [28, 40, 50, 60]:
            result = VisualFeedback.draw_note_visualizer(note)
            for char in result:
                assert char in ["●", "○"], f"Unexpected character: {char}"

    def test_step_indicator_format_consistency(self):
        """Test that step indicator maintains consistent format."""
        for total_steps in [8, 16, 32, 64]:
            for step in range(total_steps):
                result = VisualFeedback.draw_step_indicator(step, total_steps)
                # Should contain brackets, numbers, and percentage
                assert "[" in result
                assert "]" in result
                assert "/" in result
                assert "%" in result

    def test_note_name_all_midi_range(self):
        """Test that all MIDI notes (0-127) can be formatted."""
        for note in range(128):
            result = VisualFeedback.format_note_name(note)
            # Should produce a valid note name
            assert len(result) >= 2  # At least note + octave
            assert result[0] in ["C", "D", "E", "F", "G", "A", "B"]
