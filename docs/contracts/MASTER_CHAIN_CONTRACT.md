# Master Chain Contract

**Status**: PERMANENT (canon)  
**Scope**: Device order, invariants, and preflight rules

---

## Contract

**Master track device chain structure**:
```
[Track Audio] → [Device 0] → [Device 1] → ... → [Device N] → [Master Fader] → [Output]
```

**Signal flow**:
1. Track audio (all tracks summed)
2. Master devices (in order, 0 to N)
3. Master fader (post-processing volume)
4. Output (speakers, export)

---

## Invariants

### 1. Master Fader = 0.0 dB

**Why**: Master fader is POST-device chain
- Boosting fader bypasses all devices (Limiter, EQ, compression)
- Defeats peak control (can exceed Limiter ceiling)
- Breaks measurement predictability

**Verified**: Empirically observed in experiments (fader +6 dB → peak exceeded -6 dBFS limiter ceiling)

**Enforcement**: Pre-flight check (OSC read if available, user confirm if not)

---

### 2. Limiter Is Last

**Why**: Limiter is final peak catcher
- Must see final signal level before output
- Any device after Limiter can re-introduce peaks
- Chain order matters for peak safety

**Verification**: Pre-flight check reads device names, verifies Limiter is last

---

### 3. Compression Before Limiting

**Why**: Limiter alone cannot achieve loudness targets
- Limiter reduces dynamic range but hits diminishing returns
- Compression raises average level (RMS) more efficiently
- Saturation/soft clip adds density without harsh limiting

**Standard chain**: Compression → Saturation → Limiting

---

### 4. No Bypassed Devices

**Why**: Bypassed devices break signal flow
- Export may not reflect expected chain
- Measurement won't match expectations
- Defeats closed-loop optimization

**Verification**: Preflight check should verify active state (if OSC endpoint exists)

---

## Pre-Flight Checks

**File**: `src/flaas/preflight.py`

**Function**: `run_preflight_checks(track_id, target) -> bool`

**Checks**:
1. **Master fader at 0.0 dB**
   - Try OSC read: `/live/track/get/volume`
   - If fails: User must confirm visually
   - Tolerance: ±0.5 dB

2. **Device order correct**
   - Read: `/live/track/get/devices/name`
   - Verify: Glue → Saturator → Limiter (Saturator optional)
   - Fail if Limiter not last

3. **Devices exist**
   - Verify Glue Compressor exists
   - Verify Limiter exists
   - Warn if Saturator missing (optional but recommended)

**Failure behavior**: Return False, print diagnostics, abort optimization

---

## Standard Master Chain (Recommended)

**Minimal**:
```
Utility → EQ Eight → Glue Compressor → Limiter
```

**Recommended** (for maximum loudness):
```
Utility → EQ Eight → Glue Compressor → Saturator → Limiter
```

**Optional additions** (genre-dependent):
```
Utility → EQ Eight → Multiband Compressor → Glue Compressor → Saturator → Limiter → [Vintage/Character plugins]
```

**Key**: Limiter must be LAST

---

## Device Resolution at Runtime

**Never hardcode device IDs** (they change when devices added/removed)

**Always resolve by name**:
```python
device_id = resolve_device_id_by_name(track_id, "Glue Compressor", target)
```

**Case-insensitive matching**:
- "glue compressor" matches "Glue Compressor"
- "limiter" matches "Limiter"
- "saturator" matches "Saturator"

**Response format**: `/live/track/get/devices/name` returns `(track_id, name0, name1, ...)`
- Drop first element (track_id)
- Match against remaining names

---

## Parameter Resolution at Runtime

**Never hardcode parameter IDs** (they change when presets loaded)

**Always resolve by name**:
```python
params = resolve_device_params(track_id, device_id, target)
param_info = params["Threshold"]  # {"id": 2, "min": -60.0, "max": 0.0}
```

**Normalization**: Convert dB → [0,1] using min/max from OSC

---

## Export Settings (Required)

**Ableton Live**:
- File → Export Audio/Video
- Rendered Track: **Master**
- Normalize: **OFF**
- Loop/selection: Set to desired segment

**Output folder**: `/Users/trev/Repos/finishline_audio_repo/output`

**Filename convention**: Descriptive (e.g., `master_loud_preview.wav`, `master_iter3.wav`)

---

## Failure Modes & Proofs

**Symptom**: Peak exceeds expected limit
- **Cause**: Master fader boosted OR Limiter not last OR Limiter bypassed
- **Proof**: Set Limiter ceiling -20 dB, export, measure (should see -20 peak)

**Symptom**: Export silent
- **Cause**: Master track muted OR wrong Rendered Track
- **Proof**: Mute Master, export (should be silent), unmute, re-export (should be normal)

**Symptom**: LUFS doesn't change despite parameter changes
- **Cause**: Device bypassed OR wrong device ID OR export not rendering Master
- **Proof**: Extreme parameter change (e.g., Glue threshold -60 dB), export, measure (should show effect)

---

## Non-Negotiable Rules

1. Master fader = 0.0 dB (always)
2. Limiter is last device (always)
3. Resolve devices by name at runtime (never hardcode)
4. Run pre-flight checks before optimization (fail fast)
5. Log all changes (JSONL receipts with timestamps)

---

**This master chain contract is permanent. All device control flows from these rules.**
