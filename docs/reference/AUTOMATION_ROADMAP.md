# Automation Roadmap (Semi-Automated Approach)

**Date**: 2026-02-22  
**Status**: Export trigger NOT available via OSC  
**Approach**: Semi-automated (parameters + verify automated, export manual)

---

## Verified Constraints

**Export trigger**: ❌ NOT available
- `/live/song/export/structure` returns `(1,)` (status flag only)
- `/live/song/export/audio` does not exist (timeout)
- **Manual export click required**

**Parameter control**: ✅ Available
- All `/live/device/set/parameter/value` endpoints functional
- Master fader control available via `/live/track/set/volume`

**Verification**: ✅ Available
- `flaas verify-audio` functional
- Peak + LUFS analysis working

---

## Phase 1: Master Experiments (Semi-Automated)

**Goal**: Parameter sweep → find optimal compression settings

**ROI**: 10-100x faster (only export click is manual)

### 1.1 Add Glue Compressor Control

**New CLI commands**:
```bash
flaas glue-get-param <track_id> <device_id> <param_name>
flaas glue-set-param <track_id> <device_id> <param_name> <value>
```

**Key parameters**:
- `threshold` (dB, range -60 to 0)
- `makeup` (dB, range 0 to 24)
- `ratio` (range 1.0 to 10.0)
- `attack` (ms, range 0.01 to 30)
- `release` (ms, range 0.01 to 1000)

**Implementation**:
1. Generate device map for Glue Compressor (track -1000, device by name)
2. Create `src/flaas/glue_compressor.py` module
3. Wire CLI commands in `src/flaas/cli.py`
4. Add smoke test (read-only, verify param get)

### 1.2 Add Master Fader Control

**New CLI commands**:
```bash
flaas track-get-volume <track_id>
flaas track-set-volume <track_id> <linear_value>
```

**Implementation**:
1. Query `/live/track/get/volume` (returns linear 0.0-1.0)
2. Set `/live/track/set/volume` (linear 0.0-1.0)
3. Add conversion helpers (linear ↔ dB)
4. Add smoke test (get master fader, verify 0.0)

### 1.3 Create Batch Experiment Runner

**New CLI command**:
```bash
flaas batch-experiment experiments.json
```

**Input format** (`experiments.json`):
```json
{
  "experiments": [
    {
      "id": 1,
      "glue": {"threshold": -25, "makeup": 12, "ratio": 4.0},
      "limiter": {"ceiling": -6.0, "gain": 24}
    },
    {
      "id": 2,
      "glue": {"threshold": -28, "makeup": 15, "ratio": 6.0},
      "limiter": {"ceiling": -6.0, "gain": 28}
    }
  ],
  "export_path_template": "output/exp_{id}.wav"
}
```

**Workflow per experiment**:
1. Set master fader to 0.0 dB
2. Set Glue Compressor params (threshold, makeup, ratio)
3. Set Limiter params (ceiling, gain)
4. **PAUSE**: Print `"Export to output/exp_{id}.wav"`, wait for Enter
5. Run `flaas verify-audio output/exp_{id}.wav`
6. Log to `output/experiments.jsonl`:
   ```json
   {"exp_id": 1, "settings": {...}, "results": {"lufs": -13.59, "peak": -6.00, "lufs_pass": false, "peak_pass": true}, "sha256": "abc123...", "timestamp": "2026-02-22T20:00:00Z"}
   ```

**ROI**:
- Manual: 10 experiments × 5 min = 50 min
- Semi-automated: 10 experiments × 30 sec = 5 min
- **10x speedup**

### 1.4 Auto-Adjustment Algorithm (Optional)

**Meta-command**: `flaas auto-tune-master <input_wav> <output_wav>`

