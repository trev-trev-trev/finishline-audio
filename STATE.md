# STATE

**Updated**: 2026-02-22 18:50 UTC  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## CURRENT TASK

**Fully automated batch runner READY** ✅

**Command**: `flaas experiment-run data/experiments/master_sweep.json`

**Latest result**: LUFS -13.59, Peak -6.00 (experiment #14: Glue + Limiter)

**Gap to target**: 3.09 LU (-13.59 → -10.50)

**Next action**: Run batch experiment (3 runs, fully automated on macOS)

**Automation status**: 
- ✅ Parameter control (Glue, Limiter) automated
- ✅ Export trigger automated (macOS UI automation via AppleScript)
- ✅ Verification automated (LUFS, peak)
- ✅ Logging automated (JSONL receipts)
- ⚠️ Master fader (manual pre-run check, no OSC endpoint)

**ROI**: 4-5x speedup (7 min vs 30 min for 10 experiments), zero clicks on macOS

**See**: 
- `docs/reference/EXPERIMENT_RUNNER_USAGE.md` - Usage guide
- `docs/reference/EXPORT_FINDINGS.md` - Triage findings (16 experiments)
- `docs/reference/AUTOMATION_ROADMAP.md` - Implementation phases

---

## APPLIED STATE

**Master Track** (track_id=-1000):
- **Device chain**: Glue Compressor → Limiter (validated)
- **Master fader**: 0.0 dB (critical for peak control)
- Limiter ceiling: -6.0 dB, gain: +24 dB (experiment #14)
- Glue settings: GR ~12 dB, Makeup varies

**Track 41** "42-52 long chords":
- Plugins bypassed during triage (ValhallaSpaceModulator, StudioVerse)

**Latest export**: `output/sanity_glue_gain24.wav`
- LUFS: -13.59 (target -10.50, gap 3.09 LU)
- Peak: -6.00 ✅

---

## CRITICAL FACTS

### Track Indexing (AbletonOSC)
- Regular: 0, 1, 2, ...
- Returns: -1, -2, -3, ...
- **Master: -1000** (NOT 0)

### Device Resolution
```python
# Response from /live/track/get/devices/name is: (track_id, name0, name1, ...)
names = list(response)[1:]  # Drop track_id
device_id = names.index("Utility")  # Case-insensitive
```

### Gain Adjustment
- **Clamp**: ±0.25 per iteration (prevents runaway)
- **Formula**: `delta = (target_lufs - measured_lufs) / 12.0`
- **Current file**: -19.41 LUFS (target -10.5) = 8.9 dB gap, -3.0 dBFS peak (limit -6.0)
- **Problem**: Too quiet AND too hot → need Limiter control before more gain

---

## COMMANDS

### Workflow
```bash
# 1. Plan
flaas plan-gain output/master.wav

# 2. Apply (already done, gain at -0.750)
flaas apply --actions data/actions/actions.json

# 3. Verify Ableton state
flaas verify  # Returns 0.125000 (current gain normalized)

# 4. Export from Ableton (BLOCKED - crash)
# Manual: 4-8 bars, disable plugins first

# 5. Check exported file
flaas verify-audio output/master_iter1.wav
```

### Smoke Tests
```bash
make smoke       # 7s, 8 tests (read-only)
make write-fast  # 9s, 4 tests (dev gate)
make write       # 39s, 13 tests (commit gate)
```

### Exit Codes
- 0: pass
- 10: skip only
- 20: read failure
- 30: write failure

---

## KEY COMMANDS

**Master control** (auto-resolves track=-1000, Utility device):
- `flaas verify` - Read current gain
- `flaas plan-gain <wav>` - Calculate delta
- `flaas apply --actions <json>` - Apply delta

**Device control**:
- `flaas device-set-safe-param <track> <device>` - Generic plugin write+revert test
- `flaas eq8-set <t> <d> --band N --param gain --value X` - EQ Eight
- `flaas limiter-set <t> <d> --param ceiling --value X` - Limiter

**Inspection**:
- `flaas ping --wait` - Test OSC
- `flaas scan` - Get all tracks/devices
- `flaas device-map <t> <d>` - Get device parameters
- `flaas remote-version` - Check AbletonOSC version match

---

## FILES MODIFIED (Uncommitted)

**Core fixes**:
- `src/flaas/targets.py` - Added MASTER_TRACK_ID=-1000, resolve_utility_device_id()
- `src/flaas/plan.py` - Uses shared resolver
- `src/flaas/apply.py` - Uses shared resolver
- `src/flaas/verify.py` - Uses shared resolver, optional params
- `src/flaas/cli.py` - Updated verify defaults, added device-set-safe-param

**Testing**:
- `src/flaas/device_set_safe_param.py` - NEW: Generic plugin test
- `scripts/run_smoke_tests.sh` - Three lanes, exit codes, plugin test
- `Makefile` - NEW: smoke/write-fast/write shortcuts

**Version**:
- `src/flaas/version.py` - NEW: FLAAS_VERSION, ABLETONOSC_VERSION_EXPECTED

---

## KNOWN ISSUES

**Export crash**: Third-party plugins (Valhalla/StudioVerse) hang render. Solution: Disable plugins, test 4-8 bars, re-enable one-by-one.

**Device queries**: Response format is `(track_id, name0, name1, ...)` - must skip first element.

**Fingerprint**: `apply` rejects if Live set changed since `plan-gain`.

---

## NEXT ACTION

**Generate ONE consensus master** (fully automated, zero clicks):

```bash
flaas master-consensus
```

**What it does**:
- ONE thoroughly optimized master (addresses "super quiet" issue)
- Target: **LUFS -9.0** (competitive streaming loudness, NOT -10.5)
- Up to 10 iterations with adaptive adjustments
- Aggressive starting params: GR 15-18 dB, Makeup 22 dB, Limiter gain 36 dB
- Auto-adjusts threshold, makeup, limiter gain dynamically
- Converges when LUFS within 0.3 LU of target, peak safe
- Output: `output/master_consensus.wav`
- Log: `output/master_consensus.jsonl`

**Goal**: Generate ONE high-quality, properly loud master from 8-bar loop

**After completion**:
```bash
ls -lh output/master_consensus.wav
cat output/master_consensus.jsonl | jq .
```

---

**Single source of truth for operational state. No redundant documentation.**
