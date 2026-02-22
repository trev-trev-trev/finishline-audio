# FLAAS Product & Systems Architecture Specification v1

**Version**: 1.0  
**Date**: 2026-02-22  
**Status**: Living Document

---

## North Star

FLAAS is a **system-level control layer** for album production that separates technical compliance from creative intent. It provides a programmatic bridge between Ableton Live and Python-based analysis/automation, enabling album-wide consistency through measurable, repeatable corrections. The system treats an album as an **addressable dataset**: every track's audio characteristics, device state, and parameter values become queryable, correctable, and auditable. Success means: creative time is spent on taste decisions, not repetitive cleanup; an entire album can be brought into technical compliance with deterministic rules; and every change is logged, explainable, and reproducible.

---

## 1. MVP Outcomes (Top 10)

**What shipping MVP delivers**:

1. **OSC connectivity established** - Bidirectional communication with Ableton Live via AbletonOSC (ports 11000/11001)
2. **Live set structure visibility** - Query tracks, devices, parameters with fingerprint-based change detection
3. **Audio analysis pipeline** - Peak dBFS + LUFS-I measurement from exported WAV files
4. **Compliance checking** - Automated pass/fail against defined targets (LUFS -10.5 ±0.5, peak <= -6.0 dBFS)
5. **Action planning** - Calculate bounded parameter adjustments (Utility Gain ±0.25 linear delta, clamped)
6. **OSC parameter control** - Set device parameters with fingerprint enforcement and relative delta application
7. **Closed-loop iteration** - analyze → plan → apply workflow with safety stops (max gain norm 0.99)
8. **Audit trail** - All actions logged with schema versioning, fingerprints, timestamps
9. **Terminal-driven workflow** - Every operation validated by single-command probes
10. **Export standardization** - Documented export settings ensuring repeatability

**Explicit Non-Goals for MVP**:
- ❌ Multi-stem support (post-MVP)
- ❌ Device control beyond Utility (EQ, limiter, etc.)
- ❌ Automated Ableton export/re-render
- ❌ True-peak estimation (using peak dBFS approximation)
- ❌ UI/GUI (terminal-only)
- ❌ Real-time audio processing (offline analysis only)
- ❌ Subjective audio evaluation ("sounds better")
- ❌ Creative suggestions or style transfer
- ❌ Waveform copying or "reference track" matching

---

## 2. Two Operating Modes

### DISCOVERY MODE: Maximize Visibility of Ableton

**Purpose**: Systematically map and validate Ableton's surface area before shipping user-facing capabilities.

**Engineering Program: Surface Area Registry**

A formal registry tracking:
- **Endpoints discovered**: OSC paths, request/response formats, quirks
- **Device catalog**: Class names, parameter counts, param ID mappings
- **Parameter semantics**: Value ranges (normalized/linear/dB), clamp behavior
- **Validation status**: Tested in terminal, documented in notebook

**Discovery workflow**:
1. **Hypothesize**: Identify an endpoint (e.g., `/live/device/get/parameters/name`)
2. **Probe**: Run single OSC query via terminal: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/parameters/name', [0,0]))"`
3. **Document**: Add to engineering notebook with exact request/response format
4. **Validate**: Create CLI command that exercises endpoint: `flaas scan`
5. **Register**: Add to surface area registry with validation command

**Current surface area (validated)**:
- Health: `/live/test` (ping with "ok")
- Song: `/live/song/get/num_tracks`, `/live/song/get/track_names`
- Track: `/live/track/get/num_devices`, `/live/track/get/devices/name`, `/live/track/get/devices/class_name`
- Device params: `/live/device/get/parameters/{name,min,max}`, `/live/device/get/parameter/value`, `/live/device/set/parameter/value`

**Unmapped surface (known unknowns)**:
- `/live/song/export/*` - Automated export (VERIFY: does AbletonOSC support?)
- `/live/clip/*` - Clip manipulation
- `/live/scene/*` - Scene control
- `/live/tempo/*` - Tempo/arrangement
- `/live/device/get/parameter/value_string` - Human-readable param values (VERIFY: exists?)
- Device-specific endpoints beyond generic parameter access

**Discovery priorities** (see Section 5: Surface Area Roadmap)

---

### SHIPPING MODE: User-Facing Capabilities

**Purpose**: Deliver value on top of validated surface area.

**Current capabilities** (built on mapped surface):
- ✅ Utility Gain control (track 0, device 0, param 9)
- ✅ Fingerprint-enforced action application
- ✅ Bounded delta planning (±0.25 linear)
- ✅ Loop with safety stops

**Capability development workflow**:
1. **Map surface** (Discovery Mode)
2. **Build primitive** (e.g., `util.set_utility_gain_linear`)
3. **Validate primitive** in terminal: `flaas util-gain-linear 0 0 0.5 && flaas verify`
4. **Compose workflow** (e.g., `loop.run_loop` uses primitive)
5. **Document golden path**: Add to terminal cheatsheet

**Principles**:
- Never ship a capability without underlying surface mapped
- Every capability has a single-command validation
- All operations are idempotent where possible (OSC sets are not; document race conditions)

---

## 3. System Boundaries

### Inside System Scope

**FLAAS controls**:
- Python codebase (`src/flaas/`)
- CLI commands (`flaas *`)
- Data artifacts (caches, reports, actions)
- OSC client (sends messages)
- Audio analysis (reads exported WAV files)
- Planning logic (decision rules)

