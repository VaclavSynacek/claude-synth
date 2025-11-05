"""
Unit tests for PatchLoader class.

Tests JSON loading, patch validation, hot-reload functionality,
and keyboard mapping.
"""
import pytest
import json
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from acid_looper_curses import PatchLoader, PATCH_KEYS


class TestPatchLoaderInitialization:
    """Test PatchLoader initialization."""

    def test_default_initialization(self, tmp_path):
        """Test default patch loader initialization."""
        loader = PatchLoader(patches_dir=str(tmp_path))
        assert loader.patches_dir == tmp_path
        assert loader.patches == {}
        assert loader.patch_keys_map == {}
        assert loader.last_scan_time == 0

    def test_initialization_with_nonexistent_dir(self):
        """Test initialization with non-existent directory."""
        loader = PatchLoader(patches_dir="/nonexistent/path")
        assert loader.patches == {}


class TestPatchScanning:
    """Test patch directory scanning."""

    def test_scan_empty_directory(self, temp_patch_dir):
        """Test scanning empty directory."""
        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        changes = loader.scan_patches()

        assert changes is False  # No changes in empty dir
        assert len(loader.patches) == 0

    def test_scan_with_simple_patch(self, temp_patch_dir, sample_patch_simple):
        """Test scanning directory with one simple patch."""
        # Create patch file
        patch_file = temp_patch_dir / "simple.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        changes = loader.scan_patches()

        assert changes is True  # New patch detected
        assert len(loader.patches) == 1
        assert "simple" in loader.patches

    def test_scan_multiple_patches(self, temp_patch_dir, sample_patch_simple,
                                   sample_patch_complex):
        """Test scanning directory with multiple patches."""
        # Create multiple patch files
        with open(temp_patch_dir / "patch1.json", 'w') as f:
            json.dump(sample_patch_simple, f)
        with open(temp_patch_dir / "patch2.json", 'w') as f:
            json.dump(sample_patch_complex, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        assert len(loader.patches) == 2
        assert "patch1" in loader.patches
        assert "patch2" in loader.patches

    def test_scan_ignores_non_json_files(self, temp_patch_dir, sample_patch_simple):
        """Test that scanner ignores non-JSON files."""
        # Create JSON file
        with open(temp_patch_dir / "valid.json", 'w') as f:
            json.dump(sample_patch_simple, f)

        # Create non-JSON files
        (temp_patch_dir / "readme.txt").write_text("Not a patch")
        (temp_patch_dir / "data.xml").write_text("<xml/>")

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        assert len(loader.patches) == 1
        assert "valid" in loader.patches

    def test_scan_nonexistent_directory(self):
        """Test scanning non-existent directory."""
        loader = PatchLoader(patches_dir="/nonexistent/dir")
        changes = loader.scan_patches()

        assert changes is False
        assert len(loader.patches) == 0


class TestPatchParsing:
    """Test patch JSON parsing."""

    def test_parse_bass_pattern(self, temp_patch_dir, sample_patch_simple):
        """Test parsing bass pattern from JSON."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["test"]
        bass = patch['bass_pattern']

        # Check structure
        assert len(bass) == 8
        for note, velocity, label in bass:
            assert isinstance(note, int)
            assert isinstance(velocity, int)
            assert isinstance(label, str)

    def test_parse_drum_pattern(self, temp_patch_dir, sample_patch_simple):
        """Test parsing drum pattern from JSON."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["test"]
        drums = patch['drum_pattern']

        # Check structure
        assert len(drums) == 8
        for drum_hits, label in drums:
            assert isinstance(drum_hits, list)
            assert isinstance(label, str)
            for note, velocity in drum_hits:
                assert isinstance(note, int)
                assert isinstance(velocity, int)

    def test_parse_patch_metadata(self, temp_patch_dir, sample_patch_simple):
        """Test parsing patch metadata (name, description)."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["test"]
        assert patch['name'] == "Test Simple"
        assert patch['description'] == "Simple test patch with 8 steps"
        assert patch['file'] == "test"

    def test_parse_patch_without_description(self, temp_patch_dir):
        """Test parsing patch without description field."""
        patch_data = {
            "name": "No Description",
            "root_note": 36,
            "bass_pattern": [[36, 100, "C"]],
            "drum_pattern": {"steps": [[[36, 100]]]}
        }

        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(patch_data, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["test"]
        assert patch['description'] == ""  # Default empty string

    def test_parse_empty_patterns(self, temp_patch_dir, sample_patch_empty):
        """Test parsing patch with empty patterns."""
        patch_file = temp_patch_dir / "empty.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_empty, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["empty"]
        assert len(patch['bass_pattern']) == 0
        assert len(patch['drum_pattern']) == 0


class TestPatchValidation:
    """Test patch validation and error handling."""

    def test_invalid_json_skipped(self, temp_patch_dir):
        """Test that invalid JSON files are silently skipped."""
        # Create invalid JSON file
        patch_file = temp_patch_dir / "bad.json"
        patch_file.write_text('{"invalid": "json" missing brace')

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        assert "bad" not in loader.patches

    def test_missing_fields_skipped(self, temp_patch_dir):
        """Test that patches with missing required fields are skipped."""
        # Create patch without required fields
        patch_data = {"name": "Incomplete"}

        patch_file = temp_patch_dir / "incomplete.json"
        with open(patch_file, 'w') as f:
            json.dump(patch_data, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Should be skipped due to missing fields
        assert "incomplete" not in loader.patches

    def test_mixed_valid_invalid_patches(self, temp_patch_dir,
                                        sample_patch_simple):
        """Test scanning directory with mix of valid and invalid patches."""
        # Create valid patch
        with open(temp_patch_dir / "valid.json", 'w') as f:
            json.dump(sample_patch_simple, f)

        # Create invalid patch
        (temp_patch_dir / "invalid.json").write_text('bad json')

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Only valid patch should be loaded
        assert len(loader.patches) == 1
        assert "valid" in loader.patches


class TestHotReload:
    """Test hot-reload functionality."""

    def test_detect_new_patch(self, temp_patch_dir, sample_patch_simple):
        """Test detection of newly added patch."""
        loader = PatchLoader(patches_dir=str(temp_patch_dir))

        # Initial scan (empty)
        changes1 = loader.scan_patches()
        assert changes1 is False

        # Add new patch
        time.sleep(0.01)  # Ensure different timestamp
        patch_file = temp_patch_dir / "new.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        # Second scan should detect changes
        changes2 = loader.scan_patches()
        assert changes2 is True
        assert "new" in loader.patches

    def test_detect_modified_patch(self, temp_patch_dir, sample_patch_simple,
                                   sample_patch_complex):
        """Test detection of modified patch."""
        # Create initial patch
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Modify patch
        time.sleep(0.01)  # Ensure different timestamp
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_complex, f)

        # Should detect modification
        changes = loader.scan_patches()
        assert changes is True
        # Check that new content is loaded
        patch = loader.patches["test"]
        assert len(patch['bass_pattern']) == 64  # Complex patch has 64 steps

    def test_detect_deleted_patch(self, temp_patch_dir, sample_patch_simple):
        """Test detection of deleted patch."""
        # Create patch
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()
        assert "test" in loader.patches

        # Delete patch
        patch_file.unlink()

        # Should detect deletion
        changes = loader.scan_patches()
        assert changes is True
        assert "test" not in loader.patches

    def test_no_changes_detected(self, temp_patch_dir, sample_patch_simple):
        """Test that no changes are detected when files unchanged."""
        # Create patch
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Scan again without changes
        changes = loader.scan_patches()
        assert changes is False

    def test_last_scan_time_updated(self, temp_patch_dir, sample_patch_simple):
        """Test that last_scan_time is updated after scan."""
        loader = PatchLoader(patches_dir=str(temp_patch_dir))

        initial_time = loader.last_scan_time
        assert initial_time == 0

        loader.scan_patches()
        assert loader.last_scan_time > initial_time


class TestKeyboardMapping:
    """Test keyboard key to patch mapping."""

    def test_key_mapping_single_patch(self, temp_patch_dir, sample_patch_simple):
        """Test key mapping with single patch."""
        patch_file = temp_patch_dir / "test.json"
        with open(patch_file, 'w') as f:
            json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # First patch should be mapped to 'q'
        assert 'q' in loader.patch_keys_map
        assert loader.patch_keys_map['q'] == "test"

    def test_key_mapping_multiple_patches(self, temp_patch_dir,
                                          sample_patch_simple, sample_patch_complex):
        """Test key mapping with multiple patches."""
        # Create patches (alphabetically: aaa, bbb, ccc)
        for i, (name, data) in enumerate([
            ("aaa", sample_patch_simple),
            ("bbb", sample_patch_complex),
            ("ccc", sample_patch_simple)
        ]):
            with open(temp_patch_dir / f"{name}.json", 'w') as f:
                json.dump(data, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Should be mapped in alphabetical order
        assert loader.patch_keys_map['q'] == "aaa"
        assert loader.patch_keys_map['w'] == "bbb"
        assert loader.patch_keys_map['e'] == "ccc"

    def test_key_mapping_max_patches(self, temp_patch_dir, sample_patch_simple):
        """Test key mapping with maximum number of patches."""
        # Create 26 patches (max keys available)
        for i in range(26):
            patch_file = temp_patch_dir / f"patch_{i:02d}.json"
            with open(patch_file, 'w') as f:
                json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # All 26 keys should be mapped
        assert len(loader.patch_keys_map) == 26
        assert all(key in loader.patch_keys_map for key in PATCH_KEYS)

    def test_key_mapping_excess_patches(self, temp_patch_dir, sample_patch_simple):
        """Test key mapping with more patches than available keys."""
        # Create 30 patches (more than 26 keys)
        for i in range(30):
            patch_file = temp_patch_dir / f"patch_{i:02d}.json"
            with open(patch_file, 'w') as f:
                json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Only first 26 should be mapped
        assert len(loader.patch_keys_map) == 26
        assert len(loader.patches) == 30  # All loaded
        # First 26 alphabetically should be mapped
        sorted_patches = sorted(loader.patches.keys())
        for i, key in enumerate(PATCH_KEYS):
            assert loader.patch_keys_map[key] == sorted_patches[i]


class TestPatchRetrieval:
    """Test patch retrieval methods."""

    def test_get_patch_by_key(self, populated_patch_dir):
        """Test retrieving patch by keyboard key."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        # Get patch by first key
        patch = loader.get_patch_by_key('q')
        assert patch is not None
        assert 'name' in patch
        assert 'bass_pattern' in patch

    def test_get_patch_by_invalid_key(self, populated_patch_dir):
        """Test retrieving patch with unmapped key."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        # Try to get patch with unmapped key
        patch = loader.get_patch_by_key('z')  # Assuming only 2 patches (q, w)
        assert patch is None

    def test_get_all_patches(self, populated_patch_dir):
        """Test retrieving all patches with keys."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        all_patches = loader.get_all_patches()

        # Should return list of (key, patch) tuples
        assert len(all_patches) == 2  # populated_patch_dir has 2 patches
        for key, patch in all_patches:
            assert key in PATCH_KEYS
            assert 'name' in patch

    def test_get_first_patch(self, populated_patch_dir):
        """Test getting first available patch."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))
        loader.scan_patches()

        first = loader.get_first_patch()
        assert first is not None
        key, patch = first
        assert key == 'q'  # First key
        assert 'name' in patch

    def test_get_first_patch_empty(self, temp_patch_dir):
        """Test getting first patch when no patches loaded."""
        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        first = loader.get_first_patch()
        assert first is None


class TestPatchLoaderEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_patch_with_special_characters_in_name(self, temp_patch_dir):
        """Test patch file with special characters."""
        patch_data = {
            "name": "Special! @#$ Patch",
            "description": "Has special chars",
            "root_note": 36,
            "bass_pattern": [[36, 100, "C"]],
            "drum_pattern": {"steps": [[[36, 100]]]}
        }

        # File name with underscores and dashes
        patch_file = temp_patch_dir / "special_patch-v1.json"
        with open(patch_file, 'w') as f:
            json.dump(patch_data, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        assert "special_patch-v1" in loader.patches

    def test_scan_patches_repeatedly(self, populated_patch_dir):
        """Test that repeated scanning works correctly."""
        loader = PatchLoader(patches_dir=str(populated_patch_dir))

        # Scan multiple times
        for _ in range(5):
            loader.scan_patches()

        # Should have consistent results
        assert len(loader.patches) == 2

    def test_key_mapping_updates_after_deletion(self, temp_patch_dir,
                                                sample_patch_simple):
        """Test that key mapping updates when patches deleted."""
        # Create 3 patches
        for name in ["aaa", "bbb", "ccc"]:
            with open(temp_patch_dir / f"{name}.json", 'w') as f:
                json.dump(sample_patch_simple, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        # Verify initial mapping
        assert loader.patch_keys_map['q'] == "aaa"
        assert loader.patch_keys_map['w'] == "bbb"
        assert loader.patch_keys_map['e'] == "ccc"

        # Delete middle patch
        (temp_patch_dir / "bbb.json").unlink()
        loader.scan_patches()

        # Mapping should update
        assert loader.patch_keys_map['q'] == "aaa"
        assert loader.patch_keys_map['w'] == "ccc"
        assert 'e' not in loader.patch_keys_map or \
               loader.patch_keys_map.get('e') != "bbb"

    def test_very_large_patterns(self, temp_patch_dir):
        """Test loading patch with very large patterns."""
        # Create patch with 128 steps
        large_patch = {
            "name": "Large Patch",
            "description": "128 steps",
            "root_note": 36,
            "bass_pattern": [[36 + (i % 12), 100, f"N{i}"] for i in range(128)],
            "drum_pattern": {
                "steps": [[[36, 100]] for _ in range(128)]
            }
        }

        patch_file = temp_patch_dir / "large.json"
        with open(patch_file, 'w') as f:
            json.dump(large_patch, f)

        loader = PatchLoader(patches_dir=str(temp_patch_dir))
        loader.scan_patches()

        patch = loader.patches["large"]
        assert len(patch['bass_pattern']) == 128
        assert len(patch['drum_pattern']) == 128
