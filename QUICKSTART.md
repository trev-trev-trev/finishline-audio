# QUICKSTART

**Repo**: `/Users/trev/Repos/finishline_audio_repo`

## Current Status

**Master consensus generator CORRECTED** ✅

**Addressing**: "Super quiet, can barely hear it"

**Solution**: Use `loud_preview` mode with Saturator for competitive commercial loudness

## NOW: Generate LOUD Master

**User reported**: "super quiet, can barely hear it"

**Solution**: Use `loud_preview` mode with Saturator for competitive commercial loudness

```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

# Add Saturator to Master chain in Ableton (before Limiter)
# Chain: Utility → EQ → Glue → Saturator → Limiter

flaas master-consensus --mode loud_preview  # -9 LUFS, -2 dBTP (competitive)
```

**Output**: `output/master_loud_preview.wav` (LOUD, full, smooth)

**Other modes**:
- `--mode streaming_safe`: -14 LUFS, -1 dBTP (official Spotify, quieter)
- `--mode headroom`: -10 LUFS, -6 dBFS (internal safety)

**See**: `docs/reference/STREAMING_STANDARDS.md` for official platform specs

---

## Key Corrections (Per User Feedback)

**Previous (INCORRECT)**:
- Target: -8 LUFS = "Spotify ceiling"
- Safety: -6 dBFS sample peak
- Strategy: Limiter gain to max

**Corrected (Official Spotify docs)**:
- **Spotify official spec**: -14 LUFS, -1 dBTP
- **Commercial releases**: -9 LUFS, -2 dBTP (what most music targets)
- **True peak (dBTP)**: Required for codec safety (not just sample peak)
- **Strategy**: Compression + Saturation + Limiting (3-stage, not just limiter)
- **Diminishing returns**: Stop pushing limiter when < 0.2 LU improvement

**Master fader position**: POST-chain (defeats limiter if boosted) ← Already documented/observed

---

## Key Files (Priority Order)

1. `STATE.md` - Current operational state
2. `HUMAN_ACTIONS_REQUIRED.md` - Run checklist
3. `docs/reference/STREAMING_STANDARDS.md` - Official specs (NEW)
4. `docs/reference/MASTERING_RECIPE.md` - Technical guide
5. `docs/reference/EXPORT_FINDINGS.md` - Experiment findings

---

## Commands

```bash
# Smoke tests
make smoke       # 7s, read-only
make write-fast  # 9s, dev gate
make write       # 39s, commit gate

# Audio verification
flaas verify-audio <wav>  # Check LUFS/peak vs targets

# Automated mastering (CORRECTED)
flaas master-consensus --mode loud_preview     # -9 LUFS (competitive, LOUD)
flaas master-consensus --mode streaming_safe   # -14 LUFS (official Spotify)
flaas master-consensus --mode headroom         # -10 LUFS (internal)
```

---

## macOS Permissions (One-Time Setup)

**Required for auto-export**:
- System Settings → Privacy & Security → Accessibility → Terminal ON
- System Settings → Privacy & Security → Automation → Terminal → System Events ON

---

## Pre-requisites (Before Running)

- Ableton Live running with project open
- Master fader = 0.0 dB (CRITICAL)
- Device chain: Utility → EQ → Glue → **Saturator** → Limiter (all ON)
- Export defaults: Rendered Track = Master, Normalize = OFF
- Loop/selection = 8 bars

---

**Ready to run**: `flaas master-consensus --mode loud_preview`
