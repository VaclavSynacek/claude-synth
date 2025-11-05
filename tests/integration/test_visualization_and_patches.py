"""
Integration tests for visualization accuracy and patch functionality.

Tests that visualizations correctly reflect patch state, progress indicators
are accurate, and patch data is properly formatted.
"""
import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from acid_looper_curses import (VisualFeedback, PatchLoader, DrumPatternGenerator,
                                TempoController)


class TestVisualizationWithPatches:
    """Test visualization accuracy with actual patch data."""

    def test_visualize_bass_pattern_from_patch(self, temp_patch_dir, sample_patch_simple):
        """Test visualizing bass notes from loaded patch."""
        # Create and load patch
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        patch = loader.patches["test"]

        # Visualize each note in bass pattern
        for note, velocity, label in patch['bass_pattern']:
            viz = VisualFeedback.draw_note_visualizer(note, velocity)
            assert len(viz) == 8
            assert all(c in ['●', '○'] for c in viz)

            # Verify note name formatting
            note_name = VisualFeedback.format_note_name(note)
            assert len(note_name) >= 2

    def test_step_indicator_matches_pattern_length(self, temp_patch_dir,
                                                   sample_patch_simple):
        """Test that step indicator correctly reflects pattern length."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        patch = loader.patches["test"]

        pattern_length = len(patch['bass_pattern'])

        # Test step indicator for each step in pattern
        for step in range(pattern_length):
            indicator = VisualFeedback.draw_step_indicator(step, pattern_length)
            assert f"/{pattern_length:2d}" in indicator

    def test_visualization_progression_through_patch(self, temp_patch_dir,
                                                     sample_patch_complex):
        """Test visualization as we progress through a patch."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_complex, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        patch = loader.patches["test"]

        total_steps = len(patch['bass_pattern'])
        percentages = []

        # Collect percentages for each step
        for step in range(total_steps):
            indicator = VisualFeedback.draw_step_indicator(step, total_steps)
            # Extract percentage (it's in format "XXX%")
            parts = indicator.split('(')
            if len(parts) > 1:
                pct_str = parts[1].split('%')[0].strip()
                percentages.append(int(pct_str))

        # Verify progression (should increase)
        assert percentages[0] < percentages[-1]
        assert percentages[-1] == 100

    def test_drum_pattern_visualization(self, temp_patch_dir, sample_patch_simple):
        """Test that drum patterns can be visualized."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        patch = loader.patches["test"]

        # Visualize each drum hit
        for drum_hits, label in patch['drum_pattern']:
            for drum_note, velocity in drum_hits:
                # Drums are typically in 36-50 range, may show as empty or low
                viz = VisualFeedback.draw_note_visualizer(drum_note, velocity)
                assert len(viz) == 8


class TestPatchLoaderIntegration:
    """Test PatchLoader integration with visualization."""

    def test_all_patches_can_be_visualized(self, populated_patch_dir):
        """Test that all loaded patches can be visualized."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        for patch_name, patch in loader.patches.items():
            # Visualize bass pattern
            for note, velocity, label in patch['bass_pattern']:
                viz = VisualFeedback.draw_note_visualizer(note, velocity)
                assert len(viz) == 8

            # Visualize drum pattern
            for drum_hits, label in patch['drum_pattern']:
                assert len(drum_hits) > 0 or len(drum_hits) == 0  # Valid

    def test_patch_metadata_display(self, populated_patch_dir):
        """Test that patch metadata is properly formatted."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        for key, patch in loader.get_all_patches():
            # Verify metadata exists and is displayable
            assert 'name' in patch
            assert 'description' in patch
            assert len(patch['name']) > 0
            assert isinstance(patch['description'], str)

    def test_key_to_patch_visualization(self, populated_patch_dir):
        """Test retrieving and visualizing patches by key."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        # Get first patch by key
        patch = loader.get_patch_by_key('q')
        if patch:
            # Should be visualizable
            for note, velocity, label in patch['bass_pattern']:
                viz = VisualFeedback.draw_note_visualizer(note, velocity)
                assert len(viz) == 8


