# FLAAS Roadmap

**Next 20 highest-leverage visibility expansions + milestone definitions.**

**Last updated**: 2026-02-22  
**Current milestone**: MVP (v0.1.0) - 90% complete

---

## MVP Completion (v0.1.0)

**Status**: 9/10 outcomes shipped, 1 blocked.

**Remaining**:
1. ⬜ **Automated export** (P0 - MVP blocker)
   - **What it unlocks**: Eliminate manual export step, full closed-loop automation
   - **Validation**: `flaas export --output output/test.wav && ls -lh output/test.wav`
   - **Blocker**: `/live/song/export/*` endpoint existence unknown (VERIFY needed)
   - **Next**: Run discovery probe (see CURRENT.md Section 7)

**MVP Definition of Done**:
```bash
# Full golden path without manual steps
flaas ping --wait
flaas scan
flaas analyze input/test.wav
flaas plan-gain input/test.wav
flaas apply
flaas export --output output/master.wav  # ← Currently manual
flaas verify-audio output/master.wav
# Expected: PASS (or iterate via loop)
```

---

## Next 20 Visibility Expansions (Prioritized)

### Expansion 1: `/live/song/export/*` (P0 - MVP blocker)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Automated export, full closed-loop  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/export/audio', []))"`  
**Next**: CURRENT.md Section 7 (discovery probe)

---

### Expansion 2: EQ Eight band parameters (P1)
**Status**: 🔍 Discovery needed (surface already mapped via generic param access)  
**What it unlocks**: Mud cuts (200-500 Hz), harshness cuts (2-6 kHz), rumble filters  
**Validation**: `flaas inspect-selected-device` (select EQ Eight in Ableton)  
**Discovery**: Add EQ Eight to a track, select it, run inspect command  
**Next**: See RECEIPTS/2026-02-22_0400_inspect_selected_device.md for tool usage

---

### Expansion 3: Limiter parameters (P1)
**Status**: 🔍 Discovery needed  
**What it unlocks**: True-peak ceiling enforcement, release control  
**Validation**: `flaas inspect-selected-device` (select Limiter in Ableton)  
**Discovery**: Add Limiter to master, select it, run inspect command  
**Expected params**: Ceiling, Release, Gain, Lookahead

---

### Expansion 4: Compressor parameters (P1)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Dynamic range control (threshold, ratio, attack, release)  
**Validation**: `flaas inspect-selected-device` (select Compressor)  
**Expected params**: Threshold, Ratio, Attack, Release, Knee, Makeup, Dry/Wet

---

### Expansion 5: True-peak estimation (P1 - audio intelligence)
**Status**: ⬜ Algorithm needed (no discovery, pure DSP)  
**What it unlocks**: ITU-R BS.1770 compliant peak detection, -1.0 dBTP ceiling  
**Validation**: `flaas analyze input/test.wav --true-peak` (flag to add)  
**Algorithm**: Oversample 4x via `scipy.signal.resample`, compute peak  
**Next**: Implement `truepeak.py` module

---

### Expansion 6: Band energy analysis (P1 - audio intelligence)
**Status**: ⬜ Algorithm needed  
**What it unlocks**: Rumble/mud/harshness detection, EQ planning rules  
**Validation**: `flaas analyze input/test_multiband.wav` (multiband test file)  
**Bands**: Sub (20-60 Hz), Mid (200-500 Hz), High-mid (2-6 kHz), High (8-16 kHz)  
**Next**: Modify `analyze.py` to add band energy fields

---

### Expansion 7: Multi-stem naming + validation (P1)
**Status**: ⬜ Module needed (no Ableton discovery)  
**What it unlocks**: Per-stem analysis, cross-stem EQ rules  
**Validation**: `flaas validate-stems input/song_*.wav`  
**Contract**: `{song}_{ROLE}.wav` (MASTER, VOCAL_LEAD, BASS, DRUMS, etc.)  
**Next**: Implement `stems.py` module with `parse_stem_filename`, `validate_stem_set`

---

### Expansion 8: Track volume/panning (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Track mixer automation, stem balance  
**Endpoints**: `/live/track/get/volume`, `/live/track/set/volume`, `/live/track/get/panning`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/volume', [0]))"`  
**Expected**: `(track_id, volume_normalized)`

---

### Expansion 9: Track routing introspection (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Validate stem routing chains, send/return track validation  
**Endpoints**: `/live/track/get/input_routing_type`, `/live/track/get/output_routing_type`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/output_routing_type', [0]))"`  
**Expected**: Routing type string or enum

---

