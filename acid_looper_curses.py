#!/usr/bin/env python3
"""
Acid Bassline Looper for Roland T-8 - Curses Edition
Features:
- Dynamic patch loading from JSON files
- Keyboard mapping (qwertyuiopasdfghjklzxcvbnm)
- Tempo control (up/down arrows)
- Hot-reload patches (monitors directory every 1 second)
- Seamless patch switching at loop end
- Proper TUI using curses
"""

import time
import sys
import os
import json
import curses
import threading
from pathlib import Path
from typing import List, Tuple, Dict, Optional

try:
    import mido
    from mido import Message
except ImportError:
    print("ERROR: mido not installed. Please run: uv pip install mido python-rtmidi")
    sys.exit(1)


# Keyboard mapping for patches
PATCH_KEYS = "qwertyuiopasdfghjklzxcvbnm"


class AcidPlayer:
    """MIDI player for Roland T-8"""
    def __init__(self, output_port):
        self.outport = mido.open_output(output_port)
        self.bass_channel = 1      # Channel 2 for bass
        self.rhythm_channel = 9    # Channel 10 for drums

    def bass_note_on(self, note, velocity=100):
        self.outport.send(Message('note_on', channel=self.bass_channel, note=note, velocity=velocity))

    def bass_note_off(self, note):
        self.outport.send(Message('note_off', channel=self.bass_channel, note=note))

    def drum_note_on(self, drum, velocity=100):
        self.outport.send(Message('note_on', channel=self.rhythm_channel, note=drum, velocity=velocity))

    def drum_note_off(self, drum):
        self.outport.send(Message('note_off', channel=self.rhythm_channel, note=drum))

    def close(self):
        self.outport.close()