**FLAAS queries but does not control**:
- Ableton Live state (read-only via OSC queries)
- AbletonOSC plugin (installed separately, not modified)

### Outside System Scope

**User responsibilities**:
- Ableton Live running with AbletonOSC loaded
- Manual audio export (until automated export mapped)
- Creative decisions (arrangement, sound design, performance)
- Track role assignment (manual naming convention: "MASTER", "VOCAL_LEAD", etc.)

**External dependencies**:
- AbletonOSC plugin (ideoforms/AbletonOSC on GitHub)
- Python 3.11+
- Audio libraries (soundfile, pyloudnorm)
- OSC library (python-osc)

**Out of scope**:
- Ableton Live internal state (clips, automation, MIDI)
- Real-time audio (only offline exported files)
- DAW other than Ableton Live
- Mastering "AI" or subjective evaluation

---

## 4. Architecture + Data Flow

### System Diagram

```
┌──────────────────┐
│  Ableton Live    │
│  (with tracks,   │
│   devices,       │
│   parameters)    │
└────────┬─────────┘
         │
         │ (OSC UDP 11000/11001)
         │
┌────────▼─────────┐
│  AbletonOSC      │
│  (Remote Script) │
│  - Listens 11000 │
│  - Replies 11001 │
└────────┬─────────┘
         │
         │ (request_once / send_message)
         │
┌────────▼─────────────────────────────────────────┐
│  FLAAS CLI (Python)                              │
│  ┌─────────────────────────────────────────────┐ │
│  │ Commands:                                   │ │
│  │ - flaas ping / scan / analyze / check      │ │
│  │ - flaas plan-gain / apply / verify / loop  │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Core Modules:                               │ │
│  │ - osc_rpc: Request/response OSC             │ │
│  │ - scan: Live set structure + fingerprint   │ │
│  │ - analyze: Audio DSP (peak, LUFS)          │ │
│  │ - plan: Decision logic (LUFS error → gain) │ │
│  │ - apply: OSC parameter sets (relative Δ)   │ │
│  └─────────────────────────────────────────────┘ │
└───────────┬──────────────┬──────────────┬────────┘
            │              │              │
            ▼              ▼              ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│ data/caches/   │  │ data/reports/│  │ data/actions/│
│ model_cache.   │  │ analysis.json│  │ actions.json │
│ json           │  │ check.json   │  │              │
│ (fingerprint)  │  │              │  │ (schema v1.0)│
└────────────────┘  └──────────────┘  └──────────────┘
         │                   │                  │
         └───────────────────┴──────────────────┘
                             │
                  (user inspection via cat/jq)
                             │
                             ▼
                      ┌─────────────┐
                      │  Terminal   │
                      │  (stdout)   │
                      └─────────────┘
```

### Data Flow: Golden Path (flaas loop)

1. **Pre-flight check**: Query Utility Gain (verify not already maxed)
   - OSC: `/live/device/get/parameter/value [0, 0, 9]`
   - If norm >= 0.99 → STOP (safety)

2. **Analyze audio**: Read exported WAV file
   - Load: `soundfile.read(wav_path)` → numpy array
   - Compute: peak dBFS (`20*log10(max(abs(audio)))`), LUFS-I (BS.1770)
   - Write: `data/reports/analysis.json`

3. **Plan actions**: Calculate gain adjustment
   - LUFS error: `target (-10.5) - measured`
   - Raw delta: `err_db / 12.0` (rough scaling)
   - Clamp: `±0.25` linear units
   - Query: Current Live set fingerprint via OSC scan
   - Write: `data/actions/actions.json` (includes fingerprint)

4. **Validate fingerprint**: Re-scan Live set
   - If current fingerprint ≠ actions fingerprint → ABORT (set changed)

5. **Apply actions**: Set Utility Gain parameter
   - Read: Current Utility Gain (OSC get parameter value)
   - Compute: `new = current + delta` (relative application)
   - Set: OSC `/live/device/set/parameter/value [0, 0, 9, new_norm]`
   - Verify: Read back new value

6. **Report**: Print before/after values to stdout

### Cache Artifacts

**`data/caches/model_cache.json`** (ScanResult schema):
```json
{
  "ok": bool,
  "note": "scan status",
  "created_at_utc": "ISO8601",
  "num_tracks": int,
  "tracks": [
    {
      "track_id": int,
      "name": string,
      "num_devices": int,
      "devices": [{"index": int, "name": string, "class_name": string}]
    }
  ],
  "fingerprint": "SHA256 hex (64 chars)"
}
```
- **Producer**: `scan.write_model_cache()`
- **Consumers**: `plan` (fingerprint), `apply` (fingerprint validation)
- **Staleness**: Fingerprint-based (changes when tracks/devices modified)

**`data/actions/actions.json`** (ActionsFile schema v1.0):
```json
{
  "schema_version": "1.0",
  "created_at_utc": "ISO8601",
  "live_fingerprint": "SHA256 hex or null",
  "actions": [
    {
      "track_role": "MASTER",
      "device": "Utility",
      "param": "Gain",
      "delta_db": float  // Actually linear delta (-1..+1), legacy name
    }
  ]
}
```
- **Producer**: `plan.write_plan_gain_actions()`
- **Consumers**: `apply` (enforces fingerprint match)
- **Safety**: RuntimeError if fingerprint mismatch

---