### Expansion 10: Track mute/solo/arm state (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Track state validation, automated solo workflow  
**Endpoints**: `/live/track/get/mute`, `/live/track/get/solo`, `/live/track/get/arm`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/mute', [0]))"`

---

### Expansion 11: Saturator parameters (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Harmonic saturation control  
**Validation**: `flaas inspect-selected-device` (select Saturator)  
**Expected params**: Drive, Curve, Dry/Wet

---

### Expansion 12: Glue Compressor parameters (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Bus compression control  
**Validation**: `flaas inspect-selected-device` (select Glue Compressor)  
**Expected params**: Attack, Release, Ratio, Threshold, Makeup

---

### Expansion 13: Device bypass state (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: A/B testing (bypass devices for comparison)  
**Endpoints**: `/live/device/get/is_active`, `/live/device/set/is_active`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/device/get/is_active', [0,0]))"`

---

### Expansion 14: Track color (P2)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Role identification (MASTER=red, VOCAL=blue, etc.)  
**Endpoints**: `/live/track/get/color`, `/live/track/set/color`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/color', [0]))"`

---

### Expansion 15: Send levels (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Return track (reverb, delay) control  
**Endpoints**: `/live/track/get/send`, `/live/track/set/send`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/send', [0,0]))"`  
**Note**: Requires return tracks in Live set

---

### Expansion 16: Clip start/end markers (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Clip-level automation, arrangement introspection  
**Endpoints**: `/live/clip/get/start_marker`, `/live/clip/get/end_marker`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/clip/get/start_marker', [0,0]))"`  
**Note**: Requires clip in session view

---

### Expansion 17: Tempo get/set (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Tempo-aware processing, BPM normalization  
**Endpoints**: `/live/song/get/tempo`, `/live/song/set/tempo`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/get/tempo', []))"`

---

### Expansion 18: Scene names (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Scene-based organization, section markers  
**Endpoints**: `/live/song/get/num_scenes`, `/live/scene/get/name`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/get/num_scenes', []))"`

---

### Expansion 19: Master track volume (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Master fader automation  
**Endpoints**: `/live/track/get/volume`, `/live/track/set/volume` (track 0 = master)  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/track/get/volume', [0]))"`

---

### Expansion 20: Arrangement loop points (P3)
**Status**: 🔍 Discovery needed  
**What it unlocks**: Loop region introspection, bounce range control  
**Endpoints**: `/live/song/get/loop_start`, `/live/song/get/loop_length`  
**Validation**: `python3 -c "from flaas.osc_rpc import *; print(request_once(OscTarget(), '/live/song/get/loop_start', []))"`

---

## Post-MVP Milestone (v0.2.0)

**Trigger**: Complete 3 of expansions 2-7 (any combination).

**Definition of Done**:
- At least 3 new device types controlled (e.g., EQ Eight + Limiter + Compressor)
- OR: True-peak + band energy + multi-stem analysis
- All with CLI commands and terminal validation

**Acceptance test**:
```bash
# Example: EQ Eight control
flaas eq-gain 1 0 --band 2 --gain -3.0  # Cut mud
flaas verify-eq 1 0 --band 2  # (if readback implemented)

# Example: True-peak
flaas analyze input/test.wav --true-peak
cat data/reports/analysis.json | jq '{peak_dbfs, true_peak_dbtp}'
```

---

## Production Milestone (v1.0.0)

**Trigger**: 
- All of expansions 1-7 complete
- Unit test suite (pytest)
- Integration test harness
- All gates G1-G5 passing

**Definition of Done**:
```bash
# Full automated workflow (no manual steps)
flaas doctor  # Environment check
flaas loop input/test.wav  # Iterate to convergence
flaas export --output output/master.wav  # Automated export
flaas verify-audio output/master.wav  # Should print PASS

# Test suite
pytest tests/ -v  # All pass

# Stability
bash tests/run_gates.sh  # G1-G5 all pass
```

---

## Decision Rules (Prioritization)

**When to work on discovery** (expansions 1-20):
- High-leverage (unlocks multiple capabilities)
- Low-risk (read-only endpoint probes)
- Fast validation (single command)

**When to work on shipping** (post-discovery):
- Discovery already validated
- Clear user value (not just "nice to have")
- Terminal-testable

**When to work on hardening** (tests, gates, docs):
- After shipping 3+ capabilities
- Before milestone bump (v0.1 → v0.2)
- When reliability becomes blocker

**Use this roadmap**: Pick highest P0/P1 item, run discovery, validate, ship.

---

**Regenerate after**: Major milestone, 5+ receipts, or priorities change.