class VisualFeedback:
    """Visual feedback utilities"""
    @staticmethod
    def draw_step_indicator(current_step, total_steps):
        filled = (current_step % total_steps) + 1
        circle_steps = [' ', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗']
        circle_index = (filled * 8) // total_steps
        circle = circle_steps[min(circle_index, 8)]
        percentage = int((filled / total_steps) * 100)
        return f"[{circle}] {filled:2d}/{total_steps:2d} ({percentage:3d}%)"

    @staticmethod
    def draw_note_visualizer(note, velocity=100):
        min_note = 28
        max_note = 60
        note_range = max_note - min_note

        if note < min_note:
            height = 0
        elif note > max_note:
            height = 8
        else:
            height = int(((note - min_note) / note_range) * 8)

        bars = ""
        for i in range(8, 0, -1):
            if i <= height:
                bars += "●"
            else:
                bars += "○"
        return bars

    @staticmethod
    def format_note_name(note):
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (note // 12) - 1
        name = note_names[note % 12]
        return f"{name}{octave}"


class DrumPatternGenerator:
    """Generate drum patterns"""
    DRUMS = {
        'kick': 36,
        'snare': 38,
        'closed_hh': 42,
        'open_hh': 46,
        'tom_high': 50,
        'tom_mid': 47,
        'tom_low': 45,
        'clap': 39,
    }

    @staticmethod
    def elaborate_tech_drums_64():
        """Generate 64-step drum pattern"""
        drums = DrumPatternGenerator.DRUMS
        pattern = []
        kick_pattern = [1, 0, 1, 0, 0, 1, 0, 1] * 8
        snare_pattern = [0, 0, 0, 1, 0, 0, 0, 1] * 8

        for step in range(64):
            drum_hits = []
            if kick_pattern[step % len(kick_pattern)]:
                velocity = 120 if step % 8 == 0 else 115
                drum_hits.append((drums['kick'], velocity))
            if snare_pattern[step % len(snare_pattern)]:
                velocity = 110 if step % 16 == 0 else 105
                drum_hits.append((drums['snare'], velocity))
            if step % 2 == 0:
                drum_hits.append((drums['closed_hh'], 75))
            else:
                drum_hits.append((drums['closed_hh'], 65))
            if step % 16 == 7 or step % 16 == 15:
                drum_hits.append((drums['open_hh'], 80))
            pattern.append((drum_hits, f"drums_{step}"))

        return pattern


class PatchLoader:
    """Load and manage patches from JSON files"""
    def __init__(self, patches_dir="patches"):
        self.patches_dir = Path(patches_dir)
        self.patches = {}
        self.patch_keys_map = {}
        self.last_scan_time = 0

    def scan_patches(self) -> bool:
        """Scan patches directory for JSON files. Returns True if changes detected."""
        current_files = set()
        changes_detected = False

        if not self.patches_dir.exists():
            return False

        for json_file in sorted(self.patches_dir.glob("*.json")):
            current_files.add(json_file.stem)

            # Check if file is new or modified
            mtime = json_file.stat().st_mtime
            if json_file.stem not in self.patches or mtime > self.last_scan_time:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    # Parse bass pattern
                    bass_pattern = [(note, vel, label) for note, vel, label in data['bass_pattern']]

                    # Parse drum pattern - now directly from JSON
                    drum_pattern = []
                    if 'drum_pattern' in data and 'steps' in data['drum_pattern']:
                        for step_data in data['drum_pattern']['steps']:
                            # Each step is a list of [drum_note, velocity] pairs
                            drum_hits = [(hit[0], hit[1]) for hit in step_data]
                            drum_pattern.append((drum_hits, f"drums_{len(drum_pattern)}"))

                    self.patches[json_file.stem] = {
                        'name': data['name'],
                        'description': data.get('description', ''),
                        'bass_pattern': bass_pattern,
                        'drum_pattern': drum_pattern,
                        'file': json_file.stem
                    }
                    changes_detected = True
                except Exception as e:
                    pass  # Silently skip bad patches

        # Remove deleted patches
        deleted = set(self.patches.keys()) - current_files
        for patch_name in deleted:
            del self.patches[patch_name]
            changes_detected = True

        self.last_scan_time = time.time()
        self._update_key_mapping()
        return changes_detected

    def _update_key_mapping(self):
        """Map patches to keyboard keys"""
        self.patch_keys_map = {}
        sorted_patches = sorted(self.patches.keys())

        for idx, patch_name in enumerate(sorted_patches):
            if idx < len(PATCH_KEYS):
                key = PATCH_KEYS[idx]
                self.patch_keys_map[key] = patch_name

    def get_patch_by_key(self, key: str) -> Optional[Dict]:
        """Get patch by keyboard key"""
        patch_name = self.patch_keys_map.get(key)
        if patch_name:
            return self.patches[patch_name]
        return None

    def get_all_patches(self) -> List[Tuple[str, Dict]]:
        """Get all patches with their keyboard keys"""
        result = []
        for key in PATCH_KEYS:
            if key in self.patch_keys_map:
                patch_name = self.patch_keys_map[key]
                result.append((key, self.patches[patch_name]))
        return result

    def get_first_patch(self) -> Optional[Tuple[str, Dict]]:
        """Get the first available patch"""
        patches = self.get_all_patches()
        return patches[0] if patches else None


class TempoController:
    """Control tempo with up/down arrow keys"""
    def __init__(self, initial_bpm=90):
        self.bpm = initial_bpm
        self.min_bpm = 60
        self.max_bpm = 180
        self.step = 1

    def increase(self):
        self.bpm = min(self.bpm + self.step, self.max_bpm)

    def decrease(self):
        self.bpm = max(self.bpm - self.step, self.min_bpm)

    def get_step_duration_ms(self):
        """Get step duration in milliseconds (16th notes)"""
        return (60000 / self.bpm) / 4


class AcidLooperCurses:
    """Main looper class with curses UI"""
    def __init__(self, stdscr, player: AcidPlayer, patch_loader: PatchLoader):
        self.stdscr = stdscr
        self.player = player
        self.patch_loader = patch_loader
        self.tempo = TempoController(initial_bpm=90)
        self.current_patch_key = None
        self.next_patch = None
        self.next_patch_key = None
        self.running = True
        self.last_patch_scan = time.time()
        self.needs_full_redraw = False

        # Set up curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(0)  # Non-blocking getch

        # Initialize color pairs if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Header
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Current patch
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Next patch / status
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Errors

    def draw_ui(self, current_patch: Dict):
        """Draw the complete UI"""
        try:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            width = max_x - 1  # Leave 1 char margin
            row = 0

            # Header
            header_text = "ROLAND T-8 ACID LOOPER - DYNAMIC EDITION"
            padding = (width - len(header_text) - 2) // 2
            self.stdscr.addstr(row, 0, "╔" + "═" * (width - 2) + "╗", curses.color_pair(1) | curses.A_BOLD)
            row += 1
            self.stdscr.addstr(row, 0, "║" + " " * padding + header_text + " " * (width - len(header_text) - padding - 2) + "║", curses.color_pair(1) | curses.A_BOLD)
            row += 1
            self.stdscr.addstr(row, 0, "╚" + "═" * (width - 2) + "╝", curses.color_pair(1) | curses.A_BOLD)
            row += 2

            # Available Patches
            title = "─── Available Patches "
            self.stdscr.addstr(row, 0, "┌" + title + "─" * (width - len(title) - 2) + "┐")
            row += 1
            patches = self.patch_loader.get_all_patches()

            # Calculate available space for patch info
            name_width = min(30, (width - 20) // 2)
            desc_width = width - name_width - 20

            for key, patch in patches:
                if row >= max_y - 10:  # Leave room for rest of UI
                    break

                # Choose marker and color based on state
                if key == self.current_patch_key:
                    marker = "▶"
                    color = curses.color_pair(2)  # Green for current
                elif key == self.next_patch_key:
                    marker = "►"
                    color = curses.color_pair(3)  # Yellow for queued next
                else:
                    marker = " "
                    color = 0

                # Truncate if needed
                name = patch['name'][:name_width].ljust(name_width)
                desc = patch['description'][:desc_width].ljust(desc_width)

                line = f"│ {marker} [{key}]  {name} {desc} │"
                if len(line) > width:
                    line = line[:width-1] + "│"
                elif len(line) < width:
                    line = line[:-1].ljust(width-1) + "│"

                self.stdscr.addstr(row, 0, line, color)
                row += 1
            self.stdscr.addstr(row, 0, "└" + "─" * (width - 2) + "┘")
            row += 2

            # Controls
            title = "─── Controls "
            self.stdscr.addstr(row, 0, "┌" + title + "─" * (width - len(title) - 2) + "┐")
            row += 1
            controls_text = "[q-m] Switch  │  [↑/↓] Tempo  │  [ESC] Quit"
            self.stdscr.addstr(row, 0, "│  " + controls_text.ljust(width - 4) + "│")
            row += 1
            self.stdscr.addstr(row, 0, "└" + "─" * (width - 2) + "┘")
            row += 2

            # Now Playing
            title = "─── Now Playing "
            self.stdscr.addstr(row, 0, "┌" + title + "─" * (width - len(title) - 2) + "┐", curses.color_pair(3))
            row += 1
            # Header line 1: Beat and step info
            self.stdscr.addstr(row, 0, "│ " + " " * (width - 3) + "│")
            self.header1_row = row
            row += 1
            # Header line 2: Section info
            self.stdscr.addstr(row, 0, "│ " + " " * (width - 3) + "│")
            self.header2_row = row
            row += 1
            self.stdscr.addstr(row, 0, "├" + "─" * (width - 2) + "┤", curses.color_pair(3))
            row += 1
            # 7 instrument rows
            for i in range(7):
                self.stdscr.addstr(row, 0, "│ " + " " * (width - 3) + "│")
                row += 1
            self.instrument_start_row = self.header2_row + 2
            self.stdscr.addstr(row, 0, "└" + "─" * (width - 2) + "┘", curses.color_pair(3))
            row += 2

            # Footer
            footer = f"BPM: {self.tempo.bpm:3d}  │  Patch: {current_patch['name']}"
            self.stdscr.addstr(row, 0, footer[:width], curses.color_pair(2))

            self.stdscr.refresh()
        except curses.error:
            # Ignore errors when terminal is too small
            pass

    def _draw_velocity_slider(self, velocity: int, max_vel: int = 127, width: int = 24) -> str:
        """Draw a velocity slider bar"""
        filled = int((velocity / max_vel) * width)
        return "[" + "█" * filled + " " * (width - filled) + "]"

    def _extract_section_name(self, label: str) -> str:
        """Extract section prefix from label like 'intro_1' -> 'INTRO'"""
        if '_' in label:
            return label.split('_')[0].upper()
        return "MAIN"

    def _find_next_section_change(self, bass_pattern: list, current_step: int) -> tuple:
        """Find how many beats until next section change"""
        current_label = bass_pattern[current_step][2]
        current_section = self._extract_section_name(current_label)

        # Look ahead for section change
        for i in range(current_step + 1, len(bass_pattern)):
            next_label = bass_pattern[i][2]
            next_section = self._extract_section_name(next_label)
            if next_section != current_section:
                beats_to_change = i - current_step
                return current_section, next_section, beats_to_change

        # No change found, return current section
        return current_section, current_section, 0

    def update_now_playing(self, bass_note: int, bass_vel: int, drum_hits: list,
                          step_idx: int, total_steps: int, bass_pattern: list):
        """Update the entire Now Playing section"""
        try:
            max_y, max_x = self.stdscr.getmaxyx()
            width = max_x - 5  # Account for borders

            # Calculate beat position (assume 16th notes, 4 beats per bar)
            beat_num = (step_idx // 4) + 1
            sixteenth = (step_idx % 4) + 1
            beat_pos = f"{beat_num}.{sixteenth}"

            # Get section info
            current_section, next_section, beats_away = self._find_next_section_change(bass_pattern, step_idx)

            # Header line 1: Beat and Step
            header1 = f"Beat: {beat_pos:5s}  │  Step: {step_idx+1:2d}/{total_steps:2d} ({int((step_idx+1)/total_steps*100):3d}%)"
            self.stdscr.addstr(self.header1_row, 2, header1[:width].ljust(width), curses.color_pair(3))

            # Header line 2: Section with visual progress
            if beats_away > 0:
                # Draw progress bar showing countdown
                bar_width = 24
                progress = max(0, min(bar_width, int((beats_away / 32) * bar_width)))  # Scale to 32 beats
                progress_bar = "█" * (bar_width - progress) + "░" * progress
                section_text = f"Section: {current_section:6s}  │  {progress_bar}  {beats_away:2d} beats to {next_section}"
            else:
                section_text = f"Section: {current_section:6s}"
            self.stdscr.addstr(self.header2_row, 2, section_text[:width].ljust(width), curses.color_pair(3))

            # Prepare drum velocities (indexed by drum type)
            drum_vels = {
                'kick': 0, 'snare': 0, 'clap': 0, 'tom': 0,
                'closed_hh': 0, 'open_hh': 0
            }
            for drum_note, drum_vel in drum_hits:
                if drum_note == DrumPatternGenerator.DRUMS['kick']:
                    drum_vels['kick'] = drum_vel
                elif drum_note == DrumPatternGenerator.DRUMS['snare']:
                    drum_vels['snare'] = drum_vel
                elif drum_note == DrumPatternGenerator.DRUMS['clap']:
                    drum_vels['clap'] = drum_vel
                elif drum_note == DrumPatternGenerator.DRUMS['tom_high'] or \
                     drum_note == DrumPatternGenerator.DRUMS['tom_mid'] or \
                     drum_note == DrumPatternGenerator.DRUMS['tom_low']:
                    drum_vels['tom'] = drum_vel
                elif drum_note == DrumPatternGenerator.DRUMS['closed_hh']:
                    drum_vels['closed_hh'] = drum_vel
                elif drum_note == DrumPatternGenerator.DRUMS['open_hh']:
                    drum_vels['open_hh'] = drum_vel

            # Draw instrument rows
            instruments = [
                ('BASS', VisualFeedback.format_note_name(bass_note), bass_vel),
                ('KICK', '', drum_vels['kick']),
                ('SNARE', '', drum_vels['snare']),
                ('CL-HH', '', drum_vels['closed_hh']),
                ('OP-HH', '', drum_vels['open_hh']),
                ('CLAP', '', drum_vels['clap']),
                ('TOM', '', drum_vels['tom']),
            ]

            for idx, (name, note_name, velocity) in enumerate(instruments):
                slider = self._draw_velocity_slider(velocity)
                accent = "  ▲" if velocity > 110 else ""

                if note_name:  # BASS has note name
                    line = f"{name:6s} {note_name:4s} {slider}  {velocity:3d}/127{accent}"
                else:  # Drums don't have note name
                    line = f"{name:6s}      {slider}  {velocity:3d}/127{accent}"

                self.stdscr.addstr(self.instrument_start_row + idx, 2,
                                 line[:width].ljust(width), curses.color_pair(3))

            self.stdscr.refresh()
        except curses.error:
            pass

    def play_pattern_loop(self, patch: Dict, current_patch: Dict):
        """Play one complete loop of the pattern"""
        bass_pattern = patch['bass_pattern']
        drum_pattern = patch['drum_pattern']
        total_steps = len(bass_pattern)

        for step_idx, (note, velocity, label) in enumerate(bass_pattern):
            # Check if UI needs redrawing (for yellow patch selection or resize)
            if self.needs_full_redraw:
                self.draw_ui(current_patch)
                self.needs_full_redraw = False


            # Check for keyboard input during playback (for immediate tempo changes)
            key = self.stdscr.getch()
            if key == 27:  # ESC
                self.running = False
                return False
            elif key == curses.KEY_RESIZE:
                # Terminal was resized - just flag for redraw
                # Don't clear/refresh here, let draw_ui handle it
                self.needs_full_redraw = True
            elif key == curses.KEY_UP:
                self.tempo.increase()
                # Tempo will be shown in footer, just trigger redraw on next loop
            elif key == curses.KEY_DOWN:
                self.tempo.decrease()
                # Tempo will be shown in footer, just trigger redraw on next loop
            elif key != -1:  # Some other key was pressed
                char = chr(key).lower()
                if char in PATCH_KEYS:
                    new_patch = self.patch_loader.get_patch_by_key(char)
                    if new_patch:
                        # Queue the next patch (will be yellow in UI)
                        self.next_patch = new_patch
                        self.next_patch_key = char
                        # Trigger immediate UI redraw to show yellow selection
                        self.needs_full_redraw = True

            # Visual feedback - get current drum hits
            drum_hits = []
            if step_idx < len(drum_pattern):
                drum_hits, _ = drum_pattern[step_idx]

            # Update the Now Playing display
            self.update_now_playing(note, velocity, drum_hits, step_idx, total_steps, bass_pattern)

            # Play drums
            if step_idx < len(drum_pattern):
                drum_hits, _ = drum_pattern[step_idx]
                for drum_note, drum_vel in drum_hits:
                    self.player.drum_note_on(drum_note, drum_vel)

            # Play bass
            self.player.bass_note_on(note, velocity)
            time.sleep(self.tempo.get_step_duration_ms() / 1000)

            # Stop notes
            self.player.bass_note_off(note)
            if step_idx < len(drum_pattern):
                drum_hits, _ = drum_pattern[step_idx]
                for drum_note, _ in drum_hits:
                    self.player.drum_note_off(drum_note)

            time.sleep(0.01)

        return True

    def run(self):
        """Main loop"""
        # Initial patch scan
        self.patch_loader.scan_patches()

        first_patch = self.patch_loader.get_first_patch()
        if not first_patch:
            self.stdscr.addstr(0, 0, "ERROR: No patches found in patches/ directory!")
            self.stdscr.refresh()
            self.stdscr.getch()
            return

        self.current_patch_key, current_patch = first_patch
        self.draw_ui(current_patch)

        try:
            while self.running:
                # Check for patch directory changes (every 1 second)
                if time.time() - self.last_patch_scan >= 1.0:
                    if self.patch_loader.scan_patches():
                        self.needs_full_redraw = True
                    self.last_patch_scan = time.time()

                # Play one loop
                success = self.play_pattern_loop(current_patch, current_patch)
                if not success:
                    break

                # Check if patch change was requested during loop
                if self.next_patch:
                    current_patch = self.next_patch
                    self.next_patch = None
                    # Update the current patch key
                    for key, patch in self.patch_loader.get_all_patches():
                        if patch == current_patch:
                            self.current_patch_key = key
                            break
                    # Clear the next patch key (no longer queued)
                    self.next_patch_key = None
                    # Redraw UI with new current patch (green)
                    self.draw_ui(current_patch)

        except KeyboardInterrupt:
            pass
        finally:
            pass


def main_curses(stdscr, player, patch_loader):
    """Curses wrapper main function"""
    looper = AcidLooperCurses(stdscr, player, patch_loader)
    looper.run()


def main():
    try:
        print("\n[INFO] Searching for Roland T-8 MIDI port...\n")
        t8_port = None
        for port in mido.get_output_names():
            if "T-8" in port:
                t8_port = port
                print(f"[✓] Found: {port}\n")
                break

        if not t8_port:
            print("[ERROR] T-8 MIDI port not found!")
            print("[INFO] Available ports:")
            for port in mido.get_output_names():
                print(f"      - {port}")
            sys.exit(1)

        player = AcidPlayer(t8_port)
        patch_loader = PatchLoader("patches")

        print("[INFO] Starting looper in curses mode...\n")
        time.sleep(1)

        # Run curses application
        curses.wrapper(main_curses, player, patch_loader)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'player' in locals():
            player.close()
        print("\n✨ Acid looper stopped!\n")


if __name__ == "__main__":
    main()