**Logic**:
```python
def auto_tune_master(input_wav: str, output_wav: str, max_iterations: int = 10):
    for i in range(max_iterations):
        # Set initial or adjusted params
        set_glue_params(threshold, makeup, ratio)
        set_limiter_params(ceiling, gain)
        
        # Manual export (pause)
        print(f"Export to {output_wav}")
        input("Press Enter...")
        
        # Verify
        result = verify_audio(output_wav)
        if result.lufs_pass and result.peak_pass:
            print("✅ TARGETS HIT")
            return
        
        # Adjust for next iteration
        if result.peak > -6.0:
            gain -= 1.0  # reduce limiter gain
        elif result.lufs < -10.5:
            threshold -= 1.0  # more compression
            makeup += 1.0
            gain += 1.0
        
        print(f"Iteration {i+1}: LUFS {result.lufs}, Peak {result.peak}")
```

**ROI**: Convergence algorithm eliminates guesswork

**Deferral**: Build after basic parameter control proven

---

## Phase 2: Stem Export Automation

**Goal**: Render individual tracks (stems) for analysis/mixing

**Approach**: Print/Resample (in-session recording)

**Not recommended**: Ableton multi-track export (OSC control not available)

### 2.1 Track Solo/Mute Control

**Required OSC endpoints** (verify availability):
- `/live/track/set/solo` (solo track for stem render)
- `/live/track/set/mute` (mute other tracks)
- `/live/track/get/solo` (query current state)
- `/live/track/get/mute` (query current state)

### 2.2 Print/Resample Logic

**Flow**:
1. Query all track IDs (`/live/song/get/tracks`)
2. For each track:
   a. Save current solo/mute state
   b. Solo track, mute all others
   c. Create new audio track
   d. Arm for recording
   e. Start playback + recording
   f. Wait for loop duration
   g. Stop recording
   h. Export recorded audio track (manual click or via freeze/export)
   i. Restore solo/mute state
3. Collect all stem files

**Complexity**: High (timing, routing, state restoration)

**Deferral**: Only after Master workflow proven and LUFS targets hit

---

## Implementation Status

### ✅ Phase 1.1-1.3 COMPLETE (This Session)

**Implemented**:
1. ✅ Batch experiment runner (`flaas experiment-run`)
2. ✅ Runtime device resolution (by name, case-insensitive)
3. ✅ Runtime parameter resolution (by name, fuzzy match)
4. ✅ Master fader OSC control (with manual fallback)
5. ✅ Glue Compressor parameter setting (threshold, makeup, ratio)
6. ✅ Limiter parameter setting (ceiling, gain, release)
7. ✅ File stabilization check (wait for appearance + stable size)
8. ✅ JSONL logging (`output/experiments.jsonl`)
9. ✅ SHA256 audit trail
10. ✅ Early exit on success

**Command**: `flaas experiment-run data/experiments/master_sweep.json`

**Config**: 3 experiments included (iter7-9)

**Ready to test**: Close 3.09 LU gap via parameter sweep

### 🔄 Phase 1.4 (Next)
1. Auto-adjustment algorithm
2. Convergence testing
3. Meta-command: `flaas auto-tune-master`

### 🔮 Phase 2 (Future)
1. Track solo/mute control
2. Print/resample stem exporter
3. Multi-track verification

---

## Success Criteria

### Phase 1 Success
- ✅ Glue Compressor control via CLI
- ✅ Master fader control via CLI
- ✅ Batch experiment runner functional
- ✅ 10+ experiments logged to `experiments.jsonl`
- ✅ LUFS/peak targets hit consistently

### Phase 2 Success
- ✅ Solo/mute control via CLI
- ✅ Print/resample stem export functional
- ✅ Stem verification working
- ✅ Full mix + stems validated

---

**Status**: Roadmap revised. Export trigger NOT feasible. Semi-automated approach validated.

**Next**: Build Glue Compressor OSC control (Phase 1.1)

**See**: `docs/reference/EXPORT_AUTOMATION_FEASIBILITY.md` for probe details