## 5. Surface Area Roadmap (Prioritized)

### Tier 1: MVP Complete (Current)
**Status**: ✅ Mapped and validated

| Surface | Endpoints | Unlocks | Validation |
|---------|-----------|---------|------------|
| OSC ping | `/live/test` | Connectivity test | `flaas ping --wait` |
| Song structure | `/live/song/get/num_tracks`, `/live/song/get/track_names` | Track discovery | `flaas scan` |
| Track devices | `/live/track/get/num_devices`, `/live/track/get/devices/{name,class_name}` | Device discovery | `flaas scan` |
| Device params | `/live/device/get/parameters/{name,min,max}`, `/live/device/get/parameter/value`, `/live/device/set/parameter/value` | Utility Gain control | `flaas util-gain-norm 0 0 0.5 && flaas verify` |

### Tier 2: Next MVP Blocks (High Priority)
**Status**: 🔍 Discovery required

| Surface | Endpoints (Hypothesized) | Unlocks | Discovery Probe | Priority |
|---------|--------------------------|---------|-----------------|----------|
| **Automated export** | `/live/song/export/*` (VERIFY exists) | Eliminate manual export step | `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/export/audio', [...]))"` | **P0** |
| **EQ Eight params** | Already mapped (generic param access) | EQ cuts for mud/harsh/rumble | `python3 -c "from flaas.scan import scan_live; s=scan_live(); eq_device = next(d for d in s.tracks[0].devices if 'EQ' in d.class_name); print(eq_device)"` | **P1** |
| **Limiter params** | Already mapped (generic param access) | Ceiling enforcement | Similar to EQ discovery | **P1** |
| **Track routing** | `/live/track/get/input_routing_type`, `/live/track/get/output_routing_type` (VERIFY) | Stem routing validation | Discovery probe needed | P2 |

### Tier 3: Extended Capabilities (Post-MVP)
**Status**: 🚧 Future exploration

| Surface | Endpoints (Hypothesized) | Unlocks | Validation | Priority |
|---------|--------------------------|---------|------------|----------|
| Clip manipulation | `/live/clip/*` | Clip-level automation | TBD | P3 |
| Scene control | `/live/scene/*` | Scene triggers for live performance | TBD | P3 |
| Tempo/arrangement | `/live/song/get/tempo`, `/live/song/set/tempo`, `/live/song/get/arrangement_overdub` | Tempo-aware processing | TBD | P3 |
| Mixer controls | `/live/track/get/volume`, `/live/track/set/volume`, `/live/track/get/panning` | Track-level mix automation | TBD | P4 |
| MIDI control | `/live/clip/get/notes`, `/live/clip/set/notes` | Algorithmic composition | TBD | P5 |

**Discovery Protocol**:
1. Check AbletonOSC GitHub docs/wiki for endpoint existence
2. Run exploratory probe in Python REPL
3. Document request/response format in engineering notebook
4. Create wrapper function with validation
5. Add CLI command that exercises endpoint
6. Update surface area registry

**VERIFY Tags** (need confirmation):
- `/live/song/export/*` - Does AbletonOSC support automated export?
- `/live/device/get/parameter/value_string` - Human-readable param values?
- `/live/track/get/input_routing_type` - Routing introspection?
- Device-specific shortcuts (e.g., `/live/eq/set_band` vs generic param access)?

---

## 6. Audio Intelligence Roadmap

### Current (MVP)
**Implemented**:
- **Peak dBFS**: `20 * log10(max(abs(audio)))`
- **LUFS-I** (Integrated Loudness): BS.1770-4 / EBU R 128 via `pyloudnorm.Meter`
- **Compliance targets**: LUFS -10.5 ±0.5 LU, peak <= -6.0 dBFS
- **Gain planning**: LUFS error → linear delta mapping (`err_db / 12.0`, clamped ±0.25)

### Near-Term (Post-MVP)
**Planned**:

1. **True-peak estimation** (P1)
   - Oversample to 192kHz (4x)
   - Compute peak on oversampled signal
   - Target: -1.0 dBTP (true-peak ceiling)
   - Validation: Compare offline true-peak vs peak dBFS on known files

2. **Band energy analysis** (P1)
   - Sub-bass: 20-60 Hz (rumble detection)
   - Low-mid: 200-500 Hz (mud detection)
   - High-mid: 2-6 kHz (harshness detection)
   - High: 8-16 kHz (air/sibilance)
   - Compute: RMS energy per band, normalized to full-band RMS
   - Validation: Synthetic test tones with known frequency content

3. **Multi-stem support** (P1)
   - Per-stem peak/LUFS analysis
   - Stem naming contract: `{song}_{role}.wav` (e.g., `track01_VOCAL_LEAD.wav`)
   - Cross-stem checks: bass != vocal EQ rules
   - Validation: Multi-stem test set with known roles

4. **Macro EQ/Compression controls** (P2)
   - Map EQ Eight band parameters (freq, gain, Q, type)
   - Map Compressor parameters (threshold, ratio, attack, release)
   - Create device adapters with musical units
   - Validation: Set EQ cut, read back, verify in Ableton

### Future (v2+)
**Exploratory**:

