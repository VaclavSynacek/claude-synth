# Testing Guide for Roland T-8 Acid Looper

## Overview

This project includes a comprehensive test suite that enables development and CI/CD without requiring physical Roland T-8 hardware. The tests cover all major components with a focus on reliability, maintainability, and ease of use.

## Test Statistics

- **Total Tests**: 148
- **Unit Tests**: 123 (83%)
- **Integration Tests**: 25 (17%)
- **Success Rate**: 100%
- **Code Coverage**: 38% (focused on business logic)

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and mock infrastructure
├── fixtures/                # Test data
│   └── patches/            # Sample JSON patch files
├── unit/                    # Unit tests (isolated components)
│   ├── test_tempo_controller.py       # 25 tests
│   ├── test_visual_feedback.py        # 48 tests
│   ├── test_drum_pattern_generator.py # 23 tests
│   └── test_patch_loader.py           # 27 tests
└── integration/             # Integration tests (component interactions)
    ├── test_acid_player_simple.py           # 12 tests
    └── test_visualization_and_patches.py    # 13 tests
```

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh verbose

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Quick run without coverage
./run_tests.sh quick
```

### Manual Execution

```bash
# Setup environment
uv venv
source .venv/bin/activate
uv pip install mido python-rtmidi pytest pytest-cov pytest-mock pytest-timeout freezegun

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_tempo_controller.py -v

# Run specific test class
pytest tests/unit/test_tempo_controller.py::TestTempoControllerInitialization -v

# Run specific test
pytest tests/unit/test_tempo_controller.py::TestTempoControllerInitialization::test_default_initialization -v
```

## Test Categories

### Unit Tests (123 tests)

Unit tests verify isolated component functionality without external dependencies.

#### TempoController (25 tests)
- BPM validation and boundaries (60-180 range)
- Step duration calculations for 16th notes
- Tempo increase/decrease functionality
- Mathematical accuracy of timing formulas

**Coverage**: 100% of TempoController class

#### VisualFeedback (48 tests)
- Note-to-name conversion (MIDI note → "C4" format)
- Bar graph generation for note visualization
- Step progress indicators with percentage
- Edge cases (notes outside range, zero steps, etc.)

**Coverage**: 100% of VisualFeedback class

#### DrumPatternGenerator (23 tests)
- 64-step drum pattern generation
- Velocity variations by position
- Drum note mapping validation
- Pattern structure and consistency

**Coverage**: 100% of DrumPatternGenerator class

#### PatchLoader (27 tests)
- JSON file parsing and validation
- Hot-reload functionality (detect new/modified/deleted patches)
- Keyboard key mapping (q-m → patches)
- Error handling for malformed files

**Coverage**: ~95% of PatchLoader class

### Integration Tests (25 tests)

Integration tests verify interactions between components.

#### AcidPlayer (12 tests)
- MIDI channel configuration (channel 1 for bass, 9 for drums)
- Method signatures and availability
- Port management and cleanup
- Typical usage scenarios

**Coverage**: Basic functionality verified with mocks

#### Visualization & Patches (13 tests)
- Visualization accuracy with real patch data
- Step progress through patterns
- Tempo controller with pattern playback
- End-to-end workflow simulation

**Coverage**: Integration paths verified

## Mock Infrastructure

### MockMIDIPort
Simulates Roland T-8 MIDI device without hardware:
- Captures all sent MIDI messages
- Tracks message count and types
- Provides inspection API
- Handles port open/close

### MockMIDOBackend
Replaces `mido` library for testing:
- Virtual port enumeration
- Port management
- No actual MIDI communication

### Test Fixtures

**Sample Patches** (in `tests/fixtures/patches/`):
- `test_simple.json` - 8-step basic pattern
- `test_empty.json` - Empty pattern (edge case)
- `test_invalid.json` - Malformed JSON
- `test_malformed.txt` - Non-JSON file

**Pytest Fixtures**:
- `mock_midi_port` - Mock MIDI output port
- `mock_mido_backend` - Mock MIDI backend
- `sample_patch_simple` - 8-step test patch
- `sample_patch_complex` - 64-step test patch
- `sample_patch_empty` - Empty patch
- `temp_patch_dir` - Temporary directory for patches
- `populated_patch_dir` - Pre-populated with test patches

## What Is Tested

### ✅ Fully Tested Components

1. **Tempo Control**
   - BPM range enforcement (60-180)
   - Step duration calculations
   - Tempo changes during playback simulation

2. **Visualization**
   - Note height visualization (28-60 range)
   - Step progress indicators
   - Note name formatting (all MIDI notes 0-127)

3. **Drum Patterns**
   - 64-step pattern generation
   - Velocity variations
   - Rhythmic structure consistency

4. **Patch Management**
   - JSON loading and parsing
   - Hot-reload detection
   - File watching and timestamps
   - Keyboard key mapping

5. **Patch Switching**
   - Multiple patch loading
   - State preservation
   - Queue simulation