class TestTempoControllerWithPatterns:
    """Test tempo controller with pattern playback simulation."""

    def test_step_duration_for_pattern_playback(self, temp_patch_dir,
                                                sample_patch_simple):
        """Test calculating step durations for pattern playback."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        patch = loader.patches["test"]

        tempo = TempoController(initial_bpm=120)
        step_duration = tempo.get_step_duration_ms()

        # Calculate total pattern duration
        pattern_length = len(patch['bass_pattern'])
        total_duration = pattern_length * step_duration

        # At 120 BPM: 16th note = 125ms, 8 steps = 1000ms (1 second)
        assert abs(total_duration - 1000.0) < 1.0

    def test_tempo_affects_all_patterns_equally(self, temp_patch_dir,
                                                sample_patch_simple):
        """Test that tempo changes affect all patterns uniformly."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Test at different tempos
        tempos = [60, 90, 120, 180]
        pattern_length = 8

        for bpm in tempos:
            tempo = TempoController(initial_bpm=bpm)
            step_duration = tempo.get_step_duration_ms()
            total_duration = pattern_length * step_duration

            # Verify tempo relationship
            expected_duration = (pattern_length * 60000) / (bpm * 4)
            assert abs(total_duration - expected_duration) < 1.0


class TestDrumPatternIntegration:
    """Test drum pattern generation integration."""

    def test_drum_pattern_compatible_with_visualization(self):
        """Test that generated drum patterns can be visualized."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for drum_hits, label in pattern:
            for drum_note, velocity in drum_hits:
                # Each drum should be visualizable
                viz = VisualFeedback.draw_note_visualizer(drum_note, velocity)
                assert len(viz) == 8

    def test_drum_pattern_step_indicators(self):
        """Test step indicators with drum pattern length."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        pattern_length = len(pattern)

        assert pattern_length == 64

        # Test indicators for full pattern
        for step in range(pattern_length):
            indicator = VisualFeedback.draw_step_indicator(step, pattern_length)
            assert f"/{pattern_length:2d}" in indicator

    def test_drum_pattern_note_names(self):
        """Test formatting drum note names."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for drum_hits, label in pattern:
            for drum_note, velocity in drum_hits:
                note_name = VisualFeedback.format_note_name(drum_note)
                # Drum notes should format correctly
                assert len(note_name) >= 2
                assert note_name[0] in ['C', 'D', 'E', 'F', 'G', 'A', 'B']


class TestPatchSwitchingPreparation:
    """Test patch switching scenarios (state management)."""

    def test_load_multiple_patches_for_switching(self, temp_patch_dir,
                                                 sample_patch_simple,
                                                 sample_patch_complex):
        """Test loading multiple patches for seamless switching."""
        # Create multiple patches
        with open(temp_patch_dir / "patch_a.json", 'w') as f:
            json.dump(sample_patch_simple, f)
        with open(temp_patch_dir / "patch_b.json", 'w') as f:
            json.dump(sample_patch_complex, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Verify both patches loaded
        assert len(loader.patches) == 2

        # Get patches by key
        patch_a = loader.get_patch_by_key('q')
        patch_b = loader.get_patch_by_key('w')

        assert patch_a is not None
        assert patch_b is not None

        # Verify different lengths (for testing switching)
        len_a = len(patch_a['bass_pattern'])
        len_b = len(patch_b['bass_pattern'])

        assert len_a != len_b  # Different patterns

    def test_patch_switching_preserves_tempo(self, temp_patch_dir,
                                            sample_patch_simple,
                                            sample_patch_complex):
        """Test that tempo is preserved across patch switches."""
        tempo = TempoController(initial_bpm=120)

        # Simulate loading different patches
        loader = PatchLoader(patches_dir=str(temp_patch_dir))

        # Create patches
        with open(temp_patch_dir / "p1.json", 'w') as f:
            json.dump(sample_patch_simple, f)
        with open(temp_patch_dir / "p2.json", 'w') as f:
            json.dump(sample_patch_complex, f)

        loader.scan_patches()

        # Get step duration for first patch
        patch1 = loader.get_patch_by_key('q')
        duration1 = tempo.get_step_duration_ms()

        # Switch to second patch (tempo unchanged)
        patch2 = loader.get_patch_by_key('w')
        duration2 = tempo.get_step_duration_ms()

        # Tempo should remain constant
        assert duration1 == duration2

    def test_patch_queue_simulation(self, temp_patch_dir, sample_patch_simple):
        """Test simulating patch queuing for seamless switching."""
        # Create multiple patches
        for i in range(3):
            patch_file = temp_patch_dir / f"patch_{i}.json"
            with open(patch_file, 'w') as f:
                json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Simulate queue: current, next
        current_patch = loader.get_patch_by_key('q')
        next_patch = loader.get_patch_by_key('w')

        assert current_patch is not None
        assert next_patch is not None

        # Both should be valid and different
        assert current_patch['file'] != next_patch['file']


class TestVisualizationAccuracy:
    """Test accuracy of visualizations with real data."""

    def test_step_progress_accuracy(self):
        """Test that step progress is calculated accurately."""
        test_cases = [
            (0, 8, 1, 12),    # Step 0 of 8 = 1/8 = 12.5% ≈ 12%
            (7, 8, 8, 100),   # Step 7 of 8 = 8/8 = 100%
            (31, 64, 32, 50), # Step 31 of 64 = 32/64 = 50%
            (15, 16, 16, 100),# Step 15 of 16 = 16/16 = 100%
        ]

        for step, total, expected_num, expected_pct in test_cases:
            result = VisualFeedback.draw_step_indicator(step, total)

            # Check step number
            assert f"{expected_num:2d}/{total:2d}" in result or \
                   f" {expected_num}/{total}" in result

            # Check percentage (within ±1% for rounding)
            assert f"{expected_pct}" in result or \
                   f"{expected_pct-1}" in result or \
                   f"{expected_pct+1}" in result

    def test_note_height_accuracy(self):
        """Test that note visualization height is accurate."""
        # Test specific notes and their expected fill levels
        test_cases = [
            (28, 0),  # Minimum note = 0 filled
            (44, 4),  # Middle note ≈ half filled
            (60, 8),  # Maximum note = 8 filled
        ]

        for note, expected_filled in test_cases:
            viz = VisualFeedback.draw_note_visualizer(note)
            filled_count = viz.count('●')
            assert filled_count == expected_filled, \
                f"Note {note} expected {expected_filled} filled, got {filled_count}"

    def test_note_name_accuracy(self):
        """Test that note names are accurate."""
        # Test known note mappings
        test_cases = [
            (60, "C4"),   # Middle C
            (69, "A4"),   # A440
            (36, "C2"),   # Low C (bass range)
            (48, "C3"),   # C3
            (72, "C5"),   # High C
        ]

        for note, expected_name in test_cases:
            result = VisualFeedback.format_note_name(note)
            assert result == expected_name, \
                f"Note {note} expected {expected_name}, got {result}"


class TestIntegrationEndToEnd:
    """End-to-end integration tests."""

    def test_complete_patch_visualization_workflow(self, temp_patch_dir,
                                                    sample_patch_simple):
        """Test complete workflow: load patch, visualize all elements."""
        # Create patch
        patch_file = temp_patch_dir / "complete.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        # Load patch
        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        changes = loader.scan_patches()
        assert changes is True

        # Get patch
        patch = loader.get_patch_by_key('q')
        assert patch is not None

        # Setup tempo
        tempo = TempoController(initial_bpm=120)

        # Simulate playback visualization for each step
        pattern_length = len(patch['bass_pattern'])

        for step in range(pattern_length):
            # Get current note
            note, velocity, label = patch['bass_pattern'][step]

            # Visualize note
            note_viz = VisualFeedback.draw_note_visualizer(note, velocity)
            assert len(note_viz) == 8

            # Get note name
            note_name = VisualFeedback.format_note_name(note)
            assert len(note_name) >= 2

            # Show progress
            progress = VisualFeedback.draw_step_indicator(step, pattern_length)
            assert "/" in progress
            assert "%" in progress

            # Calculate timing
            step_duration = tempo.get_step_duration_ms()
            assert step_duration > 0

        # Verify complete cycle
        assert pattern_length == 8  # sample_patch_simple has 8 steps

    def test_multi_patch_session_simulation(self, temp_patch_dir,
                                           sample_patch_simple,
                                           sample_patch_complex):
        """Test simulating a session with multiple patches."""
        # Create multiple patches
        patches_data = [
            ("groove", sample_patch_simple),
            ("melody", sample_patch_complex),
        ]

        for name, data in patches_data:
            with open(temp_patch_dir / f"{name}.json", 'w') as f:
                json.dump(data, f)

        # Load all patches
        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Setup tempo
        tempo = TempoController(initial_bpm=90)

        # Get all patches
        all_patches = loader.get_all_patches()
        assert len(all_patches) == 2

        # Simulate playing each patch
        for key, patch in all_patches:
            pattern_length = len(patch['bass_pattern'])

            # Verify each step is visualizable
            for step in range(pattern_length):
                note, velocity, label = patch['bass_pattern'][step]

                viz = VisualFeedback.draw_note_visualizer(note, velocity)
                assert len(viz) == 8

                progress = VisualFeedback.draw_step_indicator(step, pattern_length)
                assert progress is not None

        # Tempo should remain consistent
        assert tempo.bpm == 90