1. **Mix profiles** (P3)
   - **Definition**: A mix profile is a named set of numeric targets and parameter mappings
   - **Example**: `"Clean Mastering"` profile:
     ```json
     {
       "name": "Clean Mastering",
       "targets": {
         "master_lufs": -10.5,
         "master_peak_dbfs": -1.0,
         "stem_peak_dbfs": -6.0,
         "sub_rumble_max_dbfs": -40.0,
         "mud_ratio_max": 0.3,
         "harshness_peak_max_dbfs": -15.0
       },
       "param_mappings": {
         "utility_gain_range": [-12.0, 12.0],
         "eq_cut_max_db": -6.0,
         "limiter_ceiling": -0.5
       }
     }
     ```
   - **NOT**: Waveform copying, "make it sound like X artist", subjective quality
   - **IS**: Numeric compliance targets customized per genre/use case
   - Validation: Load profile, run analysis, verify targets applied

2. **Stem-level statistics** (P3)
   - Crest factor (dynamic range)
   - Stereo width (correlation)
   - Spectral centroid (brightness)
   - Per-stem LUFS contributions
   - Validation: Known test stems with measured properties

3. **Reference track guidance** (P4, constrained)
   - **Definition**: Extract numeric targets from a reference track (LUFS, peak, band energy ratios)
   - **Example**: Analyze reference → set targets to match reference's LUFS/peak/energy profile
   - **NOT**: Waveform copying, EQ matching, transient cloning
   - **IS**: Target extraction only (user still defines how to achieve targets)
   - Validation: Analyze reference, compare targets to manual measurement

**Principles for audio intelligence**:
- Objective metrics only (no "sounds better" evaluation)
- Explainable decisions (log why each action was taken)
- Bounded corrections (never more than defined clamps)
- Deterministic rules (same input → same output)

---

## 7. Safety + Correctness Invariants

### Fingerprint Enforcement
**Invariant**: Actions can only be applied if Live set structure hasn't changed since planning.

**Mechanism**:
- `scan_live()` computes SHA256 of track/device structure: `sha256(";".join([f"{tid}:{name}:{num_devices}:{device_classes}"]))`
- `actions.json` includes `live_fingerprint` field
- `apply_actions_osc()` re-scans and compares fingerprints
- If mismatch → `RuntimeError("Live fingerprint mismatch")`

**Bypass**: `apply_actions_osc(enforce_fingerprint=False)` (debugging only)

**Validation**: 
```bash
flaas scan  # Baseline fingerprint
flaas plan-gain input/test.wav  # Capture fingerprint in actions
# (Manually add track in Ableton)
flaas apply  # Should fail with fingerprint mismatch
```

### Parameter Clamps
**Invariant**: Never set parameters outside their valid ranges.

**Mechanisms**:
1. **Delta clamp** (planning): `±0.25` linear units (prevents large jumps)
2. **Absolute clamp** (setting): `[0.0, 1.0]` normalized (OSC requirement)
3. **Max gain stop** (loop): `norm >= 0.99` (prevents runaway iteration)

**Validation**:
```bash
flaas reset  # Start at 0.5
flaas loop input/test.wav  # Run multiple iterations
flaas verify  # Should never exceed 0.99
```

### Stop Conditions
**Invariant**: Iteration must terminate (no infinite loops).

**Mechanisms**:
1. **Utility near max**: If `verify_master_utility_gain() >= 0.99` → early exit with message
2. **Fingerprint mismatch**: Actions rejected (see above)
3. **Manual iteration cap**: User controls loop repetition (no auto-repeat in MVP)

**Future**: Max iteration count (e.g., 2 cycles max, then require user confirmation)

### Schema Versioning
**Invariant**: Data artifacts are versioned to detect incompatibilities.

**Current schemas**:
- `actions.json`: `schema_version: "1.0"`
- Future: Reject or migrate old schemas

**Validation**: Load `actions.json`, check `schema_version` field matches expected

### Audit Trail
**Invariant**: All changes are logged and explainable.

**Current logging**:
- **Stdout**: All commands print before/after values
- **Timestamps**: All artifacts include `created_at_utc` (ISO8601)
- **Fingerprints**: Live set state captured in actions

**Future enhancements**:
- Write `data/timelines/{timestamp}.log` for each run
- Include: command executed, artifacts written, OSC messages sent/received
- Replay capability: Re-run from log file

**Validation**: Every artifact has `created_at_utc`, every action has `live_fingerprint`

---

## 8. Definitions of Done

### MVP Definition of Done
**Gate**: All acceptance tests pass.

**Acceptance tests**:

1. **OSC connectivity**
   ```bash
   flaas ping --wait
   # Expected: ok: ('ok',)
   ```

2. **Live set scan**
   ```bash
   flaas scan
   cat data/caches/model_cache.json | jq '.ok'
   # Expected: true
   ```

3. **Audio analysis**
   ```bash
   flaas analyze input/test.wav
   cat data/reports/analysis.json | jq '{lufs_i, peak_dbfs}'
   # Expected: Numeric values (LUFS ~ -17, peak ~ -14 for test sine)
   ```

4. **Compliance check**
   ```bash
   flaas check input/test.wav
   cat data/reports/check.json | jq '{pass_lufs, pass_peak}'
   # Expected: pass flags (false for test sine, which is quiet)
   ```

5. **Action planning**
   ```bash
   flaas plan-gain input/test.wav
   cat data/actions/actions.json | jq '.actions[0].delta_db'
   # Expected: Positive delta (test sine is below target)
   ```

6. **Dry-run application**
   ```bash
   flaas apply --dry
   # Expected: DRY_RUN: MASTER :: Utility.Gain += 0.XXX
   ```