### ⚠️ Partially Tested

1. **MIDI Communication**
   - Basic configuration verified
   - Method signatures tested
   - Actual message sending not fully validated (due to mocking complexity)

### ❌ Not Tested

1. **Curses UI (AcidLooperCurses)**
   - Main event loop
   - Terminal rendering
   - Keyboard input handling
   - Screen refreshing

**Rationale**: Testing terminal UIs requires complex mocking and provides limited value. Core business logic is thoroughly tested instead.

2. **Main Entry Point**
   - Port detection
   - Application startup
   - Command-line handling

**Rationale**: Integration testing of the full application requires either hardware or complex end-to-end test infrastructure.

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/test.yml` workflow runs automatically on:
- Every push to any branch
- Every pull request to main/master
- Nightly at 2 AM UTC

**Test Matrix**:
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
- OS: Ubuntu Latest

**Pipeline Steps**:
1. Install `uv` package manager
2. Create virtual environment
3. Install dependencies
4. Run full test suite
5. Generate coverage report
6. Upload coverage to Codecov
7. Fail if coverage < 70%

### CI/CD Requirements

All tests must:
- Run without user interaction
- Complete within 2 minutes
- Not require physical hardware
- Pass on all Python versions 3.8+

## Writing New Tests

### Guidelines

1. **Unit Test Template**
```python
import pytest
from acid_looper_curses import ComponentName

class TestComponentFeature:
    """Test specific feature of component."""

    def test_expected_behavior(self):
        """Test that feature behaves correctly."""
        # Arrange
        component = ComponentName()

        # Act
        result = component.method()

        # Assert
        assert result == expected_value
```

2. **Integration Test Template**
```python
def test_component_interaction(fixture1, fixture2):
    """Test interaction between components."""
    # Setup
    component_a = ComponentA(fixture1)
    component_b = ComponentB(fixture2)

    # Execute integration
    result = component_a.interact_with(component_b)

    # Verify
    assert result.state == expected_state
```

### Best Practices

- **Descriptive Names**: Test names should describe what is being tested
- **Single Assertion**: Each test should verify one specific behavior
- **Independence**: Tests should not depend on each other
- **Fast Execution**: Unit tests should run in milliseconds
- **Clear Failures**: Assertion messages should explain what went wrong

### Using Fixtures

```python
def test_with_patch(temp_patch_dir, sample_patch_simple):
    """Example using fixtures from conftest.py"""
    # temp_patch_dir is an empty temporary directory
    # sample_patch_simple is a pre-defined test patch

    # Create patch file
    patch_file = temp_patch_dir / "test.json"
    with open(patch_file, 'w') as f:
        json.dump(sample_patch_simple, f)

    # Test code...
```

## Troubleshooting

### Tests Fail to Import Module

**Error**: `ModuleNotFoundError: No module named 'acid_looper_curses'`

**Solution**:
```bash
# Make sure you're in the project root directory
cd /path/to/claude-synth

# Verify Python can find the module
python3 -c "import acid_looper_curses; print('OK')"
```

### MIDI Tests Fail

**Error**: `ImportError: No module named 'mido'`

**Solution**:
```bash
source .venv/bin/activate
uv pip install mido python-rtmidi
```

### Coverage Too Low

If coverage drops below acceptable levels:
1. Identify uncovered lines: `pytest --cov=. --cov-report=term-missing`
2. View HTML report: `xdg-open htmlcov/index.html`
3. Add tests for critical uncovered code
4. Update coverage threshold if justified

### Tests Timeout

If tests take too long:
```bash
# Run with timeout details
pytest --durations=10

# Increase timeout for specific test
@pytest.mark.timeout(10)
def test_slow_operation():
    pass
```

## Future Improvements

### Potential Additions

1. **End-to-End Tests**
   - Full application workflow simulation
   - Mock hardware device with realistic timing
   - Multi-patch session testing

2. **Performance Tests**
   - Timing accuracy validation
   - Patch hot-reload performance
   - Memory usage monitoring

3. **UI Tests**
   - Curses output capture and validation
   - Keyboard input simulation
   - Screen layout verification

4. **Stress Tests**
   - Rapid patch switching
   - Large pattern files (>1000 steps)
   - Extended playback sessions

## Contributing

When contributing tests:

1. **Run Full Suite**: Ensure all tests pass before committing
2. **Add Tests for Bugs**: Every bug fix should include a test
3. **Maintain Coverage**: Don't decrease overall coverage
4. **Update Documentation**: Add new test categories to this guide
5. **Follow Style**: Match existing test structure and naming

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [pytest-mock Plugin](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Summary

This test suite enables confident development without physical hardware by:
- ✅ Covering all major business logic components
- ✅ Enabling CI/CD automation
- ✅ Providing fast feedback during development
- ✅ Ensuring code quality and reliability
- ✅ Facilitating safe refactoring

Total Test Execution Time: **< 1 second** ⚡
