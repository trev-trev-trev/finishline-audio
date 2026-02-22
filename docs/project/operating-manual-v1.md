# FLAAS Operating Manual v1

**Single unified reference for daily FLAAS development and operation.**

**Version**: 1.0  
**Date**: 2026-02-22  
**Status**: Executable

---

## 0. Executive Snapshot

**Current system state** (terminal-verifiable):

1. **OSC connectivity**: Bidirectional communication established (`flaas ping --wait` → `ok: ('ok',)`)
2. **Surface area mapped**: 9 endpoints validated (health, song, track, device params)
3. **One actuator operational**: Utility Gain on track 0 device 0 (param 9)
4. **Closed-loop control**: analyze → plan → apply workflow with fingerprint enforcement
5. **Safety mechanisms**: Delta clamps (±0.25), max gain stop (0.99 norm), fingerprint validation
6. **Audit trail**: Schema versioning, timestamps, fingerprints in all artifacts
7. **Manual export loop**: User exports from Ableton, runs `verify-audio`, iterates via `loop`
8. **Terminal-driven**: Every operation validated by single-command probes
9. **Zero speculation**: All behaviors documented with exact commands + expected outputs
10. **Next bottleneck**: Automated export (requires `/live/song/export/*` endpoint discovery)

**What this manual does**:
- Provides single source of truth map (Section 1)
- Defines golden path with exact commands (Section 2)
- Formalizes surface area expansion process (Section 3)
- Documents audio intelligence capabilities + roadmap (Section 4)
- Specifies non-negotiable safety gates (Section 5)
- Integrates engineering notebook updates (Section 6)
- Operationalizes workflow FSM (Section 7)
- Lists next 12 atomic tasks + THE next task (Section 8)

---

## 1. Single Source of Truth Map

**Which document governs what + update rules**

| Domain | Primary Doc | Update Trigger | Validation Command | Cross-References |
|--------|-------------|----------------|-------------------|------------------|
| **Product vision** | `project/spec-v1.md` | Major milestones, capability additions | Manual review | `README.md`, `mvp_remaining.md` |
| **API catalog** | `reference/ENGINEERING_NOTEBOOK.md` | Any function/module added or signature changed | Regen script (manual for now) | `operating-manual-v1.md` (this doc) |
| **Workflow FSM** | `workflow/execution-system.md` | FSM state or error category added | Gate G1-G5 pass | `workflow/protocol.md` |
| **Command reference** | `workflow/terminal-cheatsheet.md` | CLI command added/changed | `flaas --help` | `README.md` Commands section |
| **Current state** | `reference/FINISHLINE_PROGRESS_INDEX.md` | Step completed (major milestone) | Inspect last step receipt | `finishline_context_state.json` |
| **Unique line ledger** | `reference/unique-lines/INDEX.md` | Code added/changed in `src/flaas/` | `python3 scripts/generate_unique_lines.py` | `ENGINEERING_NOTEBOOK.md` Section 12 |
| **Surface area registry** | `project/spec-v1.md` Section 5 | OSC endpoint discovered or validated | Discovery probe passes | `ENGINEERING_NOTEBOOK.md` Section 3 |
| **Stability gates** | `workflow/execution-system.md` Section E | Safety invariant added | Run gate sequence | `operating-manual-v1.md` Section 5 |
| **Next tasks** | `project/mvp_remaining.md` + this doc Section 8 | MVP block completed or reprioritized | Task completion receipt | `operating-manual-v1.md` |

### Update Rules (Operational)

**Rule 1: Engineering Notebook Update**
- **Trigger**: Any function/class added or signature changed
- **Process**:
  1. Update docstring in source code (signature, inputs, outputs, failure modes)
  2. Add entry to Section 2 (API Catalog) with all required fields:
     - Fully-qualified name
     - Signature
     - What it does (1-3 bullets)
     - Inputs/outputs + invariants
     - Side effects
     - Failure modes
     - Example
     - Where used
     - How to validate
  3. Regenerate unique line ledger: `python3 scripts/generate_unique_lines.py`
  4. Commit: `git add docs/reference/ && git commit -m "docs: update engineering notebook for [function]"`

**Rule 2: Terminal Cheatsheet Update**
- **Trigger**: CLI command added, changed, or removed
- **Process**:
  1. Update Command Reference table (command, purpose, reads, writes, exit codes)
  2. Update Golden Path if new command is part of core workflow
  3. Add troubleshooting entry if new failure mode discovered
  4. Validate: `flaas [new_command] --help`
  5. Commit: `git add docs/workflow/terminal-cheatsheet.md && git commit -m "docs: add [command] to cheatsheet"`

**Rule 3: Spec Update**
- **Trigger**: Major capability shipped or MVP definition changes
- **Process**:
  1. Update Surface Area Roadmap (move from Tier 2 → Tier 1 if validated)
  2. Update Audio Intelligence Roadmap if new analyzer added
  3. Update Definitions of Done if acceptance test added
  4. No command validation (conceptual document)
  5. Commit: `git add docs/project/spec-v1.md && git commit -m "docs: update spec for [capability]"`

**Rule 4: Execution System Update**
- **Trigger**: New error category, stability gate, or FSM state added
- **Process**:
  1. Add error category with regex patterns + probe sequence
  2. Update decision algorithm with new pattern matches
  3. If new gate: Define commands + expected outputs + pass criteria
  4. Validate new gate: Run full gate sequence, verify expected outputs
  5. Commit: `git add docs/workflow/execution-system.md && git commit -m "docs: add [gate/category]"`

**Rule 5: Cross-Reference Integrity**
- **Trigger**: Any doc update
- **Process**:
  1. Check all docs in update rule table above
  2. Update cross-links if section numbers or filenames changed
  3. Run link check: `grep -r "docs/" docs/*.md | grep -v "Binary" | grep "\.md" | sort -u`
  4. Commit link fixes separately: `git commit -m "docs: fix cross-references"`

---

## 2. Golden Path (Terminal-First End-to-End)

**One command per step. Full validation. Single-command recovery probes.**

### Pre-Flight (Environment)

**Step 0.1: Verify Python**
```bash
python3 --version
```
**Expected**: `Python 3.11.x` or higher  
**Pass**: Version ≥ 3.11  
**Fail**: Upgrade Python → `brew install python@3.11`

---

**Step 0.2: Activate venv**
```bash
source .venv/bin/activate
```
**Expected**: Prompt changes to `(.venv)`  
**Pass**: Prompt shows venv  
**Fail**: Create venv → `make dev && source .venv/bin/activate`

---

**Step 0.3: Verify package installed**
```bash
flaas --version
```
**Expected**: `0.0.2` (current version)  
**Pass**: Prints version  
**Fail probe**: `pip show flaas`  
**Fix**: `pip install -e .`

---

### Discovery Path (Map Ableton Surface)

**Step 1.1: OSC health check**
```bash
flaas ping --wait
```
**Expected**: `ok: ('ok',)`  
**Artifact**: None  
**Pass**: Reply received within 2s  
**Fail probe**: `ps aux | grep -i "ableton live"`  
**Fix**: Start Ableton, verify AbletonOSC loaded in Control Surface preferences

---

**Step 1.2: Scan Live set structure**
```bash
flaas scan
```
**Expected**: `data/caches/model_cache.json`  
**Artifact**: `model_cache.json` with tracks, devices, fingerprint  
**Pass**: File written, `ok: true`, `num_tracks > 0`  
**Fail probe**: `cat data/caches/model_cache.json | jq '{ok, note}'`  
**Fix**: Check `note` field for error details

---

**Step 1.3: Validate scan output**
```bash
cat data/caches/model_cache.json | jq '{ok, num_tracks, fingerprint, master: .tracks[0]}'
```
**Expected**:
```json
{
  "ok": true,
  "num_tracks": 1,
  "fingerprint": "a1b2c3...",
  "master": {
    "track_id": 0,
    "name": "Master",
    "num_devices": 1,
    "devices": [{"index": 0, "name": "Utility", "class_name": "StereoGain"}]
  }
}
```
**Pass**: Track 0 exists, device 0 is Utility (StereoGain)  
**Fail probe**: `cat data/caches/model_cache.json | jq '.tracks[0].devices'`  
**Fix**: Add Utility to Master track device slot 0 in Ableton

---

**Step 1.4: Query parameter names**
```bash
python3 -c "from flaas.osc_rpc import *; resp = request_once(OscTarget(), '/live/device/get/parameters/name', [0,0]); print('\n'.join(f'{i}: {n}' for i,n in enumerate(resp[2:])))"
```
**Expected**:
```
0: Device On
1: Left/Right
...
9: Gain
...
```
**Pass**: Param 9 is "Gain"  
**Fail probe**: Re-run with different device_id  
**Fix**: Verify device 0 is Utility

---

**Step 1.5: Query parameter range**
```bash
python3 -c "from flaas.param_map import get_param_range; pr = get_param_range(0,0,9); print(f'min={pr.min}, max={pr.max}')"
```
**Expected**: `min=-1.0, max=1.0` (or similar linear range)  
**Pass**: Returns ParamRange  
**Fail probe**: `flaas ping --wait` (verify OSC still alive)  
**Fix**: Check track_id/device_id/param_id correct

---

### Shipping Path (User-Facing Workflow)

**Step 2.1: Generate test audio**
```bash
python3 - <<'PY'
import numpy as np, soundfile as sf, os
os.makedirs("input", exist_ok=True)
sr = 48000
t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
x = 0.2*np.sin(2*np.pi*440*t)
sf.write("input/test.wav", x, sr)
print(f"Generated: {x.shape[0]} samples, peak={np.max(np.abs(x)):.4f}")
PY
```
**Expected**: `Generated: 96000 samples, peak=0.2000`  
**Artifact**: `input/test.wav` (96000 samples, 2s, 48kHz, mono sine)  
**Pass**: File created  
**Fail probe**: `ls -la input/`  
**Fix**: `mkdir -p input` then re-run

---

**Step 2.2: Analyze audio**
```bash
flaas analyze input/test.wav
```
**Expected**: `data/reports/analysis.json`  
**Artifact**: JSON with peak=-13.98, lufs_i≈-17.7  
**Pass**: File written  
**Fail probe**: `cat data/reports/analysis.json`  
**Fix**: Check error in JSON `note` field

---

**Step 2.3: Check compliance**
```bash
flaas check input/test.wav
```
**Expected**: `data/reports/check.json`  
**Artifact**: JSON with `pass_lufs: false` (test file is too quiet)  
**Pass**: File written, flags computed  
**Fail probe**: `python3 -c "from flaas.check import check_wav; print(check_wav('input/test.wav'))"`  
**Fix**: Check analyze.py if analysis fails

---