7. **Real application**
   ```bash
   flaas reset  # Start from known state
   flaas apply
   # Expected: APPLIED: Utility.Gain X.XXX -> Y.YYY
   ```

8. **Verification**
   ```bash
   flaas verify
   # Expected: Numeric value (0.0-1.0)
   ```

9. **Fingerprint enforcement**
   ```bash
   flaas scan && flaas plan-gain input/test.wav
   # (Manually modify Live set: add track)
   flaas apply
   # Expected: RuntimeError: Live fingerprint mismatch
   ```

10. **Loop safety stop**
    ```bash
    flaas reset
    for i in {1..10}; do flaas loop input/test.wav; done
    # Expected: Eventually prints "STOP: utility gain already near max"
    ```

**Exit criteria**: All 10 tests pass consecutively.

---

### v1 Definition of Done
**Gate**: Multi-stem support + EQ/limiter control.

**Acceptance tests** (additional to MVP):

1. **Multi-stem analysis**
   ```bash
   flaas analyze-stems input/track01_*.wav
   # Expected: Per-stem reports
   ```

2. **EQ Eight control**
   ```bash
   flaas eq-cut 0 1 --band 2 --freq 320 --gain -2.0 --q 2.0
   flaas verify-eq 0 1 --band 2
   # Expected: EQ parameters set and verified
   ```

3. **Limiter ceiling**
   ```bash
   flaas limiter-ceiling 0 2 --dbfs -0.5
   # Expected: Limiter ceiling set
   ```

4. **True-peak analysis**
   ```bash
   flaas analyze input/test.wav --true-peak
   cat data/reports/analysis.json | jq '.true_peak_dbtp'
   # Expected: True-peak value (should be higher than peak dBFS)
   ```

5. **Automated export** (if mapped)
   ```bash
   flaas export --track master --format wav
   # Expected: Export triggered in Ableton, file written to output/
   ```

**Exit criteria**: MVP + 5 additional tests pass.

---

### v2 Definition of Done
**Gate**: Mix profiles + reference track targets.

**Acceptance tests** (additional to v1):

1. **Load mix profile**
   ```bash
   flaas load-profile profiles/clean_mastering.json
   flaas check input/test.wav
   # Expected: Compliance checked against profile targets
   ```

2. **Reference track analysis**
   ```bash
   flaas analyze-reference input/reference.wav --extract-targets
   cat data/profiles/reference_targets.json
   # Expected: Numeric targets (LUFS, peak, band energies) extracted
   ```

3. **Stem-level statistics**
   ```bash
   flaas stem-stats input/track01_*.wav
   # Expected: Per-stem crest factor, stereo width, spectral centroid
   ```

**Exit criteria**: v1 + 3 additional tests pass.

---

## 9. Risks + Mitigations (Top 10)

### 1. OSC Communication Failures
**Risk**: AbletonOSC not responding, timeouts, missing replies.

**Likelihood**: High (network fragility, Ableton crashes, port conflicts)

**Impact**: All operations fail

**Mitigation**:
- Pre-flight connectivity check: `flaas ping --wait` (explicit in workflow)
- Timeout defaults: 2.0s (3.0s for param queries)
- Error messages: Clear diagnostics ("TimeoutError: check Ableton running + AbletonOSC loaded")
- Manual recovery: `flaas scan` to re-establish connection

**Validation**: Unplug network, run `flaas ping --wait` → expect clear timeout error

---

### 2. Fingerprint Mismatches (Stale Actions)
**Risk**: User modifies Live set between `plan` and `apply`, causing actions to target wrong parameters.

**Likelihood**: Medium (user workflow variability)

**Impact**: Actions applied to wrong tracks/devices (data corruption)

**Mitigation**:
- Fingerprint enforcement (mandatory by default)
- Clear error message with recovery steps: "RuntimeError: Live fingerprint mismatch. Run: flaas scan && flaas plan-gain <wav>"
- Audit trail: Fingerprint logged in actions.json

**Validation**: Run `flaas plan-gain`, modify Live set, run `flaas apply` → expect rejection

---

### 3. Parameter Value Mapping Errors
**Risk**: Incorrect conversion between linear/dB/normalized units.

**Likelihood**: Medium (device-specific quirks, undocumented ranges)

**Impact**: Wrong parameter values set (too loud, too quiet, unexpected behavior)

**Mitigation**:
- Device adapters abstract value conversion (e.g., `set_utility_gain_linear`)
- Query parameter min/max from AbletonOSC (validated ranges)
- Clamp all values before setting (never exceed [0, 1] normalized)
- Verification after setting: Read back and compare

**Validation**: Set known value, read back, verify match within tolerance

---

### 4. Audio Export Inconsistency
**Risk**: User exports with different settings (normalization on, wrong sample rate, dither variations).

**Likelihood**: High (manual step, no enforcement)

**Impact**: Analysis unreliable, wrong corrections applied

**Mitigation**:
- **MVP**: Document export settings (`flaas export-guide`)
- **v1**: Automated export via OSC (eliminates manual step)
- **Future**: Verify WAV metadata (sample rate, bit depth) before analysis

**Validation**: Export with normalization on, analyze → expect warning/failure

---

### 5. Runaway Iteration (Infinite Loop)
**Risk**: Loop continues indefinitely, repeatedly applying gain.

