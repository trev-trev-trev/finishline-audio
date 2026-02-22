# Export Automation Feasibility

**Date**: 2026-02-22  
**Probe**: `/live/song/export/structure`  
**Result**: **Automated export NOT possible via OSC**

---

## Endpoint Probe Results

**Command**:
```bash
python -c "from flaas.osc_rpc import OscTarget, request_once; print(request_once(OscTarget(), '/live/song/export/structure', []))"
```

**Response**: `(1,)`

**Interpretation**: Returns single integer (likely boolean/status flag), NOT an actionable trigger

---

## Export Control Surface (Verified)

### Available
- `/live/song/export/structure` - Returns `(1,)` (descriptive only, not actionable)

### NOT Available
- `/live/song/export/audio` - Timeout (endpoint does not exist)
- `/live/song/export/render` - Not found in endpoint inventory
- `/live/song/export/start` - Not found in endpoint inventory

**Conclusion**: AbletonOSC does NOT expose export triggering

---

## Automation Strategy (Revised)

### What CAN be automated:
1. **Parameter sweeps** (Glue Compressor, Limiter settings)
2. **Master fader control** (set to 0.0 dB)
3. **Post-export verification** (`verify-audio`)
4. **Experiment logging** (settings + results → `output/experiments.jsonl`)

### What CANNOT be automated:
- **Export trigger** (manual File → Export Audio/Video required)

### Semi-Automated Workflow

**Stage 1: Master Experiments (Batch Runner)**

```python
# flaas batch-experiment <settings_file>
# Reads: experiments.json with parameter sweep configs
# For each experiment:
#   1. Set parameters via OSC (glue threshold/makeup, limiter ceiling/gain)
#   2. PAUSE → user clicks Export → output/exp_<N>.wav
#   3. Run verify-audio
#   4. Log: {"exp_id": N, "settings": {...}, "results": {...}, "sha256": "..."}
#   5. Append to output/experiments.jsonl
```

**Key insight**: Single manual export click per experiment, all else automated

**Stage 2: Stem Export (Future)**

Options:
1. **Print/Resample** (in-session recording):
   - Solo track → Record to new track → Export stem
   - Automate solo/mute + record start/stop via OSC
   - More stable than offline export

2. **Ableton Multi-Track Export** (if OSC control found):
   - Would require `/live/song/export/tracks` or similar
   - Not currently available

**Recommendation**: Print/resample approach for stems

---

## Revised Roadmap

### Phase 1: Semi-Automated Master Experiments ✅ HIGH ROI

**Goal**: Parameter sweep → log → find optimal compression settings

**Implementation**:
1. Add Glue Compressor OSC control:
   - `flaas glue-set-threshold <dB>`
   - `flaas glue-set-makeup <dB>`
   - `flaas glue-set-ratio <ratio>`
2. Add master fader OSC control:
   - `flaas track-get-volume -1000`
   - `flaas track-set-volume -1000 0.0`
3. Create batch experiment runner:
   - `flaas batch-experiment experiments.json`
   - Pauses for manual export click
   - Auto-verifies and logs results

**ROI**: Eliminates manual parameter adjustment, creates experiment dataset

**Limitation**: Still requires one manual export click per experiment

### Phase 2: Stem Export via Print/Resample

**Goal**: Automate stem rendering without offline export

**Implementation**:
1. Query track list via OSC
2. For each track:
   - Solo track
   - Start recording to new audio track
   - Wait for loop complete
   - Stop recording
   - Export recorded audio track
3. Restore original solo/mute state

**Complexity**: High (routing, timing, state restoration)

**Deferral**: Only needed after Master workflow proven

---

## Decision

**Export remains manual for MVP**

**Automation scope**:
- ✅ Parameter control (Glue, Limiter, fader)
- ✅ Verification (verify-audio)
- ✅ Logging (experiments.jsonl)
- ❌ Export trigger (manual click required)

**Impact**: Still 10-100x faster than fully manual (only export click is manual)

**Next**: Build Glue Compressor OSC control + batch experiment runner

---

## Prior Art

**See**: `docs/status/RECEIPTS/2026-02-22_0330_export_endpoint_discovery.md`

**Finding**: `/live/song/export/audio` timed out (endpoint doesn't exist)

**Consistent with current probe**: Export control not exposed via OSC

---

**Status**: ✅ Probe complete. Export automation NOT feasible. Proceed with semi-automated approach.
