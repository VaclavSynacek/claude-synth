"""
Unit tests for TempoController class.

Tests tempo management, BPM validation, and step duration calculations.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from acid_looper_curses import TempoController


class TestTempoControllerInitialization:
    """Test TempoController initialization."""

    def test_default_initialization(self):
        """Test default tempo controller initialization."""
        controller = TempoController()
        assert controller.bpm == 90
        assert controller.min_bpm == 60
        assert controller.max_bpm == 180
        assert controller.step == 1

    def test_custom_initial_bpm(self):
        """Test initialization with custom BPM."""
        controller = TempoController(initial_bpm=120)
        assert controller.bpm == 120

    def test_minimum_bpm_initialization(self):
        """Test initialization at minimum BPM."""
        controller = TempoController(initial_bpm=60)
        assert controller.bpm == 60

    def test_maximum_bpm_initialization(self):
        """Test initialization at maximum BPM."""
        controller = TempoController(initial_bpm=180)
        assert controller.bpm == 180


class TestTempoControllerIncrease:
    """Test tempo increase functionality."""

    def test_increase_from_default(self):
        """Test increasing tempo from default value."""
        controller = TempoController(initial_bpm=90)
        controller.increase()
        assert controller.bpm == 91

    def test_increase_multiple_times(self):
        """Test increasing tempo multiple times."""
        controller = TempoController(initial_bpm=90)
        controller.increase()
        controller.increase()
        controller.increase()
        assert controller.bpm == 93

    def test_increase_to_maximum(self):
        """Test that tempo cannot exceed maximum."""
        controller = TempoController(initial_bpm=180)
        controller.increase()
        assert controller.bpm == 180  # Should stay at max

    def test_increase_near_maximum(self):
        """Test increasing when near maximum BPM."""
        controller = TempoController(initial_bpm=179)
        controller.increase()
        assert controller.bpm == 180
        controller.increase()
        assert controller.bpm == 180  # Should stay at max


class TestTempoControllerDecrease:
    """Test tempo decrease functionality."""

    def test_decrease_from_default(self):
        """Test decreasing tempo from default value."""
        controller = TempoController(initial_bpm=90)
        controller.decrease()
        assert controller.bpm == 89

    def test_decrease_multiple_times(self):
        """Test decreasing tempo multiple times."""
        controller = TempoController(initial_bpm=90)
        controller.decrease()
        controller.decrease()
        controller.decrease()
        assert controller.bpm == 87

    def test_decrease_to_minimum(self):
        """Test that tempo cannot go below minimum."""
        controller = TempoController(initial_bpm=60)
        controller.decrease()
        assert controller.bpm == 60  # Should stay at min

    def test_decrease_near_minimum(self):
        """Test decreasing when near minimum BPM."""
        controller = TempoController(initial_bpm=61)
        controller.decrease()
        assert controller.bpm == 60
        controller.decrease()
        assert controller.bpm == 60  # Should stay at min


class TestTempoControllerStepDuration:
    """Test step duration calculations."""

    def test_step_duration_at_90_bpm(self):
        """Test step duration calculation at 90 BPM."""
        controller = TempoController(initial_bpm=90)
        duration = controller.get_step_duration_ms()
        # At 90 BPM: 60000/90 = 666.67ms per beat
        # 16th note = beat/4 = 166.67ms
        expected = (60000 / 90) / 4
        assert abs(duration - expected) < 0.01

    def test_step_duration_at_120_bpm(self):
        """Test step duration calculation at 120 BPM."""
        controller = TempoController(initial_bpm=120)
        duration = controller.get_step_duration_ms()
        # At 120 BPM: 60000/120 = 500ms per beat
        # 16th note = beat/4 = 125ms
        expected = (60000 / 120) / 4
        assert abs(duration - expected) < 0.01

    def test_step_duration_at_60_bpm(self):
        """Test step duration at minimum BPM (slowest)."""
        controller = TempoController(initial_bpm=60)
        duration = controller.get_step_duration_ms()
        # At 60 BPM: 60000/60 = 1000ms per beat
        # 16th note = beat/4 = 250ms
        expected = (60000 / 60) / 4
        assert abs(duration - expected) < 0.01
        assert duration == 250.0

    def test_step_duration_at_180_bpm(self):
        """Test step duration at maximum BPM (fastest)."""
        controller = TempoController(initial_bpm=180)
        duration = controller.get_step_duration_ms()
        # At 180 BPM: 60000/180 = 333.33ms per beat
        # 16th note = beat/4 = 83.33ms
        expected = (60000 / 180) / 4
        assert abs(duration - expected) < 0.01

    def test_step_duration_precision(self):
        """Test that step duration maintains precision."""
        controller = TempoController(initial_bpm=137)
        duration = controller.get_step_duration_ms()
        expected = (60000 / 137) / 4
        assert abs(duration - expected) < 0.001

    def test_step_duration_after_changes(self):
        """Test that step duration updates after tempo changes."""
        controller = TempoController(initial_bpm=90)
        duration_before = controller.get_step_duration_ms()

        controller.increase()
        controller.increase()
        duration_after = controller.get_step_duration_ms()

        # Duration should decrease as tempo increases
        assert duration_after < duration_before


class TestTempoControllerBoundaries:
    """Test edge cases and boundary conditions."""

    def test_rapid_increases(self):
        """Test rapid tempo increases."""
        controller = TempoController(initial_bpm=60)
        for _ in range(150):  # More than max-min range
            controller.increase()
        assert controller.bpm == 180

    def test_rapid_decreases(self):
        """Test rapid tempo decreases."""
        controller = TempoController(initial_bpm=180)
        for _ in range(150):  # More than max-min range
            controller.decrease()
        assert controller.bpm == 60

    def test_alternating_changes(self):
        """Test alternating increases and decreases."""
        controller = TempoController(initial_bpm=100)
        controller.increase()
        controller.increase()
        controller.decrease()
        assert controller.bpm == 101

    def test_range_sweep(self):
        """Test sweeping through entire tempo range."""
        controller = TempoController(initial_bpm=60)

        # Sweep up
        for expected_bpm in range(60, 180):
            assert controller.bpm == expected_bpm
            controller.increase()
        assert controller.bpm == 180

        # Sweep down
        for expected_bpm in range(180, 60, -1):
            assert controller.bpm == expected_bpm
            controller.decrease()
        assert controller.bpm == 60


class TestTempoControllerMathematicalProperties:
    """Test mathematical properties and relationships."""

    def test_duration_inversely_proportional_to_bpm(self):
        """Test that duration is inversely proportional to BPM."""
        controller_slow = TempoController(initial_bpm=60)
        controller_fast = TempoController(initial_bpm=120)

        duration_slow = controller_slow.get_step_duration_ms()
        duration_fast = controller_fast.get_step_duration_ms()

        # At 120 BPM, duration should be half of 60 BPM
        assert abs(duration_slow / duration_fast - 2.0) < 0.01

    def test_duration_formula_consistency(self):
        """Test that duration formula is consistent across range."""
        for bpm in [60, 90, 120, 140, 180]:
            controller = TempoController(initial_bpm=bpm)
            duration = controller.get_step_duration_ms()
            expected = (60000 / bpm) / 4
            assert abs(duration - expected) < 0.001

    def test_16th_note_timing(self):
        """Test that 16 steps equal one beat."""
        controller = TempoController(initial_bpm=120)
        step_duration = controller.get_step_duration_ms()

        # 16 steps = 4 beats at 120 BPM
        # 4 beats = (4 * 60000 / 120) = 2000ms
        # 16 steps = 16 * step_duration should equal 2000ms
        sixteen_steps = 16 * step_duration
        four_beats = 4 * (60000 / 120)

        assert abs(sixteen_steps - four_beats) < 0.01
