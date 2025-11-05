# Testing Strategy for Roland T-8 Acid Looper

## Overview
This document outlines the comprehensive testing strategy for the Roland T-8 Acid Looper application, designed to enable automated testing in CI/CD environments without requiring physical hardware.

## Testing Goals

1. **Hardware Independence**: All tests must run without a physical Roland T-8 device
2. **Seamless Patch Switching**: Verify patches switch without audio artifacts
3. **Visualization Accuracy**: Ensure UI correctly displays patch state and progress
4. **Timing Precision**: Validate tempo control and step timing accuracy
5. **Hot-Reload Functionality**: Test dynamic patch loading during playback
6. **State Management**: Verify correct state transitions and queueing

## Testing Architecture

### 1. Mock MIDI Infrastructure

**MockMIDIPort**
- Simulates Roland T-8 MIDI device
- Captures all sent MIDI messages
- Provides message inspection API
- No actual sound generation

**MockMIDIBackend**
- Replaces `mido` library in tests
- Provides virtual port enumeration
- Tracks message timing and order

### 2. Test Categories

#### Unit Tests (Target: 70% coverage)
Tests for isolated components with no external dependencies:

- **TempoController**
  - BPM validation (60-180 range)
  - Step duration calculations
  - Boundary conditions

- **VisualFeedback**
  - Note-to-name conversion (60→C4)
  - Bar graph generation
  - Step indicator rotation
  - Edge cases (notes < 28, > 60)

- **DrumPatternGenerator**
  - Pattern length validation (64 steps)
  - Velocity ranges (0-127)
  - Drum note mapping consistency
  - Pattern structure validation

- **PatchLoader**
  - JSON parsing and validation
  - Malformed JSON handling
  - File timestamp tracking
  - Patch-to-key mapping (q-m)

#### Integration Tests (Target: 20% coverage)
Tests for component interactions:

- **AcidPlayer + MockMIDI**
  - Correct MIDI channel usage (1 for bass, 9 for drums)
  - Note On/Off message format
  - Velocity transmission accuracy
  - Message timing order

- **Patch Switching**
  - Queue mechanism (patches queued at loop end)
  - Seamless transitions (no dropped notes)
  - State consistency during switch
  - Multiple rapid patch changes

- **Hot-Reload**
  - Detect new patch files
  - Detect modified patches
  - Detect deleted patches
  - File system watching accuracy

- **Visualization Rendering**
  - Step progress accuracy
  - Beat position calculations
  - Instrument activity indicators
  - Current vs queued patch markers

#### End-to-End Tests (Target: 10% coverage)
Simulated full application workflows:

- **Complete Playback Cycle**
  - Load patch → Play → Switch → Stop
  - Verify message sequence
  - Timing consistency over multiple loops

- **Multi-Patch Session**
  - Load multiple patches
  - Switch between them during playback
  - Verify no state leakage

### 3. Test Fixtures

**Sample Patches** (`tests/fixtures/patches/`)
- `test_simple.json` - Minimal valid patch (8 steps)
- `test_complex.json` - Full-featured patch (64 steps)
- `test_empty.json` - Empty patch (edge case)
- `test_invalid.json` - Malformed JSON (error handling)
- `test_missing_fields.json` - Incomplete patch (validation)

**Expected Behaviors**
- Documented expected MIDI message sequences
- Reference timing calculations
- Expected visualization outputs

### 4. Test Utilities

**Timing Helpers**
- Tolerance-based time comparison (±5ms acceptable)
- Step duration validation
- BPM-to-milliseconds conversion verification

**Message Validators**
- MIDI message format checkers
- Sequence validators (Note On followed by Note Off)
- Channel verification

**State Inspectors**
- Patch state snapshots
- Playback position tracking
- Queue state verification

## Implementation Plan

### Phase 1: Infrastructure Setup
1. Install pytest and testing dependencies
2. Create test directory structure
3. Set up pytest configuration
4. Configure code coverage reporting

### Phase 2: Mock Development
1. Implement MockMIDIPort
2. Implement MockMIDIBackend
3. Create test fixtures (sample patches)
4. Build test utilities and helpers

### Phase 3: Unit Tests
1. TempoController tests
2. VisualFeedback tests
3. DrumPatternGenerator tests
4. PatchLoader tests

### Phase 4: Integration Tests
1. AcidPlayer with mocked MIDI
2. Patch switching tests
3. Hot-reload tests
4. Visualization accuracy tests

### Phase 5: CI/CD Integration
1. Create GitHub Actions workflow
2. Add coverage reporting
3. Configure test requirements
4. Add badge to README

### Phase 6: Documentation
1. Write test running guide
2. Document test fixtures
3. Create contribution guidelines for tests

## Success Criteria

- ✅ All tests pass without physical Roland T-8
- ✅ Code coverage ≥ 80%
- ✅ Tests run in CI/CD pipeline
- ✅ Patch switching verified without artifacts
- ✅ Visualization accuracy validated
- ✅ Timing precision within ±5ms tolerance
- ✅ Hot-reload functionality confirmed
- ✅ All edge cases covered

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v

# Run with timing information
uv run pytest --durations=10
```

## CI/CD Integration

Tests will run automatically on:
- Every push to feature branches
- Every pull request
- Scheduled nightly builds

Pipeline will fail if:
- Any test fails
- Coverage drops below 80%
- Performance regression detected

## Maintenance

- Update test fixtures when patch format changes
- Add tests for new features before implementation (TDD)
- Review and update mocks when mido library updates
- Maintain test documentation alongside code changes