**Step 2.4: Plan gain adjustment**
```bash
flaas plan-gain input/test.wav
```
**Expected**:
```
CUR_LINEAR: 0.000  DELTA: 0.XXX
data/actions/actions.json
```
**Artifact**: `actions.json` with delta, fingerprint, schema v1.0  
**Pass**: File written, delta printed  
**Fail probe**: `cat data/actions/actions.json | jq .`  
**Fix**: Check LUFS error calculation if delta is wrong

---

**Step 2.5: Preview actions (dry-run)**
```bash
flaas apply --dry
```
**Expected**: `DRY_RUN: MASTER :: Utility.Gain += 0.XXX`  
**Artifact**: None (read-only)  
**Pass**: Action previewed  
**Fail probe**: `cat data/actions/actions.json` (verify actions exist)  
**Fix**: Re-run plan-gain if actions missing

---

**Step 2.6: Apply actions (real OSC set)**
```bash
flaas apply
```
**Expected**: `APPLIED: Utility.Gain 0.000 -> 0.XXX (norm 0.500->0.XXX)`  
**Artifact**: Ableton Utility Gain parameter changed  
**Pass**: APPLIED message printed  
**Fail probe**: `flaas verify` (check current gain)  
**Fail (fingerprint)**: `flaas scan && flaas plan-gain input/test.wav` (regenerate with new fingerprint)

---

**Step 2.7: Verify parameter change**
```bash
flaas verify
```
**Expected**: `0.XXX` (normalized value > 0.5 if positive delta applied)  
**Artifact**: None (read-only)  
**Pass**: Prints normalized value matching expected  
**Fail probe**: Manual check in Ableton (Utility Gain knob position)  
**Fix**: Re-apply if readback doesn't match

---

**Step 2.8: Loop automation (analyze → plan → apply)**
```bash
flaas reset  # Start from known state
flaas loop input/test.wav --dry  # Preview first
```
**Expected**:
```
MEASURE: LUFS=-17.72 peak_dBFS=-13.98
CUR_LINEAR: 0.000  DELTA: 0.XXX
DRY_RUN: MASTER :: Utility.Gain += 0.XXX
DONE: planned (dry-run, no OSC)
```
**Pass**: All stages execute, prints DONE  
**Fail probe**: Re-run individual commands (`analyze`, `plan-gain`, `apply --dry`)  
**Fix**: Check which stage fails

---

**Step 2.9: Loop (real application)**
```bash
flaas loop input/test.wav
```
**Expected**:
```
MEASURE: LUFS=-17.72 peak_dBFS=-13.98
CUR_LINEAR: 0.000  DELTA: 0.XXX
APPLIED: Utility.Gain 0.000 -> 0.XXX (norm 0.500->0.XXX)
DONE: planned+applied (norm=0.XXX)
```
**Artifact**: Utility Gain changed in Ableton  
**Pass**: DONE printed, new norm displayed  
**Fail probe**: `flaas verify` (check final state)  
**Fix**: Check individual stages

---

**Step 2.10: Manual export from Ableton**
```bash
flaas export-guide
```
**Expected**: Prints export settings checklist  
**Artifact**: None (instruction only)  
**Pass**: Settings displayed  
**User action**: Export Master track to `output/master.wav` using these settings

---

**Step 2.11: Verify exported audio**
```bash
flaas verify-audio output/master.wav
```
**Expected**:
```
FILE: output/master.wav
LUFS: -10.52 (target -10.50)  pass=True
PEAK: -6.12 dBFS (limit -6.00) pass=False
FAIL
```
**Artifact**: None (read-only check)  
**Pass**: Exit 0 with `PASS` (compliance achieved)  
**Fail**: Exit 1 with `FAIL` (needs more iteration)  
**Next**: Repeat from Step 2.10 (export → verify → loop)

---

**Step 2.12: Reset to center (cleanup)**
```bash
flaas reset
flaas verify
```
**Expected**: `sent` then `0.500`  
**Pass**: Utility Gain back to center  
**Fail probe**: Manual check in Ableton  
**Fix**: `flaas util-gain-norm 0 0 0.5`

---

### Golden Path Summary (Command Chain)

**Full workflow** (copy-paste for testing):
```bash
# Pre-flight
flaas ping --wait

# Scan
flaas scan
cat data/caches/model_cache.json | jq '{ok, num_tracks, fingerprint}'

# Analyze
flaas analyze input/test.wav
cat data/reports/analysis.json | jq '{lufs_i, peak_dbfs}'

# Check
flaas check input/test.wav
cat data/reports/check.json | jq '{pass_lufs, pass_peak}'

# Plan
flaas plan-gain input/test.wav
cat data/actions/actions.json | jq '{schema_version, live_fingerprint, actions}'

# Apply (dry)
flaas apply --dry

# Apply (real)
flaas apply

# Verify
flaas verify

# Or: Loop (combines analyze+plan+apply)
flaas reset
flaas loop input/test.wav --dry  # Preview
flaas loop input/test.wav        # Execute
flaas verify

# Export + final check (manual)
flaas export-guide  # Follow instructions in Ableton
flaas verify-audio output/master.wav  # Should print PASS
```

**Expected runtime**: ~5-10 seconds (excluding manual export)

---

## 3. Surface Area Expansion Program

**Formal registry + validation protocol + next 20 expansions**

### Registry Format

**For each validated endpoint**, maintain:

| Field | Type | Example | Update Rule |
|-------|------|---------|-------------|
| Endpoint path | string | `/live/device/get/parameters/name` | Discovered in probe |
| Request format | tuple | `(track_id: int, device_id: int)` | Tested in terminal |
| Response format | tuple | `(track_id, device_id, name0, name1, ...)` | Observed in output |
| Quirks | list[str] | ["First 2 args echoed back", "Names start at index 2"] | Documented after debugging |
| Wrapper function | str | `flaas.param_map.get_param_names` (if exists) | Created after validation |
| CLI command | str | `flaas scan --verbose` (if exists) | Added if user-facing |
| Validation command | str | `python3 -c "from flaas.osc_rpc import *; print(request_once(...))"` | Single-command probe |
| Status | enum | VALIDATED / HYPOTHESIZED / BROKEN | Updated after probe |

### Current Registry (Tier 1 - Validated)

**Health Check**
- **Endpoint**: `/live/test`
- **Request**: `"ok"` (string, not int)
- **Response**: `("ok",)` (tuple with one string)
- **Quirks**: Fire-and-forget mode doesn't expect reply; RPC mode does
- **Wrapper**: `osc.send_ping`, `osc_rpc.request_once`
- **CLI**: `flaas ping [--wait]`
- **Validation**: `flaas ping --wait` → `ok: ('ok',)`
- **Status**: ✅ VALIDATED

**Song Structure**
- **Endpoint**: `/live/song/get/num_tracks`
- **Request**: `None` or `[]`
- **Response**: `(num_tracks: int,)`
- **Quirks**: None
- **Wrapper**: `scan.scan_live` (internal)
- **CLI**: `flaas scan`
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/get/num_tracks', None))"`
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/song/get/track_names`
- **Request**: `[]`
- **Response**: `(name0, name1, ..., nameN)`
- **Quirks**: Returns all track names (no pagination)
- **Wrapper**: `scan.scan_live`
- **CLI**: `flaas scan`
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/get/track_names', []))"`
- **Status**: ✅ VALIDATED

**Track Structure**
- **Endpoint**: `/live/track/get/num_devices`
- **Request**: `[track_id: int]`
- **Response**: `(track_id, num_devices: int)`
- **Quirks**: Echoes track_id back as first arg
- **Wrapper**: `scan.scan_live`
- **CLI**: `flaas scan`
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/num_devices', [0]))"`
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/track/get/devices/name`
- **Request**: `[track_id: int]`
- **Response**: `(track_id, name0, name1, ..., nameN)`
- **Quirks**: First arg is track_id echo, device names start at index 1
- **Wrapper**: `scan.scan_live`
- **CLI**: `flaas scan`
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/devices/name', [0]))"`
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/track/get/devices/class_name`
- **Request**: `[track_id: int]`
- **Response**: `(track_id, class0, class1, ..., classN)`
- **Quirks**: Same echo pattern as devices/name
- **Wrapper**: `scan.scan_live`
- **CLI**: `flaas scan`
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/devices/class_name', [0]))"`
- **Status**: ✅ VALIDATED

