"""
Pytest configuration and shared fixtures for AI Augmented Generative Sequencer for Roland T-8 tests.
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock
import pytest

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockMIDIMessage:
    """Mock MIDI message that captures message data."""

    def __init__(self, msg_type: str, **kwargs):
        self.type = msg_type
        self.note = kwargs.get('note', 0)
        self.velocity = kwargs.get('velocity', 0)
        self.channel = kwargs.get('channel', 0)
        self.time = kwargs.get('time', 0)

    def __repr__(self):
        return f"MockMIDIMessage(type={self.type}, note={self.note}, velocity={self.velocity}, channel={self.channel})"

    def __eq__(self, other):
        if not isinstance(other, MockMIDIMessage):
            return False
        return (self.type == other.type and
                self.note == other.note and
                self.velocity == other.velocity and
                self.channel == other.channel)


class MockMIDIPort:
    """Mock MIDI output port that captures sent messages."""

    def __init__(self, name: str = "Mock Roland T-8"):
        self.name = name
        self.messages: List[MockMIDIMessage] = []
        self.is_closed = False
        self._send_count = 0

    def send(self, message: Any) -> None:
        """Capture sent MIDI message."""
        if self.is_closed:
            raise RuntimeError("Port is closed")

        # Convert message to our mock format
        mock_msg = MockMIDIMessage(
            msg_type=message.type,
            note=getattr(message, 'note', 0),
            velocity=getattr(message, 'velocity', 0),
            channel=getattr(message, 'channel', 0)
        )
        self.messages.append(mock_msg)
        self._send_count += 1

    def close(self) -> None:
        """Close the port."""
        self.is_closed = True

    def get_messages_by_type(self, msg_type: str) -> List[MockMIDIMessage]:
        """Get all messages of a specific type."""
        return [msg for msg in self.messages if msg.type == msg_type]

    def get_messages_by_channel(self, channel: int) -> List[MockMIDIMessage]:
        """Get all messages for a specific channel."""
        return [msg for msg in self.messages if msg.channel == channel]

    def clear_messages(self) -> None:
        """Clear all captured messages."""
        self.messages = []
        self._send_count = 0

    @property
    def message_count(self) -> int:
        """Total number of messages sent."""
        return self._send_count


class MockMIDOBackend:
    """Mock mido backend for testing without actual MIDI hardware."""

    def __init__(self):
        self.output_ports = ["Mock Roland T-8", "Mock Other Device"]
        self._open_ports: Dict[str, MockMIDIPort] = {}

    def get_output_names(self) -> List[str]:
        """Return list of available output port names."""
        return self.output_ports.copy()

    def open_output(self, name: str) -> MockMIDIPort:
        """Open a mock output port."""
        if name not in self._open_ports:
            self._open_ports[name] = MockMIDIPort(name)
        return self._open_ports[name]

    def add_port(self, name: str) -> None:
        """Add a new port to available outputs."""
        if name not in self.output_ports:
            self.output_ports.append(name)

    def remove_port(self, name: str) -> None:
        """Remove a port from available outputs."""
        if name in self.output_ports:
            self.output_ports.remove(name)
            if name in self._open_ports:
                self._open_ports[name].close()
                del self._open_ports[name]


@pytest.fixture
def mock_mido_backend():
    """Provide a mock mido backend."""
    return MockMIDOBackend()


@pytest.fixture
def mock_midi_port():
    """Provide a mock MIDI port."""
    return MockMIDIPort()


@pytest.fixture
def sample_patch_simple():
    """Provide a simple test patch (8 steps)."""
    return {
        "name": "Test Simple",
        "description": "Simple test patch with 8 steps",
        "root_note": 36,
        "bass_pattern": [
            [36, 100, "C"],
            [38, 90, "D"],
            [40, 80, "E"],
            [41, 70, "F"],
            [43, 100, "G"],
            [45, 90, "A"],
            [47, 80, "B"],
            [48, 100, "C+"]
        ],
        "drum_pattern": {
            "steps": [
                [[36, 100]],  # Kick
                [[42, 60]],   # HH
                [[36, 100]],  # Kick
                [[42, 60]],   # HH
                [[38, 100]],  # Snare
                [[42, 60]],   # HH
                [[36, 100]],  # Kick
                [[42, 60]]    # HH
            ]
        }
    }


@pytest.fixture
def sample_patch_complex():
    """Provide a complex test patch (64 steps)."""
    bass = [[36 + (i % 12), 100 - (i * 2) % 50, f"Note{i}"] for i in range(64)]
    drums = [[[36, 100], [42, 60]] if i % 4 == 0 else [[42, 60]] for i in range(64)]

    return {
        "name": "Test Complex",
        "description": "Complex test patch with 64 steps",
        "root_note": 36,
        "bass_pattern": bass,
        "drum_pattern": {
            "steps": drums
        }
    }


@pytest.fixture
def sample_patch_empty():
    """Provide an empty test patch."""
    return {
        "name": "Test Empty",
        "description": "Empty test patch",
        "root_note": 36,
        "bass_pattern": [],
        "drum_pattern": {
            "steps": []
        }
    }


@pytest.fixture
def sample_patch_invalid():
    """Provide an invalid patch (malformed JSON string)."""
    return '{"name": "Invalid", "missing": "closing brace"'


@pytest.fixture
def temp_patch_dir(tmp_path):
    """Provide a temporary directory for patch files."""
    patch_dir = tmp_path / "patches"
    patch_dir.mkdir()
    return patch_dir


@pytest.fixture
def create_patch_file(temp_patch_dir):
    """Factory fixture to create patch files in temp directory."""
    def _create_patch(filename: str, patch_data: Dict[str, Any]) -> Path:
        filepath = temp_patch_dir / filename
        with open(filepath, 'w') as f:
            json.dump(patch_data, f, indent=2)
        return filepath
    return _create_patch


@pytest.fixture
def populated_patch_dir(temp_patch_dir, sample_patch_simple, sample_patch_complex):
    """Provide a temp directory pre-populated with test patches."""
    # Create simple patch
    with open(temp_patch_dir / "test_simple.json", 'w') as f:
        json.dump(sample_patch_simple, f)

    # Create complex patch
    with open(temp_patch_dir / "test_complex.json", 'w') as f:
        json.dump(sample_patch_complex, f)

    return temp_patch_dir


@pytest.fixture
def mock_curses():
    """Mock curses module for UI testing."""
    mock = MagicMock()
    mock.color_pair = lambda x: x
    mock.COLORS = 256
    mock.COLOR_PAIRS = 256
    mock.A_BOLD = 1
    mock.A_REVERSE = 2
    mock.curs_set = Mock()
    mock.init_pair = Mock()
    mock.use_default_colors = Mock()
    return mock


@pytest.fixture
def mock_stdscr():
    """Mock curses standard screen."""
    mock = MagicMock()
    mock.getmaxyx.return_value = (40, 120)  # Standard terminal size
    mock.nodelay = Mock()
    mock.keypad = Mock()
    mock.clear = Mock()
    mock.refresh = Mock()
    mock.addstr = Mock()
    mock.getch.return_value = -1  # No input by default
    return mock


# Helper functions for test assertions

def assert_midi_message(message: MockMIDIMessage,
                       msg_type: str,
                       note: int = None,
                       velocity: int = None,
                       channel: int = None) -> None:
    """Assert MIDI message properties."""
    assert message.type == msg_type, f"Expected type {msg_type}, got {message.type}"

    if note is not None:
        assert message.note == note, f"Expected note {note}, got {message.note}"

    if velocity is not None:
        assert message.velocity == velocity, f"Expected velocity {velocity}, got {message.velocity}"

    if channel is not None:
        assert message.channel == channel, f"Expected channel {channel}, got {message.channel}"


def assert_note_on_off_pair(messages: List[MockMIDIMessage],
                           idx: int,
                           note: int,
                           velocity: int,
                           channel: int) -> None:
    """Assert that messages at idx and idx+1 form a valid Note On/Off pair."""
    assert idx + 1 < len(messages), "Not enough messages for Note On/Off pair"

    note_on = messages[idx]
    note_off = messages[idx + 1]

    assert_midi_message(note_on, 'note_on', note=note, velocity=velocity, channel=channel)
    assert_midi_message(note_off, 'note_off', note=note, channel=channel)


def assert_messages_in_sequence(messages: List[MockMIDIMessage],
                               expected_sequence: List[tuple]) -> None:
    """
    Assert that messages follow expected sequence.

    Args:
        messages: List of captured MIDI messages
        expected_sequence: List of (type, note, channel) tuples
    """
    assert len(messages) >= len(expected_sequence), \
        f"Expected at least {len(expected_sequence)} messages, got {len(messages)}"

    for i, (exp_type, exp_note, exp_channel) in enumerate(expected_sequence):
        msg = messages[i]
        assert msg.type == exp_type, \
            f"Message {i}: expected type {exp_type}, got {msg.type}"
        assert msg.note == exp_note, \
            f"Message {i}: expected note {exp_note}, got {msg.note}"
        assert msg.channel == exp_channel, \
            f"Message {i}: expected channel {exp_channel}, got {msg.channel}"
