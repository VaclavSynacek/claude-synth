# Roland T-8 MIDI Mapping Reference

This document contains the official MIDI note mapping for the Roland T-8 Beat Machine, as documented in the official Roland T-8 Owner's Manual (Version 1.02, Page 31).

## Official T-8 Rhythm Instrument Note Numbers

| Instrument    | Transmit (Tx) | Receive (Rx) | Notes |
|--------------|---------------|--------------|-------|
| BASS DRUM    | 36            | 35, 36       | Kick drum |
| SNARE DRUM   | 38            | 38, 40       | Snare drum |
| **HAND CLAP**| **50**        | **48, 50**   | **Clap sound** |
| **TOM**      | **47**        | **45, 47**   | **Tom sound** |
| CLOSED HIHAT | 42            | 42, 44       | Closed hi-hat |
| OPEN HIHAT   | 46            | 46           | Open hi-hat |

## Implementation in This Project

```python
DRUMS = {
    'kick': 36,      # T-8 Manual: Tx=36, Rx=35,36
    'snare': 38,     # T-8 Manual: Tx=38, Rx=38,40
    'closed_hh': 42, # T-8 Manual: Tx=42, Rx=42,44
    'tom_low': 45,   # T-8 Manual: TOM Rx=45,47
    'open_hh': 46,   # T-8 Manual: Tx=46, Rx=46
    'tom_mid': 47,   # T-8 Manual: TOM Tx=47, Rx=45,47
    'tom_high': 47,  # T-8 Manual: TOM Tx=47, Rx=45,47 (same as tom_mid)
    'clap': 50,      # T-8 Manual: HAND CLAP Tx=50, Rx=48,50
}
```

## Important Notes

1. **Clap vs General MIDI**: The T-8 uses MIDI note 50 for clap, NOT the General MIDI standard note 39.

2. **Tom Mapping**: The T-8 has a single TOM sound that responds to notes 45 and 47. This differs from General MIDI which typically has separate low/mid/high tom sounds.

3. **Transmit vs Receive**: 
   - **Tx (Transmit)**: The note the T-8 sends when you trigger the instrument
   - **Rx (Receive)**: The note(s) the T-8 responds to when receiving MIDI

4. **MIDI Channel**: Rhythm instruments use **Channel 10** (the standard GM drum channel).

## Common Mistakes

❌ **WRONG**: Using note 39 for clap (General MIDI standard)  
✅ **CORRECT**: Use note 50 for clap (T-8 specific)

❌ **WRONG**: Using note 50 for high tom  
✅ **CORRECT**: Use note 50 for clap, note 47 for tom

## Verification

Test patches are provided to verify correct mapping:
- `test_6_clap_only.json` - Should play CLAP sounds (note 50)
- `test_7_tom_only.json` - Should play TOM sounds (notes 45, 47)

## Reference

Source: Roland T-8 Owner's Manual (Version 1.02), Page 31 - MIDI Implementation Chart
