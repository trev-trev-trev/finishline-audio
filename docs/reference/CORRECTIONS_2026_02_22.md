# Corrections Summary: 2026-02-22

**Trigger**: User/ChatGPT feedback on initial `master-consensus` implementation

---

## Technical Errors Corrected

### 1. Spotify "Ceiling" Misconception ❌ → ✅

**INCORRECT (previous)**:
- "-8 LUFS is Spotify ceiling"
- "Target maximum competitive loudness"

**CORRECTED**:
- **Spotify official recommendation**: -14 LUFS integrated, -1 dBTP true peak
- **Spotify behavior**: Normalizes to -14 LUFS (turns down if louder, up if quieter)
- **Commercial releases**: Vary by genre (-8 to -12 LUFS typical, NOT a universal ceiling)
- **-14 LUFS is recommendation**, not hard delivery spec

**Source**: [Spotify for Artists - Loudness Normalization](https://artists.spotify.com/help/article/loudness-normalization)

---

### 2. Sample Peak vs True Peak ❌ → ✅

**INCORRECT (previous)**:
- Only measured sample peak (dBFS)
- Claimed "-6 dBFS is streaming spec"

**CORRECTED**:
- **True peak (dBTP) required** for streaming compliance
- True peak = oversampled peak (4x), detects inter-sample peaks
- Sample peak misses codec distortion risk (MP3, AAC)
- **-6 dBFS is internal safety**, not streaming spec
- Streaming specs use true peak: -1 dBTP (Spotify), -2 dBTP (louder masters)

**Implementation**: Added true peak measurement via scipy 4x oversampling (approximation, needs validation)

**See**: `docs/reference/TRUE_PEAK_VALIDATION.md` for validation methodology

---

### 3. Master Fader Boost Guidance ❌ → ✅

**INCORRECT (previous)**:
- Suggested "boost master fader +6 dB if still too quiet"

**CORRECTED**:
- Master fader is **POST-device chain** (after Limiter)
- Boosting defeats limiter ceiling (observed empirically in experiments)
- **Must remain at 0.0 dB** for predictable control

**Fix**: Removed manual boost guidance, added pre-flight check to verify fader

---

### 4. Limiter-Only Strategy ❌ → ✅

**INCORRECT (previous)**:
- Primary lever: "Limiter gain to max"
- Expected linear LUFS increase with limiter gain

**CORRECTED**:
- **Limiter gain has diminishing returns** (observed in experiments)
- When limiter is working hard, increasing gain mostly adds distortion, not LUFS
- **Better strategy**: 3-stage processing
  1. Compression (Glue) - Control dynamics, raise RMS
  2. Saturation (Saturator) - Soft clip, efficient RMS boost
  3. Limiting (Limiter) - Final peak catching

**Implementation**: Added Saturator support, diminishing returns detection (< 0.2 LU improvement triggers strategy switch)

---

### 5. Mode Conflation ❌ → ✅

**INCORRECT (previous)**:
- Single target (-8 LUFS, -6 dBFS)
- Claimed "universal competitive loudness"

**CORRECTED**:
- **3 distinct modes**:
  - `streaming_safe`: -14 LUFS, -1 dBTP (official Spotify, default)
  - `loud_preview`: -9 LUFS, -2 dBTP (competitive commercial, genre-dependent)
  - `headroom`: -10 LUFS, -6 dBFS (internal safety)

**Default changed**: `streaming_safe` (conservative, avoids overcooking)

**Nuance**: Commercial loudness is genre-dependent (-8 to -12 LUFS), not a fixed target

---

## Implementation Changes

### Added

1. **True peak measurement** (`src/flaas/analyze.py`):
   - 4x oversampling via scipy (approximation)
   - `true_peak_dbtp` field in `AnalysisResult`
   - Display in `verify-audio` output

2. **Saturator support** (`src/flaas/master_consensus.py`):
   - Resolve Saturator device by name (optional)
   - Set Drive parameter (dB, soft clip)
   - More efficient RMS boost than extreme compression

3. **Diminishing returns detection**:
   - Track LUFS improvement per iteration
   - If < 0.2 LU improvement, stop increasing limiter gain
   - Switch to Saturator/compression instead

4. **Pre-flight checks** (`src/flaas/preflight.py`):
   - Verify master fader at 0.0 dB (OSC if available, user confirm if not)
   - Verify device order (Glue → Saturator → Limiter)
   - Fail fast on misconfiguration

5. **Mode-based targets**:
   - 3 modes with distinct parameters and targets
   - Output files named by mode (`master_{mode}.wav`)
   - CLI: `flaas master-consensus --mode <name>`

6. **Validation framework** (`tests/validate_true_peak.py`):
   - Generate test signals (sine sweeps)
   - Compare against reference meter
   - Methodology documented

### Modified

1. **Default mode**: Changed from `loud_preview` to `streaming_safe`
2. **Documentation**: Corrected all claims about Spotify specs, loudness targets, peak types
3. **Logging**: Added mode, targets, true_peak_dbtp to JSONL
4. **CLI help**: Reflects conservative default

---

## Documentation Added

1. `docs/reference/STREAMING_STANDARDS.md` - Official platform specs
2. `docs/reference/TRUE_PEAK_VALIDATION.md` - Validation status and methodology
3. `docs/reference/CORRECTIONS_2026_02_22.md` (this file) - Summary of corrections
4. `tests/validate_true_peak.py` - Validation test script

---

## Documentation Updated

1. `STATE.md` - Corrected targets, added true peak facts
2. `QUICKSTART.md` - Conservative default, Saturator requirement
3. `PRIORITY.md` - Reflected corrected understanding
4. `HUMAN_ACTIONS_REQUIRED.md` - Removed incorrect boost options, added modes

---

## Key Learnings

1. **Don't conflate recommendations with specs**: Spotify's -14 LUFS is target behavior, not delivery requirement
2. **True peak is not trivial**: Proper implementation requires ITU-R BS.1770-4 algorithm, not just oversampling
3. **Genre matters**: Commercial loudness varies (-8 to -12 LUFS), can't claim universal target
4. **Limiter is not magic**: Has diminishing returns, needs compression/saturation before it
5. **Fail fast on invariants**: Pre-flight checks prevent silent failure modes

---

## Validation Status

**True peak**: ⚠️ APPROXIMATION (scipy 4x resample, not full ITU-R BS.1770-4)

**Next step**: Run `tests/validate_true_peak.py` and compare against reference meter

**Tolerance**: ±0.5 dB acceptable for production use

---

## User's Original Feedback

> "It's super quiet, can barely hear it"

**Root cause**: Conservative LUFS target (-10.5, then -9.0) combined with insufficient RMS boost

**Solution**:
1. Use `loud_preview` mode (-9 LUFS, competitive commercial)
2. Add Saturator (efficient RMS boost)
3. Diminishing returns detection (stop overcooking limiter)
4. Adaptive algorithm (compression + saturation, not just limiting)

**Expected result**: LOUD, full, smooth (competitive with commercial releases)

---

**All technical corrections implemented and pushed** ✅
