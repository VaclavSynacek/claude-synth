# Electro Swing Patch Guide - REVISED

## Overview
8 compatible electro swing patches inspired by Parov Stelar's style, all at **125 BPM**.
Designed for seamless live transitions and smooth looping.

**NEW FEATURES:**
- **TRUE SWING TIMING** (swing_ratio: 0.66) - authentic shuffle/triplet feel
- Bass instrument plays dual roles: **bass foundation + lead melody**
- High octave melodies (2 octaves up) create counterpoint
- On-grid bass + off-grid lead = rich polyrhythmic texture
- More elaborate drum patterns with layered percussion
- Maximum use of T-8 drum kit (kick, snare, closed/open hi-hat, tom, clap)

## What is Swing?

**Swing timing** is what makes electro swing *swing*! Instead of playing straight eighth notes:
```
Straight:  |1 & 2 & 3 & 4 &|  (equal spacing)
           ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓

Swing:     |1   & 2   & 3   & 4   &|  (uneven spacing - triplet feel)
           ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
           on OFF on OFF...
```

These patches use **swing_ratio: 0.66** which creates a classic **triplet swing** or **2:1 ratio**:
- **On-beats** (steps 0,2,4,6...): Play at regular time, slightly rushed
- **Off-beats** (steps 1,3,5,7...): Play LATE, creating the shuffle
- The ratio of 0.66 ≈ 2/3, meaning off-beats land on the third triplet

This is the classic jazz/swing feel that Parov Stelar uses throughout his music!

## Patches

### 1. **01_intro.json** (16 bars) - "Melodic Entry"
- **Energy**: Low → Building
- **Character**: High lead melody floating over sparse bass foundation
- **Bass Role**: Simple bass on-grid (C, G) + delicate high lead melody off-grid
- **Drums**: Minimal swing, introducing claps and tom fills gradually
- **Use**: Track opener, establishing the melodic theme
- **Transitions to**: Any patch (especially 02_verse)

### 2. **02_verse.json** (32 bars) - "Walking Groove"
- **Energy**: Medium
- **Character**: Walking bass alternates with mid/high octave lead phrases
- **Bass Role**: On-grid bass foundation + off-grid mid-range (1 octave) and high (2 octave) lead
- **Drums**: Syncopated with tom and clap accents, moderate swing
- **Use**: Main body sections, establishing the groove
- **Transitions to**: 03_breakdown, 04_chorus, 08_interlude

### 3. **03_breakdown.json** (32 bars) - "High Lead Tension"
- **Energy**: Medium-Low (Tension)
- **Character**: Ethereal very-high lead melody, sparse bass, building suspense
- **Bass Role**: Minimal bass on-grid + sustained high lead phrases creating space
- **Drums**: Stripped back but with strategic tom and clap build-ups
- **Use**: Pre-drop tension, filter sweeps, dramatic pause before peak
- **Transitions to**: 04_chorus, 07_peak_drop (for maximum impact)

### 4. **04_chorus.json** (48 bars) - "Polyrhythmic Peak"
- **Energy**: High
- **Character**: Dense bass/lead interplay with complex layered drums
- **Bass Role**: Strong bass pulse on-grid + constant high lead countermelody off-grid
- **Drums**: Maximum complexity - all elements (kick, snare, claps, toms, open+closed hats)
- **Use**: Main drops, dance floor peak moments, sustained high energy
- **Transitions to**: 02_verse, 05_bridge, 08_interlude

### 5. **05_bridge.json** (32 bars) - "Octave Jump Build"
- **Energy**: Medium-High (Building)
- **Character**: Bass literally jumps between octaves, dual-role playing technique
- **Bass Role**: **One instrument, two voices** - rapid octave jumps create bass+lead simultaneously
- **Drums**: Progressive build with increasing density, all percussion layers activate
- **Use**: Build anticipation, showcase the dual-role bass technique
- **Transitions to**: 07_peak_drop, 04_chorus

### 6. **06_outro.json** (16 bars) - "Lullaby Fade"
- **Energy**: Low (Fading)
- **Character**: Delicate high melody drifting over fading bass
- **Bass Role**: Sparse bass foundation + gentle high lead creating peaceful resolution
- **Drums**: Minimal, fading to silence
- **Use**: Track ending, graceful cooldown
- **Transitions to**: 01_intro (for seamless loop), or end

### 7. **07_peak_drop.json** (64 bars) - "Maximum Chaos"
- **Energy**: Maximum
- **Character**: Wild bass/lead counterpoint, maximum drum density, total mayhem
- **Bass Role**: **Aggressive octave jumps** - bass and high lead playing simultaneously on-grid
- **Drums**: **Everything firing** - kick, snare, claps, toms, open+closed hats in dense polyrhythms
- **Use**: Ultimate peak moment, longest sustained insanity, crowd goes wild
- **Transitions to**: 03_breakdown (dramatic drop), 06_outro

### 8. **08_interlude.json** (32 bars) - "Jazz Swing Solo"
- **Energy**: Medium
- **Character**: Playful high lead riff with swung drums, jazz club vibe
- **Bass Role**: Jazz walking bass + improvised-sounding high lead melody
- **Drums**: Swung hi-hats, relaxed claps, jazzy tom fills
- **Use**: Mid-track refresh, palate cleanser, ear candy break
- **Transitions to**: 02_verse, 04_chorus, 05_bridge

## Musical Elements

### Bass Pattern (C minor pentatonic scale)
The bass instrument plays **dual roles** throughout these patches:

**Bass Range (Low octave):**
- Root: C (MIDI 36)
- D (MIDI 38)
- E (MIDI 40)
- F (MIDI 41)
- G (MIDI 43)