**Likelihood**: Low (safety stops implemented)

**Impact**: Utility Gain maxed out, potential clipping

**Mitigation**:
- Max gain stop: `norm >= 0.99` → early exit
- Delta clamp: `±0.25` (small increments)
- Manual iteration (no auto-repeat in MVP)
- **Future**: Max iteration cap (2 cycles)

**Validation**: Run loop 10+ times, verify stops when near max

---

### 6. Silent Audio False Triggers
**Risk**: Silence causes ratio-based metrics (mud, harshness) to false-trigger due to division by ~zero.

**Likelihood**: High (intros, outros, gaps)

**Impact**: Spurious detections, unnecessary corrections

**Mitigation** (post-MVP):
- Activity masking: Compute RMS per frame, threshold at -50 dBFS
- Ignore frames where RMS below threshold
- Log masked frames in analysis report

**Validation**: Analyze audio with 5s silence, verify no detections in silent regions

---

### 7. Concurrent Modification (Race Conditions)
**Risk**: Ableton state changes while OSC query in flight.

**Likelihood**: Low (OSC queries are fast, ~10-50ms)

**Impact**: Stale data, fingerprint mismatch on next operation

**Mitigation**:
- Fingerprint enforcement catches stale scans
- Re-scan on fingerprint mismatch (idempotent)
- **No retry logic** (fail fast, deterministic errors)

**Validation**: Modify Live set during `flaas scan`, run `flaas apply` → expect rejection

---

### 8. Missing AbletonOSC Installation
**Risk**: User doesn't have AbletonOSC installed or configured.

**Likelihood**: High (first-time setup)

**Impact**: All OSC operations fail

**Mitigation**:
- Clear error message: "TimeoutError: AbletonOSC not responding. Install: <URL>"
- Sanity check in docs: `flaas ping --wait` (explicit first step)
- Setup guide in README with validation command

**Validation**: Disable AbletonOSC, run `flaas ping` → expect helpful error

---

### 9. Schema Version Drift
**Risk**: Old actions.json loaded with newer code (incompatible schema).

**Likelihood**: Low (v1.0 is stable, no migrations yet)

**Impact**: Parse errors, wrong field access, silent failures

**Mitigation**:
- Schema version field in all artifacts (`schema_version: "1.0"`)
- **Future**: Version check before load, reject incompatible schemas
- **Future**: Migration scripts for schema upgrades

**Validation**: Manually edit actions.json `schema_version: "0.9"`, run `flaas apply` → expect version error

---

### 10. Unvalidated Discovery (Unmapped Surface)
**Risk**: Attempt to use OSC endpoint that doesn't exist or has undocumented behavior.

**Likelihood**: High (AbletonOSC is large, not fully mapped)

**Impact**: Timeout, wrong data returned, silent failure

**Mitigation**:
- **Discovery Mode protocol** (formal surface area registry)
- VERIFY tags for unconfirmed endpoints
- Terminal probe before shipping capability
- Engineering notebook documents all validated endpoints

**Validation**: Each new endpoint has documented validation command

---

## 10. Prioritization Principles

**How to choose next work** (ranked criteria):

### 1. Impact × Unlocks
**Question**: Does this work unlock multiple downstream capabilities?

**High priority**:
- Automated export (unlocks full closed-loop automation)
- EQ Eight control (unlocks mud/harsh/rumble corrections)
- Multi-stem support (unlocks per-stem analysis)

**Low priority**:
- UI polish (terminal-first MVP)
- Clip manipulation (not on critical path)

### 2. Surface Area Discovery
**Question**: Does this require mapping new Ableton surface?

**Discovery Mode first**: Map endpoint, validate, document before shipping capability.

**Shipping Mode second**: Build user-facing feature on validated surface.

**Priority order**:
1. Discover essential surface (export, EQ, limiter)
2. Ship capabilities on mapped surface
3. Discover extended surface (clips, scenes, tempo)

### 3. Terminal Testability
**Question**: Can this be validated with a single terminal command?

**Requirement**: Every feature must have deterministic probe.

**Examples**:
- ✅ `flaas verify` → read parameter value
- ✅ `flaas scan` → validate fingerprint
- ❌ "UI looks good" → subjective, no terminal validation

### 4. Stability Over Features
**Question**: Is existing functionality reliable?

**Rule**: Fix bugs and edge cases before adding features.

**Priority order**:
1. Safety invariants (fingerprint, clamps)
2. Error handling (clear messages, recovery steps)
3. Repeatability (deterministic, auditable)
4. New capabilities

### 5. Manual → Automated
**Question**: Can we eliminate manual steps?

**Progression**:
1. Manual (documented checklist)
2. Semi-automated (CLI command + manual verification)
3. Fully automated (closed-loop)

**Example**: Export workflow:
- MVP: Manual export with `flaas export-guide` checklist
- v1: `flaas export` (if AbletonOSC supports)
- v2: Loop triggers export automatically

### 6. Fail Fast Over Retry
**Question**: Should we retry on error?

**Philosophy**: No retries (MVP). Fail fast with clear diagnostics.

**Rationale**:
- Retries hide underlying issues
- OSC queries are fast (~10-50ms)
- User can manually retry if transient

**Exception**: Future consideration for read operations only (never writes).

---

## 11. Edge Cases + Stability Constraints

### OSC Race Conditions
**Scenario**: Ableton state changes between scan and apply.

**Detection**: Fingerprint mismatch on apply.

