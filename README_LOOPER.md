# Acid Looper - Dynamic Edition

A refactored Roland T-8 acid bassline looper with dynamic patch loading and live controls.

## Features

- **Dynamic Patch Loading**: Patches are loaded from JSON files in the `patches/` directory
- **Keyboard Mapping**: Each patch is mapped to keys `qwertyuiopasdfghjklzxcvbnm`
- **Live Tempo Control**: Use arrow keys ↑/↓ to adjust BPM (60-180)
- **Hot-Reload**: The patches directory is monitored every second - add/modify patches while running!
- **Seamless Switching**: Patch changes happen at the end of the current loop

## Quick Start

```bash
# Run the looper
./run_looper.sh

# Or directly:
source .venv/bin/activate
python3 acid_looper.py
```

## Controls

- **[q-m]** - Switch to different patches (see on-screen mapping)
- **[↑]** - Increase tempo by 2 BPM
- **[↓]** - Decrease tempo by 2 BPM
- **[ESC]** - Quit the looper

## Patch Format

Patches are JSON files in the `patches/` directory:

```json
{
  "name": "My Acid Pattern",
  "description": "A cool acid bassline",
  "root_note": 36,
  "bass_pattern": [
    [36, 100, "step_0"],
    [38, 110, "step_1"],
    ...
  ],
  "drum_pattern": {
    "type": "elaborate_tech_drums_64"
  }
}
```

### Bass Pattern Format

Each entry in `bass_pattern` is: `[note, velocity, label]`

- **note**: MIDI note number (0-127)
- **velocity**: Note velocity (0-127)
- **label**: Human-readable label for debugging

### Drum Pattern Types

- `elaborate_tech_drums_64`: A 64-step techno drum pattern with kick, snare, and hi-hats

## Creating New Patches

1. Create a new `.json` file in the `patches/` directory
2. Follow the format above
3. The looper will automatically detect it within 1 second
4. Use the displayed key to switch to your new patch

## File Structure

```
.
├── acid_looper.py          # Main refactored script
├── run_looper.sh           # Launch script
├── patches/                # Patch directory
│   ├── deep_acid.json      # Deep progressive acid
│   ├── melodic_acid.json   # Melodic pattern
│   └── groove_acid.json    # Groovy syncopated pattern
└── README_LOOPER.md        # This file
```

## Technical Details

- **BPM Range**: 60-180 BPM
- **Pattern Length**: Flexible (usually 64 steps for 16-bar loops)
- **Channels**:
  - Bass: Channel 2
  - Drums: Channel 10
- **Step Resolution**: 16th notes

## Tips

- Start with existing patches as templates
- Experiment with velocity values (>110 = accented notes)
- Create variations of patterns by copying and modifying
- The looper monitors file changes, so you can edit patches live!

## Old Scripts

The original scripts are still available:
- `play_acid_loop_manual.py` - Original manual control version
- `acid_looper_interactive.py` - Interactive controller wrapper

Enjoy making acid! 🎵
