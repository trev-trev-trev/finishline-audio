# PRIORITY CORRECTION

**Date**: 2026-02-22 19:30 UTC

---

## CRITICAL CORRECTION: Streaming Standards

**Previous (INCORRECT)**:
- Target: -8 LUFS = "Spotify ceiling"
- Peak: -6 dBFS sample peak = "streaming spec"
- Strategy: Limiter gain to max for loudness

**Corrected (Official Spotify documentation)**:
- **Spotify official**: -14 LUFS integrated, -1 dBTP true peak
- **Commercial releases**: -9 LUFS, -2 dBTP (what most music targets)
- **True peak (dBTP)**: Required (4x oversampling, codec safety)
- **Strategy**: Compression → Saturation → Limiting (3-stage processing)
- **Diminishing returns**: Stop limiter when < 0.2 LU improvement

**See**: `docs/reference/STREAMING_STANDARDS.md` for official platform specs

---

## RIGHT NOW (User Action Required)

**User feedback**: "Super quiet, can barely hear it"

**Solution**: Run `flaas master-consensus --mode loud_preview`

**What was corrected**:
1. **Mode-based targets** (streaming_safe vs loud_preview vs headroom)
2. **Saturator support** (optional, recommended for RMS boost)
3. **True peak measurement** (dBTP via 4x oversampling)
4. **Diminishing returns detection** (stops pushing limiter when ineffective)
5. **Adaptive algorithm** (prioritizes Saturator/compression over extreme limiter gain)

**Command**:
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

# Add Saturator to Master chain in Ableton (if not already present)
# Chain order: Utility → EQ → Glue Compressor → Saturator → Limiter

flaas master-consensus --mode loud_preview
```

**Expected output**: `output/master_loud_preview.wav` (LOUD, full, smooth)

**Checklist**: See `HUMAN_ACTIONS_REQUIRED.md` for complete pre-run setup

---

## IMPLEMENTATION STATUS

### ✅ COMPLETE (All Code Implemented)

**1. Smoke Tests (Three Lanes)**:
- `make smoke`: 7s, 8 tests (read-only)
- `make write-fast`: 9s, 4 tests (dev gate)
- `make write`: 39s, 13 tests (commit gate, includes plugin test)
- Exit codes: 0 (pass), 10 (skip), 20 (read failure), 30 (write failure)

**2. Master Track Control**:
- `MASTER_TRACK_ID = -1000` (shared constant)
- Dynamic Utility device resolution (case-insensitive)
- `flaas plan-gain`, `apply`, `verify` all use master track correctly

**3. Export Loop (CORRECTED)**:
- ✅ macOS UI automation via AppleScript (Cmd+Shift+R → keystrokes)
- ✅ File stabilization wait (size + mtime)
- ✅ Audio verification (LUFS, sample peak, **true peak dBTP**)
- ✅ JSONL logging
- ⚠️ Master fader (manual pre-run check, no OSC endpoint)

**4. Master Consensus Generator (CORRECTED)**:
- ✅ Mode-based targets (streaming_safe, loud_preview, headroom)
- ✅ Saturator support (optional, recommended)
- ✅ True peak measurement (dBTP, 4x oversampling)
- ✅ Diminishing returns detection
- ✅ Adaptive algorithm (compression + saturation, not just limiter)
- ✅ Up to 15 iterations
- Output: `output/master_{mode}.wav`, `output/master_{mode}.jsonl`

---

## NEXT ACTIONS

**IMMEDIATE (User)**:
1. Add **Saturator** to Master chain (if missing): `Glue → Saturator → Limiter`
2. Verify Master fader = 0.0 dB
3. Run: `flaas master-consensus --mode loud_preview`
4. Listen to `output/master_loud_preview.wav`
5. Paste results to chat

**AFTER CONSENSUS MASTER**:
- Close loop on loudness optimization
- Begin systematic control discovery (unblocked)

---

## CRITICAL FACTS

### Streaming Standards (Official)
- **Spotify**: -14 LUFS, -1 dBTP (official spec)
- **Apple Music**: -16 LUFS, -1 dBTP
- **Commercial releases**: -9 LUFS, -2 dBTP (competitive)
- **True peak (dBTP)**: Required for codec safety

### Master Chain Position
- **Master fader**: POST-device chain (after Limiter)
- **Implication**: Boosting fader defeats limiter ceiling
- **Rule**: Must remain at 0.0 dB for predictable control

### Loudness Strategy
1. Compression (Glue) - Control dynamics, raise RMS
2. Saturation (Saturator) - Soft clip, raise RMS efficiently
3. Limiting (Limiter) - Catch peaks, final safety
4. **Limiter alone is insufficient** (observed in experiments)

### Track Indexing
- Regular: 0, 1, 2, ...
- Returns: -1, -2, -3, ...
- **Master: -1000**

---

## COMMANDS

```bash
# Master consensus (CORRECTED)
flaas master-consensus --mode loud_preview     # -9 LUFS, -2 dBTP (default, LOUD)
flaas master-consensus --mode streaming_safe   # -14 LUFS, -1 dBTP (official Spotify)
flaas master-consensus --mode headroom         # -10 LUFS, -6 dBFS (internal)

# Audio verification
flaas verify-audio <wav>  # Now shows true peak (dBTP)

# Smoke tests
make smoke       # 7s, read-only
make write-fast  # 9s, dev gate
make write       # 39s, commit gate
```

---

**Single source of truth for operational state. No redundant documentation.**