**Recovery**: Re-scan and re-plan (idempotent operations).

**Prevention**: Keep scan-to-apply time minimal (<1s for simple operations).

**Validation**:
```bash
flaas scan && flaas plan-gain input/test.wav &
# (Immediately modify Live set)
flaas apply  # Should fail with fingerprint mismatch
```

---

### Missing OSC Replies
**Scenario**: AbletonOSC doesn't respond (timeout).

**Detection**: `TimeoutError` after 2.0s (3.0s for param queries).

**Recovery**: 
1. Check Ableton running: Open Live application
2. Check AbletonOSC loaded: Preferences → Control Surface → AbletonOSC
3. Check ports: `lsof -i :11000 -i :11001`
4. Retry command

**Prevention**: Pre-flight `flaas ping --wait` in documented workflow.

**Validation**: Quit Ableton, run `flaas scan` → expect timeout with recovery instructions

---

### Stale Caches
**Scenario**: `model_cache.json` is old (Live set changed since last scan).

**Detection**: Fingerprint mismatch when loading actions.

**Recovery**: `flaas scan` to regenerate cache (overwrites old).

**Prevention**: Scan is fast (~200ms), always re-scan before planning.

**Validation**: 
```bash
flaas scan  # Generate cache
# (Modify Live set)
flaas plan-gain input/test.wav  # Re-scans automatically, fingerprint updates
```

---

### Fingerprint Collisions (Theoretical)
**Scenario**: Two different Live sets produce same SHA256 fingerprint.

**Likelihood**: Negligible (SHA256 collision probability ~2^-256).

**Impact**: Actions applied to wrong set (if user swapped files).

**Mitigation**: Include track names and device class names in fingerprint (not just counts).

**Detection**: User would notice wrong track names in scan output.

**Recovery**: Manual verification of scan output before apply.

---

### Repeatability Requirements

#### Deterministic Analysis
**Requirement**: Same WAV file → same analysis results (bit-for-bit).

**Current**:
- Peak dBFS: Deterministic (pure math)
- LUFS-I: Deterministic (BS.1770 standard, pyloudnorm library)
- Timestamps: Non-deterministic (real-time clock)

**Validation**: Analyze same file twice, compare results (excluding timestamps).

**Future**: Reproducible timestamps via `SOURCE_DATE_EPOCH` environment variable.

---

#### Environment Checks
**Requirement**: Validate environment before running (catch setup issues early).

**Current checks**:
- Python version: `>=3.11` (in pyproject.toml)
- Dependencies: `python-osc`, `numpy`, `soundfile`, `pyloudnorm`

**Validation**: `python3 -m compileall src/flaas/` (syntax check).

**Future enhancements**:
- OSC port availability: Check 11000/11001 not in use
- Ableton version: Query via OSC (if supported)
- AbletonOSC version: Compare against known compatible versions

---

#### Log Hashes (Future)
**Requirement**: Every artifact includes hash of inputs for traceability.

**Example** (future):
```json
{
  "analysis": {
    "file": "input/test.wav",
    "file_sha256": "abc123...",
    "lufs_i": -17.72,
    "created_at_utc": "2026-02-22T10:00:00Z"
  }
}
```

**Validation**: Re-analyze same file, verify hash matches.

---

### Reference Track Constraints

#### Numeric Targets Only
**Allowed**:
- Extract LUFS, peak, band energy ratios from reference track
- Set targets to match reference's numeric profile
- Plan corrections to achieve those targets

**Forbidden**:
- Waveform copying (convolution, EQ matching)
- Transient cloning
- "Make it sound like X artist" (subjective)

**Rationale**: Stay within "technical compliance" boundary (objective, measurable).

**Validation**: Reference track analyzer outputs JSON with numeric targets only (no audio processing).

---

#### Target Extraction (Not Matching)
**Definition**: Reference track guidance means:
1. Analyze reference track → extract numeric targets (LUFS, peak, energy ratios)
2. Use those targets for compliance checking (same as manual targets)
3. User's audio is corrected to meet targets (not to match reference's waveform)

**Example**:
```bash
flaas analyze-reference input/reference.wav
# Outputs: {"lufs": -11.5, "peak": -1.2, "sub_energy_ratio": 0.15, ...}

flaas set-targets-from-reference data/profiles/reference_targets.json
# Now compliance checks use reference-derived targets

flaas check input/my_track.wav
# Pass/fail against reference-derived targets (not waveform similarity)
```

**Not allowed**: Spectral matching, phase alignment, transient copying.

---

## 12. Execution Contract (One Atomic Task Per Iteration)

### Workflow Loop
**State machine**: PLAN → EDIT → RUN → OBSERVE → DIAGNOSE → FIX → VERIFY → COMMIT

1. **PLAN**: User/agent defines next single task
   - Example: "Add EQ Eight parameter query"

2. **EDIT**: Agent writes code changes
   - Create `src/flaas/eq8.py` with parameter query function

3. **RUN**: Execute validation command
   - `flaas scan` (includes EQ device discovery)

4. **OBSERVE**: Paste terminal output
   - Output shows EQ Eight device with param_id mappings

5. **DIAGNOSE**: If error, classify error category
   - Example: "TimeoutError" → OSC connectivity issue

6. **FIX**: Apply targeted fix
   - Increase timeout, check Ableton running, retry

7. **VERIFY**: Re-run validation command
   - `flaas scan` succeeds