**Device Parameters**
- **Endpoint**: `/live/device/get/parameters/name`
- **Request**: `[track_id: int, device_id: int]`
- **Response**: `(track_id, device_id, name0, name1, ..., nameN)`
- **Quirks**: First 2 args echoed, param names start at index 2
- **Wrapper**: None (used in discovery only)
- **CLI**: None (manual probe only)
- **Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/parameters/name', [0,0]))"`
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/device/get/parameters/min`
- **Request**: `[track_id: int, device_id: int]`
- **Response**: `(track_id, device_id, min0, min1, ..., minN)`
- **Quirks**: Returns "linear" range (e.g., -1..+1 for Utility Gain), not actual dB
- **Wrapper**: `param_map.get_param_range`
- **CLI**: None (internal)
- **Validation**: `python3 -c "from flaas.param_map import get_param_range; print(get_param_range(0,0,9))"`
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/device/get/parameters/max`
- **Request**: `[track_id: int, device_id: int]`
- **Response**: `(track_id, device_id, max0, max1, ..., maxN)`
- **Quirks**: Same as min (linear range, not dB)
- **Wrapper**: `param_map.get_param_range`
- **CLI**: None (internal)
- **Validation**: Same as min
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/device/get/parameter/value`
- **Request**: `[track_id: int, device_id: int, param_id: int]`
- **Response**: `(track_id, device_id, param_id, value: float)` where value is normalized 0..1
- **Quirks**: Value is normalized (0..1), not linear or dB
- **Wrapper**: `verify.verify_master_utility_gain`
- **CLI**: `flaas verify`
- **Validation**: `flaas util-gain-norm 0 0 0.7 && flaas verify` (should print 0.7)
- **Status**: ✅ VALIDATED

- **Endpoint**: `/live/device/set/parameter/value`
- **Request**: `[track_id: int, device_id: int, param_id: int, value: float]` where value is normalized 0..1
- **Response**: None (fire-and-forget)
- **Quirks**: No confirmation (use get to verify)
- **Wrapper**: `util.set_utility_gain_norm`, `util.set_utility_gain_linear`, `apply.apply_actions_osc`
- **CLI**: `flaas util-gain-norm`, `flaas util-gain-linear`, `flaas apply`
- **Validation**: `flaas util-gain-norm 0 0 0.6 && flaas verify` (should print 0.6)
- **Status**: ✅ VALIDATED

---

### Next 20 Surface Expansions (Prioritized)

**Priority key**: P0 (MVP blocker) > P1 (post-MVP high) > P2 (medium) > P3 (future)

#### Expansion 1: `/live/song/export/*` (P0 - MVP blocker)
**Hypothesized endpoints**:
- `/live/song/export/audio` (unknown request format)
- `/live/song/export/midi` (unknown)

**Discovery probe**:
```bash
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once

# Try various request formats
test_cases = [
    ([], "empty list"),
    ([0, 1], "track range"),
    (["output/test.wav"], "filepath only"),
    ([0, 1, "output/test.wav"], "range + filepath"),
]

for args, desc in test_cases:
    print(f"\nTrying /live/song/export/audio with {desc}: {args}")
    try:
        resp = request_once(OscTarget(), "/live/song/export/audio", args, timeout_sec=10.0)
        print(f"  SUCCESS: {resp}")
        break
    except TimeoutError:
        print(f"  TIMEOUT (endpoint may not exist or wrong args)")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
PY
```

**Expected outcome**: Determine if endpoint exists + request format.

**If VALIDATED**: Create `export.py`, add `flaas export`, update golden path.

**If NOT EXISTS**: Document manual export as permanent MVP solution.

**Next**: Task 1 in Section 8.

---

#### Expansion 2: EQ Eight band parameters (P1)
**Already mapped**: Generic param access works for all devices.

**Discovery probe**:
```bash
# Requires: EQ Eight on a track (user adds in Ableton)
flaas scan
cat data/caches/model_cache.json | jq '.tracks[] | select(.devices[] | .class_name == "Eq8") | {track_id, devices: [.devices[] | select(.class_name == "Eq8")]}'

# Get param names
python3 -c "from flaas.osc_rpc import *; resp = request_once(OscTarget(), '/live/device/get/parameters/name', [1,0]); print('\n'.join(f'{i}: {n}' for i,n in enumerate(resp[2:])))"
```

**Expected output**: List of 40 params (5 per band × 8 bands).

**If VALIDATED**: Create `eq8.py` adapter, add `flaas eq-gain`, document param offsets.

**Next**: Task 5 in Section 8.

---

#### Expansion 3: Limiter parameters (P1)
**Discovery probe**:
```bash
# Requires: Limiter on master track
flaas scan | jq '.tracks[0].devices[] | select(.class_name | contains("Limiter"))'

python3 -c "from flaas.osc_rpc import *; resp = request_once(OscTarget(), '/live/device/get/parameters/name', [0,1]); print('\n'.join(f'{i}: {n}' for i,n in enumerate(resp[2:])))"
```

**Expected**: Params include "Ceiling", "Release", "Gain".

**If VALIDATED**: Create `limiter.py` adapter, add `flaas limiter-ceiling`, document.

---

#### Expansion 4: Track volume/panning (P2)
**Hypothesized endpoints**:
- `/live/track/get/volume`
- `/live/track/set/volume`
- `/live/track/get/panning`
- `/live/track/set/panning`

**Discovery probe**:
```bash
python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/volume', [0]))"
```

**Expected**: `(track_id, volume_normalized)`

**If VALIDATED**: Add track mixer controls.

---

#### Expansion 5: Track routing (P2)
**Hypothesized endpoints**:
- `/live/track/get/input_routing_type`
- `/live/track/get/output_routing_type`

**Discovery probe**:
```bash
python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/output_routing_type', [0]))"
```

**Expected**: Routing type string or enum.

**If VALIDATED**: Validate stem routing configuration.

---

#### Expansion 6-20: Additional Surface
- **6**: Compressor parameters (threshold, ratio, attack, release)
- **7**: Saturator parameters (drive, curve)
- **8**: Track mute/solo/arm state
- **9**: Track color (for role identification)
- **10**: Clip start/end markers
- **11**: Scene names and clip slots
- **12**: Tempo get/set
- **13**: Arrangement loop points
- **14**: Track freeze state
- **15**: Device bypass state
- **16**: Send levels (track → return track)
- **17**: Return track parameters
- **18**: Master track volume
- **19**: Crossfader assignment
- **20**: Quantization settings

**Discovery process** (same for all):
1. Check AbletonOSC GitHub docs: `curl -s https://raw.githubusercontent.com/ideoforms/AbletonOSC/master/README.md | grep -i [keyword]`
2. Run probe: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '[endpoint]', [args]))"`
3. Document in engineering notebook (Section 3)
4. Create wrapper if user-facing
5. Add CLI command if needed
6. Update this registry (move from Hypothesized → Validated)

---

### Validation Protocol (Per Expansion)

**Phase 1: Discovery Probe (read-only)**
- Execute hypothesis probe (Python REPL or single command)
- Observe output (exact format)
- Document success/timeout/error

**Phase 2: Wrapper Creation (if validated)**
- Create `[device].py` or update existing module
- Type hints for request/response
- Error handling (timeout, validation)
- Compile check: `python3 -m compileall src/flaas/[module].py`

**Phase 3: CLI Integration (if user-facing)**
- Add argparse subcommand to `cli.py`
- Help text: `flaas [command] --help`
- Test: `flaas [command] [args]`

**Phase 4: Documentation**
- Add to engineering notebook (Section 2: API Catalog)
- Add to terminal cheatsheet (Command Reference)
- Update this registry (status → VALIDATED)

**Phase 5: Stability Gate (if critical path)**
- Define gate with exact commands + expected outputs
- Add to execution-system.md Section E
- Run gate after wrapper changes

---

## 4. Audio Intelligence Program

**Current analyzers, near-term roadmap, schemas, parameter mappings**

### 4.1 Current Analyzers (Implemented)

#### Analyzer: Peak dBFS
**Module**: `analyze.py` → `analyze_wav()`  
**Algorithm**:
```python
peak = np.max(np.abs(audio_mono_float32))
peak_dbfs = -inf if peak == 0 else 20.0 * log10(peak)
```
**Validation**:
- Sine wave amplitude 0.2 → peak_dbfs = -13.98 (±0.1 dB)
- Silence → peak_dbfs = -inf

**Command**: `flaas analyze input/test.wav`  
**Output field**: `analysis.json → peak_dbfs`

---

#### Analyzer: LUFS-I (Integrated Loudness)
**Module**: `analyze.py` → `analyze_wav()`  
**Algorithm**: BS.1770-4 via `pyloudnorm.Meter(sr).integrated_loudness(audio)`  
**Standard**: ITU-R BS.1770-4, EBU R 128  
**Validation**:
- Sine wave 0.2 amplitude → lufs_i ≈ -17.7 (±0.5 LU)
- Known reference file (if available)

**Command**: `flaas analyze input/test.wav`  
**Output field**: `analysis.json → lufs_i`

---

#### Analyzer: Compliance Check
**Module**: `check.py` → `check_wav()`  
**Logic**:
- LUFS pass: `|measured - target| <= 0.5` (tolerance: ±0.5 LU)
- Peak pass: `measured <= target` (ceiling enforcement)

**Targets** (`targets.py`):
- `master_lufs`: -10.5 LUFS
- `stem_peak_ceiling_dbfs`: -6.0 dBFS (used for peak check in MVP)
- `true_peak_ceiling_dbfs`: -1.0 dBFS (placeholder, not used yet)

**Command**: `flaas check input/test.wav`  
**Output fields**: `check.json → {pass_lufs, pass_peak}`

---

### 4.2 Near-Term Analyzers (Post-MVP Roadmap)

#### Analyzer: True-Peak Estimate (P1)
**Purpose**: Detect inter-sample peaks (more accurate than peak dBFS).

**Algorithm** (planned):
```python
def estimate_true_peak_dbtp(audio: np.ndarray, sr: int, oversample: int = 4) -> float:
    """Oversample and compute peak (ITU-R BS.1770-4 compliant)."""
    from scipy.signal import resample
    upsampled = resample(audio, len(audio) * oversample)
    peak = np.max(np.abs(upsampled))
    return -inf if peak == 0 else 20.0 * log10(peak)
```

**Validation**:
- True-peak >= peak dBFS (always)
- Test on known file with inter-sample peaks
- Compare to commercial true-peak meter

**Discovery task**: Task 10 in Section 8.

**Output field**: `analysis.json → true_peak_dbtp`

---

#### Analyzer: Band Energy (P1)
**Purpose**: Detect frequency imbalances (rumble, mud, harshness).

**Bands** (planned):
- Sub-bass: 20-60 Hz (rumble detection)
- Low-mid: 200-500 Hz (mud detection)
- High-mid: 2-6 kHz (harshness detection)
- High: 8-16 kHz (sibilance/air)

**Algorithm** (planned):
```python
from scipy.signal import butter, filtfilt

def band_energy_dbfs(audio: np.ndarray, sr: int, low_hz: float, high_hz: float) -> float:
    """Compute RMS energy in frequency band."""
    sos = butter(4, [low_hz, high_hz], btype='band', fs=sr, output='sos')
    filtered = filtfilt(sos, audio)
    rms = np.sqrt(np.mean(filtered**2))
    return -inf if rms == 0 else 20.0 * log10(rms)
```

**Validation**:
- Test tone at 40 Hz → sub-bass high, others low
- Test tone at 320 Hz → low-mid high, others low

**Discovery task**: Task 9 in Section 8.

**Output fields**: `analysis.json → {sub_bass_dbfs, low_mid_dbfs, high_mid_dbfs, high_dbfs}`

---

#### Analyzer: Multi-Stem Support (P1)
**Purpose**: Analyze multiple stems (MASTER, VOCAL, BASS, etc.) in one pass.

**Naming contract**:
```
{song}_{ROLE}.wav

Examples:
- track01_MASTER.wav
- track01_VOCAL_LEAD.wav
- track01_BASS.wav

Roles: MASTER, VOCAL_LEAD, VOCAL_BG, BASS, DRUMS, KEYS, OTHER
```

**Algorithm** (planned):
```python
def analyze_stem_set(paths: list[Path]) -> dict[str, AnalysisResult]:
    """Analyze multiple stems, validate naming."""
    stems = validate_stem_set(paths)  # Raises if invalid
    results = {}
    for path in paths:
        song, role = parse_stem_filename(path)
        results[role] = analyze_wav(path)
    return results
```

**Validation**:
- Create test stems: `track01_MASTER.wav`, `track01_VOCAL_LEAD.wav`
- Run: `flaas analyze-stems input/track01_*.wav`
- Verify: JSON output includes all roles

**Discovery task**: Task 12 in Section 8.

**Output**: `data/reports/stems_analysis.json → {MASTER: {...}, VOCAL_LEAD: {...}}`

---

### 4.3 Parameter Mapping Intelligence

**Current mappings**:

| Device | Class Name | Param ID | Param Name | Linear Range | Normalized | Notes |
|--------|------------|----------|------------|--------------|------------|-------|
| Utility | StereoGain | 9 | Gain | -1.0 to +1.0 | 0..1 | Center = 0.5 norm = 0.0 linear |

**Mapping functions**:
- `param_map.get_param_range(track, device, param)` → `ParamRange(min, max)`
- `param_map.linear_to_norm(x, pr)` → float in [0, 1]
- Inverse: `linear = pr.min + norm * (pr.max - pr.min)`

**Future mappings** (post-MVP):

| Device | Params to Map | Priority | Discovery Command |
|--------|---------------|----------|-------------------|
| EQ Eight | Band 1-8: freq, gain, Q, type | P1 | `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/parameters/name', [1,0]))"` |
| Compressor | Threshold, Ratio, Attack, Release | P1 | Similar to EQ |
| Limiter | Ceiling, Release, Gain | P1 | Similar to EQ |
| Saturator | Drive, Curve, Dry/Wet | P2 | Similar to EQ |
| Glue Compressor | Attack, Release, Ratio, Makeup | P2 | Similar to EQ |

**Mapping workflow**:
1. Discover param names (see Discovery Command)
2. Get min/max for each param
3. Determine semantics: linear, log, dB, enum, boolean
4. Create device-specific adapter (e.g., `eq8.py`)
5. Validate: set value, read back, verify in Ableton
6. Document in engineering notebook

---

### 4.4 Planning Logic (Decision Rules)

**Current planner**: `plan.py` → `plan_utility_gain_delta_for_master()`

**Algorithm**:
```python
# 1. Measure current state
lufs_measured = analyze_wav(wav).lufs_i
lufs_target = -10.5  # from targets.py
cur_gain_linear = get_current_utility_linear()  # OSC query

# 2. Compute error
err_db = lufs_target - lufs_measured  # Positive = need more gain

# 3. Map to control delta (rough first-order model)
raw_delta = err_db / 12.0  # 12 dB change ≈ full-scale control move

# 4. Clamp for safety
delta_linear = clamp(raw_delta, -0.25, +0.25)

# 5. Output action
action = GainAction(track_role="MASTER", device="Utility", param="Gain", delta_db=delta_linear)
```

**Validation**:
- LUFS too quiet (-17.7) → positive delta
- LUFS too loud (-5.0) → negative delta
- Delta never exceeds ±0.25

**Command**: `flaas plan-gain input/test.wav`

**Improvements needed** (future):
- Better LUFS → gain model (nonlinear, iterative refinement)
- Peak headroom enforcement (reduce gain if peak would clip)
- Multi-stem planning (per-stem actions)

---

### 4.5 Audio Intelligence Schemas

#### Schema: AnalysisResult
**File**: `data/reports/analysis.json`  
**Producer**: `analyze.write_analysis()`

```json
{
  "file": "input/test.wav",
  "sr": 48000,
  "channels": 1,
  "samples": 96000,
  "duration_sec": 2.0,
  "peak_dbfs": -13.98,
  "lufs_i": -17.72,
  "created_at_utc": "2026-02-22T10:30:00.123456Z"
}
```

**Validation**: All fields present, peak_dbfs < 0, lufs_i < 0 (typical).

---

#### Schema: CheckResult
**File**: `data/reports/check.json`  
**Producer**: `check.write_check()`

```json
{
  "file": "input/test.wav",
  "pass_lufs": false,
  "pass_peak": true,
  "lufs_i": -17.72,
  "peak_dbfs": -13.98,
  "target_lufs": -10.5,
  "target_peak_dbfs": -6.0
}
```

**Validation**: All booleans present, measured values match analysis.json.

---

#### Schema: ActionsFile (v1.0)
**File**: `data/actions/actions.json`  
**Producer**: `actions.write_actions()`

```json
{
  "schema_version": "1.0",
  "created_at_utc": "2026-02-22T10:30:00Z",
  "live_fingerprint": "a1b2c3d4e5f6...",
  "actions": [
    {
      "track_role": "MASTER",
      "device": "Utility",
      "param": "Gain",
      "delta_db": 0.123
    }
  ]
}
```

**Validation**: schema_version present, fingerprint 64 hex chars, actions array non-empty.

**CRITICAL**: `delta_db` field is legacy name; actually contains **linear delta** (-1..+1), not dB.

---

#### Schema: ScanResult
**File**: `data/caches/model_cache.json`  
**Producer**: `scan.write_model_cache()`

```json
{
  "ok": true,
  "note": "live scan",
  "created_at_utc": "2026-02-22T10:30:00Z",
  "num_tracks": 1,
  "tracks": [
    {
      "track_id": 0,
      "name": "Master",
      "num_devices": 1,
      "devices": [
        {"index": 0, "name": "Utility", "class_name": "StereoGain"}
      ]
    }
  ],
  "fingerprint": "a1b2c3d4e5f6..." (SHA256 hex, 64 chars)
}
```

**Validation**: ok=true, num_tracks > 0, fingerprint non-empty.

**Fingerprint algorithm**: `sha256(";".join([f"{tid}:{name}:{num_devices}:{device_classes_pipe_separated}"]))`

---

### 4.6 Future Intelligence (Exploratory)

**Mix Profiles** (P3):
- **Definition**: Named set of numeric targets + parameter mappings (NOT waveform copying)
- **Example**: `profiles/clean_mastering.json`:
  ```json
  {
    "name": "Clean Mastering",
    "targets": {
      "master_lufs": -10.5,
      "master_peak_dbfs": -1.0,
      "stem_peak_dbfs": -6.0,
      "sub_rumble_max_dbfs": -40.0,
      "mud_ratio_max": 0.3
    },
    "param_mappings": {
      "utility_gain_clamp": 0.25,
      "eq_cut_max_db": -6.0
    }
  }
  ```
- **Validation**: Load profile, run analysis, verify targets applied

**Reference Track Extraction** (P4, constrained):
- **Definition**: Extract numeric targets from reference track (LUFS, peak, band ratios only)
- **NOT**: Waveform copying, EQ matching, transient cloning
- **Command**: `flaas extract-targets reference.wav --output profiles/from_reference.json`
- **Validation**: Analyze reference manually, compare to extracted targets

---

## 5. Safety + Stability Gates (Non-Negotiable)

**Gates that must pass before shipping any capability.**

### Gate G1: OSC Health + Scan Stability
**Purpose**: Verify basic Ableton communication and set structure query.

**Commands**:
```bash
# G1.1: Bidirectional ping
flaas ping --wait

# G1.2: Scan Live set
flaas scan

# G1.3: Verify scan output
cat data/caches/model_cache.json | jq '{ok, num_tracks, fingerprint}'
```

**Expected outputs**:
```
# G1.1:
ok: ('ok',)

# G1.2:
data/caches/model_cache.json

# G1.3:
{
  "ok": true,
  "num_tracks": 1,
  "fingerprint": "a1b2c3d4e5f6..." (64 hex chars)
}
```

**Pass criteria**:
- ✅ All 3 commands exit 0
- ✅ Ping returns `('ok',)` tuple
- ✅ Scan writes valid JSON with `ok: true`
- ✅ num_tracks > 0, fingerprint non-empty

**Run after**: Any change to `osc.py`, `osc_rpc.py`, `scan.py`

**Run frequency**: Every session start, after Ableton restart

---

### Gate G2: Fingerprint Safety + Action Correctness
**Purpose**: Verify fingerprint enforcement prevents stale actions.

**Commands**:
```bash
# G2.1: Generate baseline
flaas reset
flaas plan-gain input/test.wav

# G2.2: Check fingerprint embedded
cat data/actions/actions.json | jq -r '.live_fingerprint'

# G2.3: Apply should succeed
flaas apply

# G2.4: Modify Live set (add track in Ableton)
echo "USER ACTION: Add a track in Ableton, then press Enter"
read

# G2.5: Try to apply old actions (should fail)
flaas apply
```

**Expected outputs**:
```
# G2.2:
a1b2c3d4e5f6...

# G2.3:
APPLIED: Utility.Gain 0.000 -> 0.XXX (norm 0.500->0.XXX)

# G2.5:
RuntimeError: Live fingerprint mismatch: expected a1b2c3..., got d4e5f6...
```

**Pass criteria**:
- ✅ G2.3 succeeds (apply with matching fingerprint)
- ✅ G2.5 fails with RuntimeError (rejects stale fingerprint)
- ✅ Error message shows expected vs actual

**Critical**: If G2.5 succeeds, fingerprint enforcement is broken (escalate immediately).

**Run after**: Changes to `apply.py`, `scan.py`, `actions.py`

---

### Gate G3: Audio Analysis Correctness
**Purpose**: Verify analysis produces expected values on known WAV.

**Commands**:
```bash
# G3.1: Generate known test WAV
python3 - <<'PY'
import numpy as np, soundfile as sf, os
os.makedirs("input", exist_ok=True)
sr = 48000
t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
x = 0.2*np.sin(2*np.pi*440*t)  # -13.98 dBFS, ~-17.7 LUFS
sf.write("input/test.wav", x, sr)
print(f"Generated: peak={np.max(np.abs(x)):.4f}")
PY

# G3.2: Analyze
flaas analyze input/test.wav

# G3.3: Verify values
cat data/reports/analysis.json | jq '{peak_dbfs, lufs_i}'
```

**Expected outputs**:
```
# G3.1:
Generated: peak=0.2000

# G3.3:
{
  "peak_dbfs": -13.98 (±0.1 tolerance),
  "lufs_i": -17.7 (±0.5 tolerance)
}
```

**Pass criteria**:
- ✅ Peak within ±0.1 dB of -13.98
- ✅ LUFS within ±0.5 LU of -17.7

**Run after**: Changes to `analyze.py`, `audio_io.py`

---

### Gate G4: Apply Correctness + Readback
**Purpose**: Verify parameter changes are applied and readable.

**Commands**:
```bash
# G4.1: Reset to known state
flaas reset
flaas verify  # Should print 0.500

# G4.2: Set specific value
flaas util-gain-linear 0 0 0.3
flaas verify  # Should print ~0.650 (depends on param range)

# G4.3: Apply delta via actions
flaas reset
echo '{"schema_version":"1.0","created_at_utc":"2026-02-22T00:00:00Z","live_fingerprint":"'$(cat data/caches/model_cache.json | jq -r .fingerprint)'","actions":[{"track_role":"MASTER","device":"Utility","param":"Gain","delta_db":0.1}]}' > data/actions/actions.json
flaas apply
flaas verify  # Should be ~0.5 + (0.1 mapped to norm)
```

**Expected outputs**:
```
# G4.1:
sent
0.500

# G4.2:
sent
0.650 (example)

# G4.3:
APPLIED: Utility.Gain 0.000 -> 0.100 (norm 0.500->0.550)
0.550
```

**Pass criteria**:
- ✅ Reset returns to 0.500
- ✅ Set + readback match (within ±0.01)
- ✅ Delta application is relative (not absolute)

**Run after**: Changes to `apply.py`, `util.py`, `param_map.py`, `verify.py`

---

### Gate G5: Render Automation (Future)
**Purpose**: Verify automated export when implemented.

**Status**: 🚧 Pending `/live/song/export/*` endpoint discovery (Expansion 1)

**Commands** (hypothetical):
```bash
flaas export --track 0 --output output/test.wav
timeout 30 bash -c 'until [ -f output/test.wav ]; do sleep 1; done' && echo "Export complete"
ls -lh output/test.wav
flaas analyze output/test.wav
```

**Expected**: File appears, valid WAV, analysis succeeds.

**Run after**: Export automation implemented.

---

### Non-Negotiable Invariants (Never Bypass)

1. **Fingerprint enforcement** in apply (unless `enforce_fingerprint=False` for debugging)
2. **Delta clamps** (±0.25 linear) in plan
3. **Max gain stop** (0.99 norm) in loop
4. **Normalized clamping** ([0, 1]) in all set operations
5. **Relative delta application** (read current → add delta → set new) in apply
6. **Schema versioning** in all artifacts
7. **Timestamp logging** in all artifacts (ISO8601 UTC)

**Validation**: Run Gates G1-G4 after any safety-critical change.

---

## 6. Engineering Notebook Integration Rules

**How docs stay current + regeneration rules**

### Rule 1: When Code Changes → Update Notebook

**Trigger events**:
- New module created (`src/flaas/[name].py`)
- Function signature changed
- New CLI command added
- OSC endpoint discovered

**Update checklist**:
1. ✅ Add/update Section 1 (Codebase Index) - file purpose + dependencies
2. ✅ Add/update Section 2 (API Catalog) - function signature + full details
3. ✅ Add/update Section 3 (OSC Contract) - endpoint details if OSC-related
4. ✅ Add/update Section 5 (CLI Command Sheet) - command + args + exit codes
5. ✅ Regenerate Section 12 (Unique Line Ledger): `python3 scripts/generate_unique_lines.py`
6. ✅ Update Section 6 (Call Graph) if new caller/callee relationships

**Validation**:
```bash
# Check notebook is consistent
grep "def [a-z_]*(" src/flaas/*.py | wc -l  # Count functions
grep "^### \`.*\`$" docs/reference/ENGINEERING_NOTEBOOK.md | wc -l  # Count documented functions
# Should match (or notebook has more if includes internal functions)
```

---

### Rule 2: Unique Line Ledger Regeneration

**When to regenerate**:
- Any code added/changed in `src/flaas/`
- After merging branches
- Before major milestone commits

**Command**:
```bash
python3 scripts/generate_unique_lines.py
```

**Expected output**:
```
Processing src/flaas/...
Found N unique lines across M files
Writing docs/reference/unique-lines/*.md
Done. Generated:
  - INDEX.md
  - cli_wiring.md
  - comments.md
  - constants.md
  - decorators.md
  - definitions.md
  - file_io.md
  - imports.md
  - logic.md
  - osc_calls.md
  - planning.md
  - safety.md
  - stats.json
```

**Validation**:
```bash
ls docs/reference/unique-lines/
cat docs/reference/unique-lines/stats.json | jq .
```

**Commit**:
```bash
git add docs/reference/unique-lines/
git commit -m "docs: regenerate unique line ledger"
```

---

### Rule 3: Cross-Reference Validation

**After any doc update**, check links:

```bash
cd docs/
grep -rn "\[.*\](" . --include="*.md" | grep -v "http" | while read line; do
  file=$(echo "$line" | cut -d: -f1)
  link=$(echo "$line" | grep -oP '\[.*?\]\(\K[^)]+')
  if [ ! -z "$link" ] && [ ! -f "$(dirname $file)/$link" ] && [ ! -f "$link" ]; then
    echo "BROKEN: $file → $link"
  fi
done
```

**Expected**: No output (all links valid).

**Fix**: Update broken links, commit: `git commit -m "docs: fix broken links"`

---

### Rule 4: Sync README.md Commands Section

**Trigger**: CLI command added/changed in `cli.py`

**Process**:
1. Extract commands from cli.py:
   ```bash
   grep "sub.add_parser" src/flaas/cli.py | grep -oP "\"[a-z-]+\"" | tr -d '"'
   ```
2. Update `README.md` Commands section
3. Update `docs/workflow/terminal-cheatsheet.md` Command Reference table
4. Validate: `flaas --help` (should show all commands)
5. Commit: `git commit -m "docs: sync commands in README"`

---

### Rule 5: Version Bump Protocol

**Trigger**: Shipping a new capability or breaking change

**Process**:
1. Update version in `pyproject.toml`, `src/flaas/__init__.py`
2. Update `CHANGELOG.md` (if exists) with changes
3. Update `reference/FINISHLINE_PROGRESS_INDEX.md` with new step receipts
4. Update `finishline_context_state.json` version field
5. Commit: `git commit -m "chore: bump version to [X.Y.Z]"`

**Versioning scheme**:
- `0.0.x`: Pre-MVP iterations
- `0.1.0`: MVP complete (Utility Gain + manual export loop)
- `0.2.0`: Post-MVP (multi-stem or EQ control)
- `1.0.0`: Production-ready (automated export, full test suite)

---

## 7. Workflow Protocol (Compact FSM + Decision Algorithm)

**Finite-State Machine states + transitions** (see `workflow/execution-system.md` for full details)

### FSM States (Quick Reference)

```
PLAN → EDIT → RUN → OBSERVE → {COMMIT | DIAGNOSE → FIX → VERIFY → COMMIT}
```

**State: PLAN**
- **Input**: User provides Step N specification
- **Output**: Task understood (step number, commands, expected output)
- **Next**: EDIT

**State: EDIT**
- **Input**: Task specification
- **Output**: Files modified (list all)
- **Next**: RUN

**State: RUN**
- **Input**: Validation command
- **Output**: Terminal output (stdout + stderr + exit code)
- **Next**: OBSERVE

**State: OBSERVE**
- **Input**: Command output
- **Output**: Classification (success or error category 1-6)
- **Next**: COMMIT (if success) or DIAGNOSE (if error)

**State: DIAGNOSE**
- **Input**: Error output
- **Output**: Error category + probe command
- **Next**: FIX (if fixable) or STOP (if user action required)
- **Limit**: Max 3 probes

**State: FIX**
- **Input**: Diagnosis + fix strategy
- **Output**: Files modified or command executed
- **Next**: VERIFY

**State: VERIFY**
- **Input**: Original validation command
- **Output**: Re-run result
- **Next**: COMMIT (if pass) or DIAGNOSE (if fail)
- **Limit**: Max 3 fix attempts

**State: COMMIT**
- **Input**: Validated changes
- **Output**: Git commit SHA + push confirmation
- **Next**: DONE (ready for next PLAN)

---

### Error Taxonomy (Quick Reference)

**Category 1: Connectivity/Ports**
- **Symptoms**: `TimeoutError.*waiting.*reply`, `Connection refused`
- **Probe**: `flaas ping --wait`
- **Auto-fix**: None (user must start Ableton)

**Category 2: Ableton Configuration**
- **Symptoms**: `ok: false` in scan, `num_tracks: 0`, empty devices
- **Probe**: `flaas scan && cat model_cache.json | jq .tracks[0]`
- **Auto-fix**: None (user must add tracks/devices)

**Category 3: Schema/Fingerprint Mismatch**
- **Symptoms**: `RuntimeError.*fingerprint mismatch`
- **Probe**: `cat actions.json | jq -r .live_fingerprint` vs `cat model_cache.json | jq -r .fingerprint`
- **Auto-fix**: `flaas scan && flaas plan-gain input/test.wav` (regenerate)

**Category 4: Audio Analysis**
- **Symptoms**: `ValueError.*empty audio`, `FileNotFoundError.*\.wav`
- **Probe**: `ls -lh input/test.wav && file input/test.wav`
- **Auto-fix**: Regenerate test file (see Step 2.1)

**Category 5: Path/Permissions**
- **Symptoms**: `PermissionError`, `cannot create directory`
- **Probe**: `ls -la data/`
- **Auto-fix**: `mkdir -p data/caches data/reports data/actions`

**Category 6: Packaging/Import**
- **Symptoms**: `ModuleNotFoundError`, `command not found: flaas`
- **Probe**: `pip show flaas`
- **Auto-fix**: `pip install -e .`

**Full details**: See `workflow/execution-system.md` Section B.

---

### Paste Templates (Quick Reference)

**Normal success**:
```
✅ **Step N complete.**
**Validation output:**
[exact terminal output]
**git push output:**
[git push output]
```

**Error encountered**:
```
⚠️ **Error during Step N.**
**Terminal output:**
[exact error with full traceback]
**Error category:** [1-6]
**Next probe:**
[single diagnostic command]
```

**Full templates**: See `workflow/execution-system.md` Section D.

---

### Decision Algorithm (Quick Reference)

**Input**: Terminal output from RUN state

**Step 1**: Parse exit code (0 = success path, ≠0 = error path)

**Step 2 (success path)**: Match success patterns
- `sent`, `ok: (...)`, `APPLIED:`, `PASS`, `data/.*.json`
- If matched → COMMIT
- If not matched but exit 0 → Warn, review manually

**Step 3 (error path)**: Classify into Category 1-6
- Match regex patterns (see Taxonomy)
- Select category-specific probe
- Execute probe

**Step 4**: Choose action type
- Read-only probe (preferred)
- Auto-fix (if deterministic)
- User action (if external dependency)
- Escalate (if unknown)

**Step 5**: Execute + transition to next state

**Full algorithm**: See `workflow/execution-system.md` Section C.

---

## 8. Shipping Roadmap (MVP → v1 → v2)

### 8.1 Backlog (≤30 tasks, prioritized)

**MVP Completion (v0.1.0)**:
1. ✅ OSC connectivity (ping, RPC)
2. ✅ Live set scanning (tracks, devices, fingerprint)
3. ✅ Audio analysis (peak dBFS, LUFS-I)
4. ✅ Compliance checking (targets)
5. ✅ Action planning (bounded delta)
6. ✅ OSC parameter control (Utility Gain)
7. ✅ Closed-loop iteration (loop with safety stops)
8. ✅ Fingerprint enforcement
9. ✅ Manual export workflow documented
10. ⬜ **Automated export** (requires Expansion 1) ← **Next bottleneck**

**Post-MVP (v0.2.0)**:
11. ⬜ True-peak estimation (oversampling)
12. ⬜ Band energy analysis (rumble, mud, harshness detection)
13. ⬜ Multi-stem support (naming contract + per-stem analysis)
14. ⬜ EQ Eight control (band gain cuts)
15. ⬜ Limiter control (ceiling enforcement)
16. ⬜ Iteration cap + timeline logging
17. ⬜ Unit test suite (pytest for analysis/plan/apply)
18. ⬜ Integration test harness (requires Ableton)
19. ⬜ Error message improvements (contextual hints)
20. ⬜ `flaas doctor` environment health check

**v1.0 (Production-Ready)**:
21. ⬜ Compressor control (threshold, ratio)
22. ⬜ Per-stem EQ planning (bass cut, vocal presence boost)
23. ⬜ Stem routing validation (verify send/receive chains)
24. ⬜ Mix profiles (load/save numeric target sets)
25. ⬜ Reference track extraction (numeric targets only)
26. ⬜ Stereo width analysis
27. ⬜ Crest factor (dynamic range) analysis
28. ⬜ Audit log export (all actions + timestamps)
29. ⬜ Replay mode (re-apply logged actions)
30. ⬜ CI/CD pipeline (automated testing)

---

### 8.2 Next 12 Atomic Tasks (Immediate Backlog)

**Context**: Starting from current MVP state (Utility Gain control working).

---

#### Task 1: Discover `/live/song/export/*` endpoint existence
**Type**: Discovery Mode  
**File changes**: None (probe only)

**Command**:
```bash
# Check AbletonOSC docs
curl -s https://raw.githubusercontent.com/ideoforms/AbletonOSC/master/README.md | grep -i export

# Attempt probe
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once
try:
    resp = request_once(OscTarget(), "/live/song/export/audio", [], timeout_sec=5.0)
    print(f"SUCCESS: {resp}")
except TimeoutError:
    print("TIMEOUT: Endpoint likely does not exist")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
PY
```

**Expected output**: SUCCESS (endpoint exists) or TIMEOUT (doesn't exist)

**Success criteria**: Determination of endpoint existence.

**Rollback**: None (read-only).

**Next if exists**: Task 2 (map export parameters).  
**Next if not exists**: Task 5 (skip to EQ Eight).

---

#### Task 2: Map `/live/song/export/audio` parameters (conditional)
**Type**: Discovery Mode  
**File changes**: None (probe only)

**Command**:
```bash
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once

# Try various request formats
test_cases = [
    ([], "empty"),
    (["output/test.wav"], "filepath only"),
    ([0, "output/test.wav"], "track_id + filepath"),
    (["output/test.wav", 48000, 24], "path + sr + depth"),
]

for args, desc in test_cases:
    print(f"\nTrying: {desc}")
    try:
        resp = request_once(OscTarget(), "/live/song/export/audio", args, timeout_sec=15.0)
        print(f"  SUCCESS: {resp}")
        print(f"  VALIDATED FORMAT: {args}")
        break
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}")
PY
```

**Expected output**: One format succeeds, reveals args.

**Success criteria**: Document request format in notebook.

**Rollback**: None.

**Next**: Task 3 (implement export module).

---

#### Task 3: Implement `export.py` module (conditional)
**Type**: Shipping Mode  
**File changes**: `src/flaas/export.py` (new)

**Command**:
```bash
cat > src/flaas/export.py <<'EOF'
from __future__ import annotations
from pathlib import Path
from flaas.osc_rpc import OscTarget, request_once

def export_master(
    output_path: str | Path,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 30.0,
) -> None:
    """
    Trigger Ableton export via OSC.
    
    Request format based on Task 2 discovery.
    Blocks until export completes or times out.
    """
    # TODO: Adjust args based on Task 2 result
    resp = request_once(
        target,
        "/live/song/export/audio",
        [str(output_path)],  # Placeholder format
        timeout_sec=timeout_sec,
    )
    print(f"Export response: {resp}")
EOF

python3 -m compileall src/flaas/export.py
```

**Expected output**: `Compiling 'src/flaas/export.py'...` (no errors)

**Success criteria**: Module compiles.

**Rollback**: `rm src/flaas/export.py`

**Next**: Task 4 (add CLI command).

---

#### Task 4: Add `flaas export` CLI command (conditional)
**Type**: Shipping Mode  
**File changes**: `src/flaas/cli.py` (add export parser + handler)

**Command**:
```bash
# Agent edits cli.py to add:
# - import export module
# - add export subparser
# - add export handler

python3 -m compileall src/flaas/cli.py

flaas export --help

# Test (requires Ableton with renderable track)
flaas export --output output/test_export.wav

ls -lh output/test_export.wav
file output/test_export.wav
```

**Expected output**:
```
Compiling 'src/flaas/cli.py'...

usage: flaas export [-h] --output OUTPUT [--timeout TIMEOUT]

Export response: (...)
-rw-r--r-- 1 user staff NNNN ... output/test_export.wav
output/test_export.wav: RIFF ... WAVE audio
```

**Success criteria**: File appears, is valid WAV.

**Rollback**: `git checkout -- src/flaas/cli.py && rm src/flaas/export.py`

**Commit**: `git add -A && git commit -m "feat: add automated export via OSC" && git push`

**Next**: Integrate into loop (Task 11).

---

#### Task 5: Discover EQ Eight device + parameters (P1)
**Type**: Discovery Mode  
**File changes**: None (probe only)

**Command**:
```bash
# Requires: User adds EQ Eight to a track in Ableton

flaas scan
cat data/caches/model_cache.json | jq '.tracks[] | select(.devices[] | .class_name | contains("Eq")) | {track_id, name, eq_device: [.devices[] | select(.class_name | contains("Eq"))]}'

# Get param names (adjust track/device based on above)
python3 -c "from flaas.osc_rpc import *; resp = request_once(OscTarget(), '/live/device/get/parameters/name', [1,0]); print('\n'.join(f'{i}: {n}' for i,n in enumerate(resp[2:])))"
```

**Expected output**:
```
{
  "track_id": 1,
  "name": "Audio",
  "eq_device": [{"index": 0, "name": "EQ Eight", "class_name": "Eq8"}]
}

0: Device On
1: Filter 1 Frequency A
2: Filter 1 Gain A
3: Filter 1 Resonance A
... (5 params per band × 8 bands = 40 params)
```

**Success criteria**: EQ class name = `Eq8`, param structure documented.

**Rollback**: None.

**Next**: Task 6 (create EQ adapter).

---

#### Task 6: Create `eq8.py` adapter module
**Type**: Shipping Mode  
**File changes**: `src/flaas/eq8.py` (new)

**Command**:
```bash
cat > src/flaas/eq8.py <<'EOF'
from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget
from flaas.param_map import get_param_range, linear_to_norm

# EQ Eight param layout: 5 params per band (freq, gain, Q, type, enabled)
# Bands 1-8: params 0-39

def _band_param_id(band: int, param_name: str) -> int:
    """Get parameter ID for EQ band parameter."""
    if not 1 <= band <= 8:
        raise ValueError(f"Band must be 1-8, got {band}")
    
    band_base = (band - 1) * 5
    offsets = {"freq": 0, "gain": 1, "q": 2, "type": 3, "enabled": 4}
    
    if param_name not in offsets:
        raise ValueError(f"Unknown param: {param_name}. Valid: {list(offsets.keys())}")
    
    return band_base + offsets[param_name]

def set_band_gain(
    track_id: int,
    device_id: int,
    band: int,
    gain_linear: float,
    target: OscTarget = OscTarget(),
) -> None:
    """
    Set EQ Eight band gain.
    
    Note: gain_linear is in device's linear units (from min/max query).
    Typical range: -12.0 to +12.0 (but varies by band/type).
    """
    param_id = _band_param_id(band, "gain")
    pr = get_param_range(track_id, device_id, param_id, target=target)
    norm = linear_to_norm(gain_linear, pr)
    
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, param_id, float(norm)])
    print(f"Set EQ band {band} gain to {gain_linear:.2f} (norm {norm:.3f})")
EOF

python3 -m compileall src/flaas/eq8.py
```

**Expected output**: `Compiling 'src/flaas/eq8.py'...` (no errors)

**Success criteria**: Module compiles, functions defined.

**Rollback**: `rm src/flaas/eq8.py`

**Next**: Task 7 (add CLI command).

---

#### Task 7: Add `flaas eq-gain` CLI command
**Type**: Shipping Mode  
**File changes**: `src/flaas/cli.py` (add eq-gain parser + handler)

**Command**:
```bash
# Agent edits cli.py

python3 -m compileall src/flaas/cli.py

flaas eq-gain --help

# Test (requires EQ Eight on track 1 device 0)
flaas eq-gain 1 0 --band 2 --gain -3.0

# Verify
python3 -c "from flaas.osc_rpc import *; from flaas.eq8 import _band_param_id; pid = _band_param_id(2, 'gain'); resp = request_once(OscTarget(), '/live/device/get/parameter/value', [1,0,pid]); print(f'Band 2 gain norm: {resp[3]}')"
```

**Expected output**:
```
Compiling 'src/flaas/cli.py'...

usage: flaas eq-gain [-h] track_id device_id --band BAND --gain GAIN

Set EQ band 2 gain to -3.00 (norm 0.XXX)

Band 2 gain norm: 0.XXX (should be <0.5 for negative gain)
```

**Success criteria**: Command executes, readback confirms change.

**Rollback**: `git checkout -- src/flaas/cli.py && rm src/flaas/eq8.py`

**Commit**: `git add -A && git commit -m "feat: add EQ Eight band gain control" && git push`

**Next**: Task 8 (generate multi-band test audio).

---

#### Task 8: Generate multi-band test WAV
**Type**: Shipping Mode (audio intelligence)  
**File changes**: `input/test_multiband.wav` (new)

**Command**:
```bash
python3 - <<'PY'
import numpy as np, soundfile as sf, os

os.makedirs("input", exist_ok=True)
sr = 48000
dur = 2.0
t = np.linspace(0, dur, int(sr * dur), endpoint=False)

# Multi-band signal (equal amplitude per band)
sub_bass = 0.1 * np.sin(2*np.pi*40*t)    # 40 Hz
mid = 0.1 * np.sin(2*np.pi*320*t)        # 320 Hz (mud)
high = 0.1 * np.sin(2*np.pi*4000*t)      # 4 kHz (presence)

x = sub_bass + mid + high
sf.write("input/test_multiband.wav", x, sr)

print(f"Generated: {x.shape[0]} samples, peak={np.max(np.abs(x)):.4f}")
print("Bands: 40 Hz (sub), 320 Hz (mid), 4000 Hz (high) - equal amplitude")
PY

flaas analyze input/test_multiband.wav
cat data/reports/analysis.json | jq '{peak_dbfs, lufs_i}'
```

**Expected output**:
```
Generated: 96000 samples, peak=0.3000
Bands: 40 Hz (sub), 320 Hz (mid), 4000 Hz (high) - equal amplitude

data/reports/analysis.json

{
  "peak_dbfs": -10.46,
  "lufs_i": -XX.X
}
```

**Success criteria**: File created, analysis succeeds.

**Rollback**: `rm input/test_multiband.wav`

**Next**: Task 9 (add band energy analysis).

---

#### Task 9: Add band energy analysis to `analyze.py`
**Type**: Shipping Mode  
**File changes**: `src/flaas/analyze.py` (modify AnalysisResult + analyze_wav)

**Command**:
```bash
# Agent edits analyze.py to add:
# - band_energy_dbfs() function using scipy.signal bandpass filters
# - Add fields to AnalysisResult: sub_bass_dbfs, low_mid_dbfs, high_mid_dbfs, high_dbfs
# - Update analyze_wav() to compute band energies

python3 -m compileall src/flaas/analyze.py

# Test on multi-band file
flaas analyze input/test_multiband.wav
cat data/reports/analysis.json | jq '{peak_dbfs, lufs_i, sub_bass_dbfs, high_dbfs}'
```

**Expected output**:
```
Compiling 'src/flaas/analyze.py'...

data/reports/analysis.json

{
  "peak_dbfs": -10.46,
  "lufs_i": -XX.X,
  "sub_bass_dbfs": -XX.X (should be high for 40 Hz tone),
  "high_dbfs": -XX.X (should be high for 4 kHz tone)
}
```

**Success criteria**: Band energy fields present, values match expected frequency content.

**Rollback**: `git checkout -- src/flaas/analyze.py`

**Commit**: `git add src/flaas/analyze.py && git commit -m "feat: add band energy analysis" && git push`

**Next**: Task 10 (true-peak estimator).

---

#### Task 10: Create true-peak estimator module
**Type**: Shipping Mode  
**File changes**: `src/flaas/truepeak.py` (new)

**Command**:
```bash
cat > src/flaas/truepeak.py <<'EOF'
from __future__ import annotations
import numpy as np
from scipy.signal import resample

def estimate_true_peak_dbtp(audio: np.ndarray, sr: int, oversample: int = 4) -> float:
    """
    Estimate true peak via oversampling.
    
    Note: Uses simple resampling (not ITU-R BS.1770 compliant filter).
    Good enough for safety margin estimation.
    """
    if audio.size == 0:
        return -float("inf")
    
    upsampled = resample(audio, len(audio) * oversample)
    peak = float(np.max(np.abs(upsampled)))
    
    if peak == 0.0:
        return -float("inf")
    
    return float(20.0 * np.log10(peak))
EOF

python3 -m compileall src/flaas/truepeak.py

# Test
python3 - <<'PY'
from flaas.audio_io import read_mono_float
from flaas.truepeak import estimate_true_peak_dbtp

audio, sr = read_mono_float("input/test.wav")
tp = estimate_true_peak_dbtp(audio, sr)
peak_dbfs = 20.0 * np.log10(np.max(np.abs(audio)))

print(f"Peak dBFS: {peak_dbfs:.2f}")
print(f"True peak dBTP: {tp:.2f}")
print(f"Difference: {tp - peak_dbfs:.2f} dB (should be >= 0)")
PY
```

**Expected output**:
```
Compiling 'src/flaas/truepeak.py'...

Peak dBFS: -13.98
True peak dBTP: -13.50
Difference: 0.48 dB (should be >= 0)
```

**Success criteria**: True-peak >= peak dBFS (always).

**Rollback**: `rm src/flaas/truepeak.py`

**Commit**: `git add src/flaas/truepeak.py && git commit -m "feat: add true-peak estimator" && git push`

**Next**: Task 11 (integrate into analyze command).

---

#### Task 11: Add `--true-peak` flag to analyze
**Type**: Shipping Mode  
**File changes**: `src/flaas/analyze.py`, `src/flaas/cli.py`

**Command**:
```bash
# Agent edits:
# - analyze.py: Add true_peak_dbtp field to AnalysisResult, compute if requested
# - cli.py: Add --true-peak flag to analyze parser

python3 -m compileall src/flaas/analyze.py src/flaas/cli.py

flaas analyze input/test.wav --true-peak
cat data/reports/analysis.json | jq '{peak_dbfs, true_peak_dbtp}'
```

**Expected output**:
```
Compiling ...

data/reports/analysis.json

{
  "peak_dbfs": -13.98,
  "true_peak_dbtp": -13.50
}
```

**Success criteria**: true_peak_dbtp >= peak_dbfs.

**Rollback**: `git checkout -- src/flaas/analyze.py src/flaas/cli.py`

**Commit**: `git add -A && git commit -m "feat: add true-peak to analyze" && git push`

---

#### Task 12: Create stem naming validation module
**Type**: Shipping Mode  
**File changes**: `src/flaas/stems.py` (new)

**Command**:
```bash
cat > src/flaas/stems.py <<'EOF'
from __future__ import annotations
from pathlib import Path
import re

STEM_PATTERN = re.compile(r'^(.+)_(MASTER|VOCAL_LEAD|VOCAL_BG|BASS|DRUMS|KEYS|OTHER)\.wav$')

def parse_stem_filename(path: str | Path) -> tuple[str, str]:
    """
    Parse stem filename into (song_name, role).
    
    Raises ValueError if filename doesn't match contract.
    """
    filename = Path(path).name
    match = STEM_PATTERN.match(filename)
    if not match:
        raise ValueError(f"Invalid stem: {filename}. Expected: {{song}}_{{ROLE}}.wav")
    return match.group(1), match.group(2)

def validate_stem_set(paths: list[str | Path]) -> dict[str, list[str]]:
    """
    Validate stem set. Returns {song_name: [roles]}.
    
    Raises ValueError if:
    - Multiple songs in one set
    - Duplicate roles for same song
    - Invalid naming
    """
    stems = {}
    for path in paths:
        song, role = parse_stem_filename(path)
        if song not in stems:
            stems[song] = []
        if role in stems[song]:
            raise ValueError(f"Duplicate role {role} for song {song}")
        stems[song].append(role)
    
    if len(stems) > 1:
        raise ValueError(f"Multiple songs in stem set: {list(stems.keys())}")
    
    return stems
EOF

python3 -m compileall src/flaas/stems.py

# Test
python3 - <<'PY'
from flaas.stems import parse_stem_filename, validate_stem_set

# Valid
print(parse_stem_filename("track01_VOCAL_LEAD.wav"))

# Invalid (should raise)
try:
    parse_stem_filename("invalid.wav")
except ValueError as e:
    print(f"Correctly rejected: {e}")

# Set validation
files = ["song_MASTER.wav", "song_VOCAL_LEAD.wav"]
print(validate_stem_set(files))
PY
```

**Expected output**:
```
Compiling 'src/flaas/stems.py'...

('track01', 'VOCAL_LEAD')
Correctly rejected: Invalid stem: invalid.wav. Expected: {song}_{ROLE}.wav
{'song': ['MASTER', 'VOCAL_LEAD']}
```

**Success criteria**: Valid names parse, invalid raise ValueError.

**Rollback**: `rm src/flaas/stems.py`

**Commit**: `git add src/flaas/stems.py && git commit -m "feat: add stem naming validation" && git push`

---

#### Task 13: Add `flaas validate-stems` CLI command
**Type**: Shipping Mode  
**File changes**: `src/flaas/cli.py`

**Command**:
```bash
# Agent edits cli.py

flaas validate-stems --help

# Test valid
touch input/song_MASTER.wav input/song_BASS.wav
flaas validate-stems input/song_*.wav

# Test invalid
touch input/bad.wav
flaas validate-stems input/bad.wav
```

**Expected output**:
```
usage: flaas validate-stems [-h] stems [stems ...]

✓ song_MASTER.wav - MASTER
✓ song_BASS.wav - BASS
VALID: 2 stems for 'song'

ERROR: Invalid stem: bad.wav. Expected: {song}_{ROLE}.wav
```

**Success criteria**: Valid stems pass, invalid fail with clear error.

**Rollback**: `git checkout -- src/flaas/cli.py`

**Commit**: `git add src/flaas/cli.py && git commit -m "feat: add validate-stems command" && git push`

---

#### Task 14: Add `--max-iterations` flag to loop
**Type**: Shipping Mode (safety)  
**File changes**: `src/flaas/loop.py`, `src/flaas/cli.py`

**Command**:
```bash
# Agent edits:
# - loop.py: Add iteration counter, check max
# - cli.py: Add --max-iterations arg (default 5)

python3 -m compileall src/flaas/loop.py src/flaas/cli.py

flaas loop input/test.wav --dry --max-iterations 2
```

**Expected output**:
```
Compiling ...

MEASURE: LUFS=-17.72 peak_dBFS=-13.98
CUR_LINEAR: 0.000  DELTA: 0.XXX
DRY_RUN: MASTER :: Utility.Gain += 0.XXX
DONE: planned (dry-run, no OSC)
```

**Success criteria**: Flag accepted, loop respects limit (test with real iterations later).

**Rollback**: `git checkout -- src/flaas/loop.py src/flaas/cli.py`

**Commit**: `git add -A && git commit -m "feat: add max-iterations to loop" && git push`

---

#### Task 15: Add iteration timeline logging
**Type**: Shipping Mode (audit trail)  
**File changes**: `src/flaas/loop.py`

**Command**:
```bash
# Agent edits loop.py to:
# - Write JSONL log per iteration: data/timelines/{timestamp}.jsonl
# - Log: iteration number, timestamp, lufs_i, delta, cur_linear, new_norm

python3 -m compileall src/flaas/loop.py

flaas reset
flaas loop input/test.wav --dry

ls -lh data/timelines/
cat data/timelines/*.jsonl
```

**Expected output**:
```
Compiling 'src/flaas/loop.py'...

MEASURE: ...
DONE: ...

-rw-r--r-- 1 user staff 256 ... data/timelines/2026-02-22T10-30-00.jsonl

{"iteration": 1, "timestamp": "2026-02-22T10:30:00Z", "lufs_i": -17.72, "delta": 0.XXX, ...}
```

**Success criteria**: Timeline file created, JSONL format.

**Rollback**: `git checkout -- src/flaas/loop.py && rm -rf data/timelines/`

**Commit**: `git add src/flaas/loop.py && git commit -m "feat: add timeline logging to loop" && git push`

---

#### Task 16: Add `flaas scan --verbose` (show all param names)
**Type**: Discovery Mode  
**File changes**: `src/flaas/scan.py`, `src/flaas/cli.py`

**Command**:
```bash
# Agent edits:
# - scan.py: Add optional param name query per device (if verbose=True)
# - cli.py: Add --verbose flag to scan parser

python3 -m compileall src/flaas/scan.py src/flaas/cli.py

flaas scan --verbose
cat data/caches/model_cache.json | jq '.tracks[0].devices[0].parameters | length'
```

**Expected output**:
```
Compiling ...

data/caches/model_cache.json

10 (number of Utility parameters)
```

**Success criteria**: Verbose scan includes parameters array.

**Rollback**: `git checkout -- src/flaas/scan.py src/flaas/cli.py`

**Commit**: `git add -A && git commit -m "feat: add verbose param scan" && git push`

---

#### Task 17: Add `flaas doctor` environment check
**Type**: Shipping Mode (reliability)  
**File changes**: `src/flaas/doctor.py` (new), `src/flaas/cli.py`

**Command**:
```bash
cat > src/flaas/doctor.py <<'EOF'
from __future__ import annotations
import sys
from pathlib import Path
from flaas.osc_rpc import OscTarget, request_once

def run_doctor() -> int:
    """Run environment health checks. Returns 0 if all pass."""
    checks = []
    
    # Check 1: Python version
    py_ver = sys.version_info
    py_ok = py_ver >= (3, 11)
    checks.append(("Python >=3.11", py_ok, f"{py_ver.major}.{py_ver.minor}"))
    
    # Check 2: OSC connectivity
    try:
        request_once(OscTarget(), "/live/test", "ok", timeout_sec=2.0)
        osc_ok = True
        osc_msg = "Connected"
    except Exception as e:
        osc_ok = False
        osc_msg = f"{type(e).__name__}"
    checks.append(("OSC connectivity", osc_ok, osc_msg))
    
    # Check 3: Data directories
    dirs = ["data/caches", "data/reports", "data/actions"]
    dirs_ok = all(Path(d).exists() for d in dirs)
    checks.append(("Data directories", dirs_ok, "Present" if dirs_ok else "Missing"))
    
    # Check 4: Input directory
    input_ok = Path("input").exists()
    checks.append(("Input directory", input_ok, "Exists" if input_ok else "Missing"))
    
    # Print results
    for name, ok, msg in checks:
        status = "✓" if ok else "✗"
        print(f"{status} {name}: {msg}")
    
    return 0 if all(ok for _, ok, _ in checks) else 1
EOF

python3 -m compileall src/flaas/doctor.py

# Agent adds to cli.py

flaas doctor
```

**Expected output**:
```
Compiling 'src/flaas/doctor.py'...

✓ Python >=3.11: 3.11
✓ OSC connectivity: Connected
✓ Data directories: Present
✓ Input directory: Exists
```

**Success criteria**: All checks pass (exit 0).

**Rollback**: `rm src/flaas/doctor.py && git checkout -- src/flaas/cli.py`

**Commit**: `git add -A && git commit -m "feat: add doctor environment check" && git push`

---

#### Task 18: Add CHANGELOG.md
**Type**: Documentation  
**File changes**: `CHANGELOG.md` (new)

**Command**:
```bash
cat > CHANGELOG.md <<'EOF'
# Changelog

All notable changes to FLAAS.

## [Unreleased]

## [0.0.2] - 2026-02-22

### Added
- Fingerprint-enforced action application
- Relative delta planning (±0.25 clamp)
- Loop safety stops (max gain 0.99)
- OSC request/response (RPC)
- Real Live set scanning
- Utility Gain control (linear + normalized)
- Export guide command
- Audio verification (PASS/FAIL)
- Complete documentation reorganization
- Engineering notebook with API catalog
- Product & systems spec (spec-v1.md)
- Execution system FSM + stability gates

### Fixed
- OSC ping sends "ok" string
- Parameter values normalized 0..1
- Apply uses relative delta
- Parameter min/max via plural endpoints

## [0.0.1] - 2026-02-21

### Added
- Initial package structure
- Basic CLI
- OSC fire-and-forget ping
- Audio analysis (peak + LUFS)
- Compliance checking
- Action planning
- Apply dry-run
EOF

git add CHANGELOG.md
git commit -m "docs: add changelog" && git push
```

**Expected output**:
```
[main XYZ] docs: add changelog
 1 file changed, 35 insertions(+)
To https://github.com/...
```

**Success criteria**: File created and committed.

**Rollback**: `git reset --soft HEAD~1 && rm CHANGELOG.md`

---

### 8.3 THE Next Task (Do This Now)

**Task 1: Discover `/live/song/export/*` endpoint existence**

**Command to run**:
```bash
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once
try:
    resp = request_once(OscTarget(), "/live/song/export/audio", [], timeout_sec=5.0)
    print(f"SUCCESS: Endpoint exists. Response: {resp}")
except TimeoutError:
    print("TIMEOUT: Endpoint likely does not exist in this AbletonOSC build")
    print("FALLBACK: Manual export remains MVP solution")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
PY
```

---

### 8.4 Acceptance Tests (Definitions of Done)

**MVP (v0.1.0) - ALMOST COMPLETE**

Acceptance test (manual):
```bash
# 1. OSC connectivity
flaas ping --wait  # → ok: ('ok',)

# 2. Scan stability
flaas scan  # → valid JSON, fingerprint present

# 3. Audio analysis
flaas analyze input/test.wav  # → peak + LUFS correct

# 4. Compliance check
flaas check input/test.wav  # → pass/fail flags correct

# 5. Action planning
flaas plan-gain input/test.wav  # → bounded delta, fingerprint embedded

# 6. Dry-run preview
flaas apply --dry  # → action previewed

# 7. Real application
flaas apply  # → APPLIED message, Utility Gain changed

# 8. Readback verification
flaas verify  # → normalized value matches expected

# 9. Loop automation
flaas loop input/test.wav  # → analyze+plan+apply in one command

# 10. Manual export workflow
flaas export-guide  # → settings printed
# (User exports in Ableton)
flaas verify-audio output/master.wav  # → PASS (after iteration)
```

**Pass**: All 10 steps complete without error.

**Blocker**: Step 10 requires manual export (automation pending Task 1-4).

---

**v1.0 (Production-Ready)**

Additional tests (future):
```bash
# 11. Automated export
flaas export --output output/test.wav  # → file appears

# 12. Multi-stem analysis
flaas analyze-stems input/song_*.wav  # → per-stem reports

# 13. EQ control
flaas eq-gain 1 0 --band 2 --gain -3.0  # → EQ changed, verified

# 14. Unit tests
pytest tests/  # → all pass

# 15. Integration tests
pytest tests/integration/  # → requires Ableton

# 16. Stability gates
bash tests/run_gates.sh  # → G1-G5 all pass
```

**Pass**: All 16 steps complete.

---

## Appendix A: Quick Command Reference

**Copy-paste for daily work:**

### Environment Setup
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
flaas --version  # Should print 0.0.2
```

### Pre-Flight Check
```bash
flaas doctor  # (if implemented)
flaas ping --wait
flaas scan
```

### Analysis Workflow
```bash
flaas analyze input/test.wav
flaas check input/test.wav
flaas plan-gain input/test.wav
flaas apply --dry
flaas apply
flaas verify
```

### Loop Workflow
```bash
flaas reset
flaas loop input/test.wav --dry  # Preview
flaas loop input/test.wav        # Execute
```

### Manual Export + Verify
```bash
flaas export-guide
# (Export in Ableton to output/master.wav)
flaas verify-audio output/master.wav
```

### Discovery Probes
```bash
# Query OSC endpoint
python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '[endpoint]', [args]))"

# Check device params
python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/parameters/name', [track, device]))"

# Inspect cache
cat data/caches/model_cache.json | jq '.'
```

### Troubleshooting
```bash
# Category 1: OSC issue
flaas ping --wait
ps aux | grep -i ableton

# Category 3: Fingerprint mismatch
flaas scan && flaas plan-gain input/test.wav

# Category 4: Audio issue
ls -lh input/test.wav
flaas analyze input/test.wav

# Category 6: Packaging issue
pip install -e .
python3 -m compileall src/flaas/
```

### Rollback
```bash
# Before commit
git checkout -- [file]

# After commit (not pushed)
git reset --soft HEAD~1

# After push
# Create fix commit (DO NOT rewrite history)
git add -A && git commit -m "fix: [issue]" && git push
```

---

## Appendix B: Constants + Operational Parameters

### Ports
- AbletonOSC listen: `11000` (UDP)
- AbletonOSC reply: `11001` (UDP)

### Device Assumptions
- Master track ID: `0`
- Utility device ID: `0`
- Utility class name: `StereoGain`
- Utility Gain param ID: `9`

### Targets (from `targets.py`)
- `master_lufs`: `-10.5` LUFS
- `lufs_tolerance`: `±0.5` LU
- `stem_peak_ceiling_dbfs`: `-6.0` dBFS
- `true_peak_ceiling_dbfs`: `-1.0` dBFS (placeholder)

### Safety Clamps
- Delta clamp: `±0.25` linear units (`plan.py`)
- Max gain norm: `0.99` (`loop.py`)
- Normalized value: `[0.0, 1.0]` (all set operations)

### Timeouts
- OSC ping: `2.0s`
- OSC param query: `3.0s`
- Shell command: `30s`
- Export (future): `60s`

### Schema Versions
- `actions.json`: `"1.0"`
- Future artifacts: TBD

---

## Appendix C: Link Integrity Check

**Run periodically to verify cross-references:**

```bash
cd /Users/trev/Repos/finishline_audio_repo/docs/

# Check all markdown internal links
find . -name "*.md" -exec grep -H "\[.*\](" {} \; | \
  grep -v "http" | \
  grep -v "mailto" | \
  while IFS=: read file rest; do
    link=$(echo "$rest" | grep -oP '\]\(\K[^)]+' | head -1)
    if [ ! -z "$link" ]; then
      target="$(dirname $file)/$link"
      if [ ! -f "$target" ]; then
        echo "BROKEN: $file → $link"
      fi
    fi
  done
```

**Expected**: No output (all links valid).

**Fix**: Update broken links, commit as `docs: fix broken links`.

---

## Appendix D: Regeneration Commands

**Run after code changes to keep docs in sync:**

### Unique Line Ledger
```bash
python3 scripts/generate_unique_lines.py
git add docs/reference/unique-lines/
git commit -m "docs: regenerate unique line ledger"
```

### Command List Sync
```bash
# Extract commands from cli.py
grep "sub.add_parser" src/flaas/cli.py | grep -oP '"[a-z-]+"' | tr -d '"' | sort

# Manually update README.md Commands section
# Then commit
```

### Cross-Reference Update
```bash
# After moving files
cd docs/
grep -rn "docs/" . --include="*.md" | grep "\.md" | sort -u
# Manually update links
```

---

**End of Operating Manual v1**

This is the single unified reference for FLAAS. All other docs provide deeper detail on specific areas. When in doubt, start here.

**Next action**: Complete Task 1 (discover export endpoint) to unblock MVP finalization.