**Lead Range (Mid octave - add 12 semitones):**
- C (MIDI 48)
- D (MIDI 50)
- E (MIDI 52)
- F (MIDI 53)
- G (MIDI 55)

**Lead Range (High octave - add 24 semitones):**
- C (MIDI 60)
- D (MIDI 62)
- E (MIDI 64)
- F (MIDI 65)
- G (MIDI 67)

### Dual-Role Bass Technique
- **On-grid notes**: Bass foundation hits on strong beats (kicks)
- **Off-grid notes**: Lead melody fills gaps between bass notes
- **Octave jumps**: Same instrument plays both bass and lead in same pattern
- Creates rich polyrhythmic texture with ONE instrument!

### Drum Kit (Roland T-8)
- **Kick (36)**: Four-on-floor foundation with swing variations
- **Snare (38)**: Backbeat on 2 and 4, varying velocities
- **Closed Hi-hat (42)**: Swing eighths pattern, main groove texture
- **Open Hi-hat (46)**: Accent points, fills, and energy peaks
- **Tom (47)**: Transitional fills, build-ups, and drum breaks
- **Clap (50)**: Swing accent, additional rhythmic layer, crowd energy

## Live Performance Suggestions

### Example Track Flow 1 (Progressive build)
```
01_intro → 02_verse → 04_chorus → 05_bridge → 07_peak_drop → 06_outro
```

### Example Track Flow 2 (With breakdown)
```
01_intro → 02_verse → 03_breakdown → 04_chorus → 08_interlude → 04_chorus → 06_outro
```

### Example Track Flow 3 (Maximum energy)
```
02_verse → 04_chorus → 05_bridge → 07_peak_drop → 03_breakdown → 07_peak_drop → 06_outro
```

### Live Tweaking Tips

**During Low Energy Sections (01, 03, 06):**
- Filter sweeps on bass to bring out high lead melody
- Reverb/delay on the high notes for ethereal effect
- Subtle tempo rides (±2-3 BPM)
- Mute kick for extra-sparse moments

**During High Energy Sections (04, 07):**
- Push the bass distortion/drive
- Hi-hat velocity variations for swing feel
- Snare/clap accent variations
- Drop tom/clap layers in/out on the fly
- Filter resonance sweeps on the lead range

**Creative Bass/Lead Manipulation:**
- **Filter sweeps** will affect both bass and lead (they're the same instrument!)
- Low-pass filter closed = focus on bass foundation
- High-pass filter = brings out the lead melody
- Resonance peaks can emphasize different octaves
- Envelope/decay tweaks change the character of both voices

**Transitions:**
- All patches end on bar boundaries
- Bass patterns resolve to C (root) in both octaves
- Drum patterns complete their 16-step cycle
- Safe to switch on any bar division (4, 8, 16, etc.)
- Lead melodies designed to fade naturally into next patch

## Keyboard Mapping
Once loaded, patches will map to keys q-m:
- q = 01_intro
- w = 02_verse
- e = 03_breakdown
- r = 04_chorus
- t = 05_bridge
- y = 06_outro
- u = 07_peak_drop
- i = 08_interlude

## Technical Notes
- **BPM**: All patches are 125 BPM (fixed)
- **Swing Ratio**: 0.66 (triplet swing / 2:1 ratio) - true shuffle feel
- **Length**: 16, 32, 48, or 64 bars
- **Pattern Length**: 16 steps per cycle (standard for T-8)
- **Key**: C minor pentatonic (club-friendly)
- **Style**: Electro swing with vintage jazz feel over 4/4 house beats
- **Timing**: Uneven eighth notes create authentic swing groove

### Understanding Swing Ratio Values
- **0.0**: Straight timing (no swing, like house/techno)
- **0.5**: Subtle swing (light shuffle)
- **0.66**: Classic triplet swing (2:1 ratio) ← **OUR PATCHES**
- **0.75**: Heavy swing (almost dotted)
- **1.0**: Extreme swing (maximum delay)

The 0.66 ratio means off-beats land exactly on the third part of a triplet, creating that classic jazz/swing bounce that defines the genre!

## Performance Strategy
1. **Start Simple**: Begin with 01_intro to establish the melodic theme
2. **Build Gradually**: Move through 02_verse before hitting 04_chorus
3. **Create Dynamics**: Use 03_breakdown before big drops for maximum impact
4. **Add Variation**: Use 08_interlude to refresh ears mid-set
5. **Peak Wisely**: Save 07_peak_drop for ultimate climax moments (64 bars!)
6. **Showcase Technique**: Use 05_bridge to highlight the octave-jump bass/lead trick
7. **End Gracefully**: Use 06_outro or fade from 01_intro

## What Makes These Patches Special

**The "One Instrument, Two Voices" Concept:**
Instead of traditional bass-only patterns, these patches use the Roland T-8's bass synth to play BOTH bass and lead simultaneously through clever octave usage:

- **Traditional approach**: Bass plays root notes only
- **These patches**: Bass plays root notes AND melodic lead lines in higher octaves
- **Result**: Fuller, richer sound from a single voice

**When you tweak the bass knobs, you're affecting BOTH the bass line and the lead melody** - this creates incredibly dynamic sound design possibilities during your live performance!

**Drum Complexity:**
- Simple patches (01, 06): 1-2 drum hits per step
- Medium patches (02, 03, 08): 2-3 drum hits per step with variation
- Complex patches (04, 05): 3-4 drum hits per step, polyrhythmic
- Maximum chaos (07): 4-5 drum hits per step, every element firing

Remember: These patches are designed to loop seamlessly, so you can stay on any patch as long as needed while tweaking knobs and building energy! The dual-role bass technique means filter sweeps, resonance changes, and envelope tweaks will create continuous variation even when looping.