8. **COMMIT**: Git add/commit/push
   - Commit message: "feat: add EQ Eight parameter discovery"

### Task Atomicity Rules
**What counts as one task**:
- ✅ Add one module with one function + CLI command
- ✅ Fix one parameter mapping bug
- ✅ Add one OSC endpoint wrapper
- ✅ Update one schema version

**What does NOT count as one task**:
- ❌ "Add full multi-stem support" (too broad)
- ❌ "Make the system work" (undefined)
- ❌ "Improve error handling everywhere" (unbounded)

**Task specification format**:
```
**Step NNN: [imperative verb] [object].**

Run:
```bash
<exact commands>
```

Paste output of [specific command].
```

### Terminal Validation Requirement
**Rule**: Every task MUST produce observable terminal output.

**Examples**:
- ✅ `flaas scan` → prints scan result + writes JSON
- ✅ `python3 -m compileall src/flaas/` → prints syntax check
- ✅ `git push` → prints push confirmation

**Anti-pattern**: Changes with no terminal validation (untestable).

### Error Handling Protocol
**On error**:
1. **Classify**: OSC/Config/Schema/Audio/Path/Package (see workflow/protocol.md)
2. **Probe**: Run single diagnostic command
3. **Paste**: Full error output + probe result
4. **Fix**: Targeted change (not shotgun debugging)
5. **Verify**: Re-run original command

**Example**:
```
Error: TimeoutError on flaas scan
Probe: flaas ping --wait
Result: TimeoutError (Ableton not responding)
Fix: Start Ableton Live, load AbletonOSC
Verify: flaas ping --wait → ok: ('ok',)
        flaas scan → success
```

---

## Appendix A: Surface Area Registry (Current State)

### Validated Endpoints

| Endpoint | Request | Response | Validated | CLI Command |
|----------|---------|----------|-----------|-------------|
| `/live/test` | `"ok"` | `("ok",)` | ✅ | `flaas ping --wait` |
| `/live/song/get/num_tracks` | `None` or `[]` | `(int,)` | ✅ | `flaas scan` |
| `/live/song/get/track_names` | `[]` | `(name1, name2, ...)` | ✅ | `flaas scan` |
| `/live/track/get/num_devices` | `[track_id]` | `(track_id, num_devices)` | ✅ | `flaas scan` |
| `/live/track/get/devices/name` | `[track_id]` | `(track_id, name1, name2, ...)` | ✅ | `flaas scan` |
| `/live/track/get/devices/class_name` | `[track_id]` | `(track_id, class1, class2, ...)` | ✅ | `flaas scan` |
| `/live/device/get/parameters/name` | `[track_id, device_id]` | `(track_id, device_id, name1, ...)` | ✅ | `flaas scan` (future: verbose mode) |
| `/live/device/get/parameters/min` | `[track_id, device_id]` | `(track_id, device_id, min1, ...)` | ✅ | Used by `flaas util-gain-linear` |
| `/live/device/get/parameters/max` | `[track_id, device_id]` | `(track_id, device_id, max1, ...)` | ✅ | Used by `flaas util-gain-linear` |
| `/live/device/get/parameter/value` | `[track_id, device_id, param_id]` | `(track_id, device_id, param_id, value)` | ✅ | `flaas verify` |
| `/live/device/set/parameter/value` | `[track_id, device_id, param_id, value]` | None (fire-and-forget) | ✅ | `flaas util-gain-norm 0 0 0.5` |

### Known Quirks (Documented)

1. **Plural vs. Singular**: Must use `/live/device/get/parameters/min` (plural), not `/parameter/min` (singular, doesn't exist)
2. **Response Format**: Prefixes vary (some include track_id, some don't)
3. **Normalized Values**: All parameter values are 0..1 (min/max are in "linear" units, not dB)
4. **No Batch Operations**: Must query each track individually (O(N) complexity)
5. **No Transactions**: Each set is immediate, no rollback

### Discovery Queue (VERIFY Tags)

| Hypothesized Endpoint | Purpose | Discovery Probe |
|----------------------|---------|-----------------|
| `/live/song/export/audio` | Automated export | `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/export/audio', [...]))"` |
| `/live/device/get/parameter/value_string` | Human-readable values | `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/parameter/value_string', [0,0,9]))"` |
| `/live/track/get/input_routing_type` | Routing introspection | Similar probe |
| Device-specific shortcuts (e.g., `/live/eq/set_band`) | Direct EQ control | Check AbletonOSC docs |

---

## Appendix B: Glossary

**Terms**:

- **Surface area**: The set of OSC endpoints, parameters, and device controls exposed by AbletonOSC
- **Fingerprint**: SHA256 hash of Live set structure (tracks, devices) used to detect changes
- **Discovery Mode**: Operating mode focused on mapping/validating Ableton surface area
- **Shipping Mode**: Operating mode focused on delivering user capabilities
- **Atomic task**: Single unit of work with deterministic validation
- **Terminal probe**: Single command that validates a capability
- **Mix profile**: Named set of numeric targets and parameter mappings (NOT subjective evaluation)
- **Linear delta**: Parameter change in device's exposed units (e.g., -1..+1 for Utility Gain)
- **Normalized value**: OSC parameter value in [0, 1] range
- **Clamp**: Safety limit preventing parameter from exceeding bounds

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-22 | Initial specification |

---

**End of Specification v1**
