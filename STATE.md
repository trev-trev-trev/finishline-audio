# STATE

**Updated**: 2026-02-22 18:50 UTC  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## CURRENT TASK

**IMMEDIATE BLOCKER**: Export crash prevents closed-loop audio iteration

**Real bottleneck**: Can't scale to 500 commands until `plan-gain → apply → export → verify-audio` loop works

**Next action**: In Ableton, disable ValhallaSpaceModulator + StudioVerse on track 41, attempt 4-8 bar export to `output/master_iter1.wav`

**After export succeeds**: `flaas verify-audio output/master_iter1.wav`

**Future work**: Systematic control discovery (see DISCOVERY.md, NEXT_CHAPTER.md)

---

## APPLIED STATE

**Master Track** (track_id=-1000):
- Utility gain: **-0.750 linear** (was -1.000, delta +0.250 applied, NOT reset)
- Devices: Utility(0), EQ Eight(1), Limiter(2)

**Track 41** "42-52 long chords":
- Devices: EQ Eight(0), ValhallaSpaceModulator(1), StudioVerse(2)

**Actions**: `data/actions/actions.json` contains last plan (delta +0.250)

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

**Execute Step 2 of export triage**: In Ableton, disable ValhallaSpaceModulator + StudioVerse, attempt 4-8 bar export.

---

**Single source of truth for operational state. No redundant documentation.**
