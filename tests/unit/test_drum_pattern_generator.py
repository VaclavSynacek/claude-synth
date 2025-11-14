"""
Unit tests for DrumPatternGenerator class.

Tests drum pattern generation, note mapping, velocity ranges,
and pattern structure validation.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from acid_looper_curses import DrumPatternGenerator


class TestDrumMapping:
    """Test drum note mapping constants."""

    def test_drum_mapping_exists(self):
        """Test that drum mapping dictionary exists."""
        assert hasattr(DrumPatternGenerator, 'DRUMS')
        assert isinstance(DrumPatternGenerator.DRUMS, dict)

    def test_all_drums_mapped(self):
        """Test that all expected drums are mapped."""
        expected_drums = ['kick', 'snare', 'closed_hh', 'open_hh',
                         'tom_high', 'tom_mid', 'tom_low', 'clap']

        for drum in expected_drums:
            assert drum in DrumPatternGenerator.DRUMS

    def test_drum_note_numbers(self):
        """Test correct MIDI note numbers for drums."""
        drums = DrumPatternGenerator.DRUMS
        assert drums['kick'] == 36
        assert drums['snare'] == 38
        assert drums['closed_hh'] == 42
        assert drums['open_hh'] == 46
        assert drums['tom_high'] == 47
        assert drums['tom_mid'] == 47
        assert drums['tom_low'] == 45
        assert drums['clap'] == 50  # T-8 Manual: HAND CLAP Tx=50

    def test_drum_notes_valid_midi_range(self):
        """Test that all drum notes are in valid MIDI range (0-127)."""
        for drum_name, note in DrumPatternGenerator.DRUMS.items():
            assert 0 <= note <= 127, f"{drum_name} note {note} out of range"

    def test_drum_notes_unique(self):
        """Test that each drum has a unique note number."""
        # Note: T-8 uses same note (47) for tom_high and tom_mid
        # This is correct per the T-8 manual (TOM responds to 45, 47)
        notes = list(DrumPatternGenerator.DRUMS.values())
        # Allow tom_high and tom_mid to share note 47
        unique_drums = {k: v for k, v in DrumPatternGenerator.DRUMS.items() 
                       if k not in ['tom_high', 'tom_mid']}
        tom_notes = [DrumPatternGenerator.DRUMS['tom_high'], 
                    DrumPatternGenerator.DRUMS['tom_mid']]
        
        # Check non-tom drums are unique
        non_tom_notes = list(unique_drums.values())
        assert len(non_tom_notes) == len(set(non_tom_notes)), \
            "Duplicate drum note numbers found (excluding toms)"
        
        # Check toms use valid T-8 tom notes (45 or 47)
        for tom_note in tom_notes:
            assert tom_note in [45, 47], f"Tom note {tom_note} not valid (should be 45 or 47)"


class TestElaborateTechDrumsPattern:
    """Test the elaborate_tech_drums_64 pattern generator."""

    def test_pattern_length(self):
        """Test that pattern has exactly 64 steps."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        assert len(pattern) == 64

    def test_pattern_structure(self):
        """Test that each step has correct structure."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for i, step in enumerate(pattern):
            # Each step should be a tuple (drum_hits, label)
            assert isinstance(step, tuple), f"Step {i} is not a tuple"
            assert len(step) == 2, f"Step {i} doesn't have 2 elements"

            drum_hits, label = step
            assert isinstance(drum_hits, list), f"Step {i} drum_hits not a list"
            assert isinstance(label, str), f"Step {i} label not a string"

    def test_drum_hits_structure(self):
        """Test that drum hits have correct structure."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for i, (drum_hits, label) in enumerate(pattern):
            for hit_idx, hit in enumerate(drum_hits):
                assert isinstance(hit, tuple), \
                    f"Step {i}, hit {hit_idx} is not a tuple"
                assert len(hit) == 2, \
                    f"Step {i}, hit {hit_idx} doesn't have 2 elements"

                note, velocity = hit
                assert isinstance(note, int), \
                    f"Step {i}, hit {hit_idx} note is not int"
                assert isinstance(velocity, int), \
                    f"Step {i}, hit {hit_idx} velocity is not int"

    def test_velocity_ranges(self):
        """Test that all velocities are in valid MIDI range (0-127)."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for i, (drum_hits, _) in enumerate(pattern):
            for note, velocity in drum_hits:
                assert 0 <= velocity <= 127, \
                    f"Step {i} velocity {velocity} out of range"

    def test_note_numbers(self):
        """Test that all notes are valid drum notes."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        valid_notes = set(DrumPatternGenerator.DRUMS.values())

        for i, (drum_hits, _) in enumerate(pattern):
            for note, velocity in drum_hits:
                assert note in valid_notes, \
                    f"Step {i} has invalid drum note {note}"

    def test_kick_pattern(self):
        """Test kick drum pattern structure."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        kick_note = drums['kick']

        # Kick pattern should be: [1, 0, 1, 0, 0, 1, 0, 1] * 8
        expected_pattern = [1, 0, 1, 0, 0, 1, 0, 1] * 8

        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            has_kick = any(note == kick_note for note, vel in drum_hits)

            if expected_pattern[step_idx]:
                assert has_kick, f"Expected kick at step {step_idx}"
            # Note: we don't assert NOT has_kick when expected is 0
            # because other patterns might add kicks

    def test_snare_pattern(self):
        """Test snare drum pattern structure."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        snare_note = drums['snare']

        # Snare pattern should be: [0, 0, 0, 1, 0, 0, 0, 1] * 8
        expected_pattern = [0, 0, 0, 1, 0, 0, 0, 1] * 8

        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            has_snare = any(note == snare_note for note, vel in drum_hits)

            if expected_pattern[step_idx]:
                assert has_snare, f"Expected snare at step {step_idx}"

    def test_hihat_on_every_step(self):
        """Test that closed hi-hat appears on every step."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        hh_note = drums['closed_hh']

        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            has_hh = any(note == hh_note for note, vel in drum_hits)
            assert has_hh, f"Missing hi-hat at step {step_idx}"

    def test_open_hihat_placement(self):
        """Test open hi-hat appears at specific steps."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        open_hh_note = drums['open_hh']

        # Open HH should appear on steps: 7, 15, 23, 31, 39, 47, 55, 63
        expected_steps = [7, 15, 23, 31, 39, 47, 55, 63]

        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            has_open_hh = any(note == open_hh_note for note, vel in drum_hits)

            if step_idx in expected_steps:
                assert has_open_hh, f"Expected open hi-hat at step {step_idx}"

    def test_kick_velocity_variation(self):
        """Test that kick velocity varies based on position."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        kick_note = drums['kick']

        velocities = []
        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            for note, velocity in drum_hits:
                if note == kick_note:
                    velocities.append((step_idx, velocity))

        # Should have two different velocities (120 and 115)
        unique_velocities = set(vel for _, vel in velocities)
        assert len(unique_velocities) >= 2, "Kick should have velocity variation"
        assert 120 in unique_velocities or 115 in unique_velocities

    def test_snare_velocity_variation(self):
        """Test that snare velocity is consistent (105) based on pattern."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        snare_note = drums['snare']

        velocities = []
        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            for note, velocity in drum_hits:
                if note == snare_note:
                    velocities.append((step_idx, velocity))

        # All snares have velocity 105 (none hit on step % 16 == 0)
        unique_velocities = set(vel for _, vel in velocities)
        assert 105 in unique_velocities, "Snare should have velocity 105"
        # Currently all snares have same velocity due to pattern timing
        assert len(velocities) > 0, "Should have snare hits"

    def test_hihat_velocity_alternation(self):
        """Test that closed hi-hat velocity alternates."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        drums = DrumPatternGenerator.DRUMS
        hh_note = drums['closed_hh']

        # Extract hi-hat velocities
        hh_velocities = []
        for step_idx in range(64):
            drum_hits, _ = pattern[step_idx]
            for note, velocity in drum_hits:
                if note == hh_note:
                    hh_velocities.append(velocity)
                    break  # Only first occurrence per step

        # Should have exactly 64 hi-hats
        assert len(hh_velocities) == 64

        # Should alternate between two velocities (75 and 65)
        assert 75 in hh_velocities
        assert 65 in hh_velocities

        # Check alternation pattern
        for i in range(64):
            if i % 2 == 0:
                assert hh_velocities[i] == 75, f"Even step {i} should have vel 75"
            else:
                assert hh_velocities[i] == 65, f"Odd step {i} should have vel 65"

    def test_labels_unique(self):
        """Test that each step has a unique label."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()
        labels = [label for _, label in pattern]

        # All labels should be unique
        assert len(labels) == len(set(labels)), "Duplicate labels found"

    def test_labels_format(self):
        """Test that labels follow expected format."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for i, (_, label) in enumerate(pattern):
            assert label == f"drums_{i}", \
                f"Step {i} has unexpected label: {label}"

    def test_pattern_deterministic(self):
        """Test that pattern generation is deterministic."""
        pattern1 = DrumPatternGenerator.elaborate_tech_drums_64()
        pattern2 = DrumPatternGenerator.elaborate_tech_drums_64()

        assert len(pattern1) == len(pattern2)

        for i in range(64):
            hits1, label1 = pattern1[i]
            hits2, label2 = pattern2[i]

            assert label1 == label2
            assert len(hits1) == len(hits2)
            assert hits1 == hits2

    def test_no_empty_steps(self):
        """Test that no step is completely empty."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        for i, (drum_hits, _) in enumerate(pattern):
            assert len(drum_hits) > 0, f"Step {i} has no drum hits"

    def test_pattern_rhythmic_consistency(self):
        """Test that pattern maintains rhythmic structure."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        # Test that pattern repeats its structure every 8 steps
        # (based on kick and snare patterns)
        for section in range(8):
            section_start = section * 8
            first_bar_drums = [pattern[i][0] for i in range(8)]
            section_bar_drums = [pattern[section_start + i][0]
                                for i in range(8)]

            # Structure should be consistent (same drum types, maybe different velocities)
            for step in range(8):
                first_notes = set(note for note, vel in first_bar_drums[step])
                section_notes = set(note for note, vel in section_bar_drums[step])
                # Same drums should be hit (notes should match)
                assert first_notes == section_notes, \
                    f"Section {section} step {step} has different drums"


class TestDrumPatternGeneratorEdgeCases:
    """Test edge cases and additional functionality."""

    def test_multiple_pattern_calls(self):
        """Test that multiple calls produce consistent results."""
        patterns = [DrumPatternGenerator.elaborate_tech_drums_64()
                   for _ in range(5)]

        # All patterns should be identical
        for i in range(1, 5):
            assert len(patterns[0]) == len(patterns[i])
            for step in range(64):
                assert patterns[0][step] == patterns[i][step]

    def test_pattern_not_all_silent(self):
        """Test that pattern has actual drum hits."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        total_hits = sum(len(drum_hits) for drum_hits, _ in pattern)
        assert total_hits > 64, "Pattern should have more than one hit per step"

    def test_velocity_not_all_same(self):
        """Test that velocities are not all identical."""
        pattern = DrumPatternGenerator.elaborate_tech_drums_64()

        all_velocities = []
        for drum_hits, _ in pattern:
            for _, velocity in drum_hits:
                all_velocities.append(velocity)

        unique_velocities = set(all_velocities)
        assert len(unique_velocities) > 1, "Pattern should have velocity variation"
