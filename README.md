# Roland T-8 Acid Looper

A dynamic Roland T-8 acid bassline looper with MIDI sequencing, hot-reload patch management, and comprehensive testing.

## Features

- **Dynamic Patch Loading**: Load patches from JSON files with hot-reload support
- **Keyboard Control**: Map patches to keyboard keys (q-m) for quick switching
- **Live Tempo Control**: Adjust BPM (60-180) with arrow keys during playback
- **Seamless Patch Switching**: Changes happen at loop boundaries without artifacts
- **Visual Feedback**: Real-time display of notes, progress, and patch information
- **Comprehensive Tests**: 148 automated tests for CI/CD without hardware

## Quick Start

```bash
# Run the looper
./run_looper.sh

# Run tests
./run_tests.sh
```

## Project Structure

```
claude-synth/
├── acid_looper_curses.py      # Main application
├── patches/                   # Patch JSON files
│   ├── deep_acid.json
│   ├── melodic_techno.json
│   └── ...
├── tests/                     # Comprehensive test suite
│   ├── unit/                  # Unit tests (123 tests)
│   ├── integration/           # Integration tests (25 tests)
│   └── fixtures/              # Test data
├── run_looper.sh             # Launch script
├── run_tests.sh              # Test runner
├── TESTING.md                # Testing documentation
├── TESTING_STRATEGY.md       # Test strategy and design
└── pyproject.toml            # Project configuration
```

## Testing

This project includes a comprehensive test harness that enables development without physical Roland T-8 hardware.

### Test Suite Overview

- **Total Tests**: 148 (100% passing)
- **Unit Tests**: 123 tests covering business logic
- **Integration Tests**: 25 tests covering component interactions
- **Execution Time**: < 1 second
- **Code Coverage**: 38% (focused on testable business logic)

### Running Tests

```bash
# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh verbose

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Generate coverage report
pytest --cov=. --cov-report=html
```

### What's Tested

✅ **Fully Tested Components**:
- Tempo control (BPM management, step duration calculations)
- Visual feedback (note visualization, progress indicators)
- Drum pattern generation (64-step patterns, velocity variations)
- Patch loading (JSON parsing, hot-reload, keyboard mapping)
- Patch switching (seamless transitions, state management)

⚠️ **Partially Tested**:
- MIDI communication (basic functionality verified with mocks)

❌ **Not Tested**:
- Curses UI (terminal rendering complexity)
- Main entry point (requires hardware integration)

See [TESTING.md](TESTING.md) for complete testing documentation.

## CI/CD Integration

Tests run automatically on:
- Every push to any branch
- Pull requests to main/master
- Nightly schedule (2 AM UTC)

GitHub Actions workflow tests against Python 3.8, 3.9, 3.10, 3.11, and 3.12.

## Controls

- **[q-m]** - Switch patches (mapped to available patches)
- **[↑]** - Increase tempo
- **[↓]** - Decrease tempo
- **[ESC]** - Quit

## Patch Format

Create JSON files in `patches/` directory:

```json
{
  "name": "My Acid Pattern",
  "description": "A cool acid bassline",
  "root_note": 36,
  "bass_pattern": [
    [36, 100, "C"],
    [38, 90, "D"],
    ...
  ],
  "drum_pattern": {
    "steps": [
      [[36, 100], [42, 60]],
      [[42, 60]],
      ...
    ]
  }
}
```

## Development

### Setup

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install mido python-rtmidi

# Install dev dependencies for testing
uv pip install pytest pytest-cov pytest-mock pytest-timeout freezegun
```

### Testing Strategy

The testing strategy focuses on:
1. **Hardware Independence**: All tests run without Roland T-8
2. **Mock Infrastructure**: MockMIDIPort simulates MIDI device
3. **Fast Feedback**: Tests complete in under 1 second
4. **CI/CD Ready**: Automated testing on every commit
5. **Business Logic Coverage**: Core components thoroughly tested

See [TESTING_STRATEGY.md](TESTING_STRATEGY.md) for detailed strategy.

## Requirements

- Python 3.8+
- `uv` package manager
- `mido` and `python-rtmidi` for MIDI
- Roland T-8 hardware (for actual music production)
- No hardware needed for development/testing!

## Contributing

1. Write tests for new features
2. Ensure all tests pass: `./run_tests.sh`
3. Maintain or improve code coverage
4. Update documentation

## Documentation

- [README_LOOPER.md](README_LOOPER.md) - Original user guide
- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - Testing strategy and design
- [CLAUDE.md](CLAUDE.md) - Development guidelines

## License

Open source project for Roland T-8 enthusiasts.
