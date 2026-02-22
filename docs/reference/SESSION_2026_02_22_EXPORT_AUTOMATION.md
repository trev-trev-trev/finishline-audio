# Session: Export Automation Implementation

**Date**: 2026-02-22 (Evening)  
**Focus**: Semi-automated batch experiment runner  
**Status**: ✅ Implementation complete, ready to test

---

## Context from Chat Log

**Source**: `finishline_export_chat_log_2026-02-22.md`

**Key findings**:
- 16 export experiments documented
- Export loop functional (manual iteration working)
- Critical discoveries: Master fader post-chain, limiter insufficient alone
- Best result: LUFS -13.59, Peak -6.00 (gap 3.09 LU to target)

**User directive**: Build `flaas experiment-run` for semi-automated parameter sweeps

---

## What Was Built

### 1. Core Module: `src/flaas/experiment_run.py`

**Capabilities**:
- Runtime device resolution by name (case-insensitive)
- Runtime parameter resolution by name (fuzzy match)
- dB → normalized [0,1] conversion with min/max clamping
- Master fader OSC control (0.85 linear = 0.0 dB)
- Glue Compressor parameter setting (threshold, makeup, ratio)
- Limiter parameter setting (ceiling, gain, release)
- File stabilization check (wait for appearance + 3 stable size checks)
- SHA256 hash computation for audit trail
- JSONL logging to `output/experiments.jsonl`
- Early exit on success (pass_lufs && pass_peak)

**Exit codes**:
- `0`: Success or all experiments complete
- `20`: Read failure (config missing, device not found, OSC timeout)
- `30`: Write failure (OSC parameter set failed)

### 2. CLI Integration: `src/flaas/cli.py`

**Command**: `flaas experiment-run <config.json>`

**Arguments**:
- `config`: Path to experiment config JSON
- `--host`: OSC host (default: 127.0.0.1)
- `--port`: OSC port (default: 11000)

**Help**: `flaas experiment-run --help`

### 3. Example Config: `data/experiments/master_sweep.json`

**Contents**: 3 experiments (iter7-9)

**Parameter sweep**:
- Experiment 1: GR ~12 dB, Makeup 15 dB, Limiter 28 dB
- Experiment 2: GR ~14 dB, Makeup 18 dB, Limiter 30 dB
- Experiment 3: GR ~16 dB, Makeup 20 dB, Limiter 32 dB

**Goal**: Close 3.09 LU gap (-13.59 → -10.50 LUFS)

### 4. Documentation

**Created**:
- `docs/reference/EXPORT_AUTOMATION_FEASIBILITY.md` - OSC probe results
- `docs/reference/AUTOMATION_ROADMAP.md` - Implementation phases
- `docs/reference/EXPERIMENT_RUNNER_USAGE.md` - Complete usage guide
- `docs/reference/EXPORT_FINDINGS.md` - 16 experiments + critical findings
- `docs/reference/SESSION_2026_02_22_EXPORT_AUTOMATION.md` - This file

**Updated**:
- `STATE.md` - Semi-automated runner ready, next action
- `QUICKSTART.md` - Add experiment-run command, update workflow
- `PRIORITY.md` - Export loop unblocked, Phase 1 complete
- `DISCOVERY.md` - Remove blocker language
- `NEXT_CHAPTER.md` - Remove blocker language
- `docs/status/STATUS.md` - Update current state, next action
- `README.md` - Export loop functional
- `NEW_CHAT_CONTEXT.md` - Mark obsolete, redirect to START_HERE.md
- `docs/reference/ENGINEERING_NOTEBOOK.md` - Add Section 13 (export triage)

---

## Technical Highlights

### Runtime Resolution (Not Hardcoded)

**Device resolution**:
```python
# Query devices by name, not ID
devices = request_once(target, "/live/track/get/devices/name", [track_id])
names = list(devices)[1:]  # Drop track_id
device_id = names.index("Glue Compressor")  # Case-insensitive
```

**Parameter resolution**:
```python
# Query all param info
names = request_once(target, "/live/device/get/parameters/name", [t, d])
mins = request_once(target, "/live/device/get/parameters/min", [t, d])
maxs = request_once(target, "/live/device/get/parameters/max", [t, d])

# Build mapping: param_name -> {id, min, max}
params = {str(names[i]): {"id": i, "min": mins[i], "max": maxs[i]} for i in range(len(names))}
```

**Fuzzy parameter matching**:
```python
# Config has "threshold_db", device has "Threshold"
key_lower = "threshold_db".replace("_db", "").replace("_", " ").lower()  # "threshold"
for pname in device_params:
    if pname.lower().replace(" ", "") == key_lower.replace(" ", ""):  # Match
        found = pname
```

### File Stabilization

**Problem**: WAV file may appear before write completes (premature verification)

**Solution**: Poll for stable file size
```python
stable_count = 0
while True:
    size = path.stat().st_size
    if size == last_size and size > 0:
        stable_count += 1
        if stable_count >= 3:  # 3 × 0.5s = 1.5s stable
            return True  # Ready
    else:
        stable_count = 0
    last_size = size
    time.sleep(0.5)
```

### JSONL Logging

**One line per experiment**:
```json
{"ts": "2026-02-22T19:10:00Z", "id": "iter7", "export_file": "output/master_iter7.wav", "sha256": "abc123", "params": {...}, "results": {"lufs_i": -11.5, "peak_dbfs": -6.2, "pass_lufs": false, "pass_peak": false}}
```

**Query with `jq`**:
```bash
# Find successful experiments
jq 'select(.results.pass_lufs and .results.pass_peak)' output/experiments.jsonl

# Find best LUFS
jq -s 'sort_by(.results.lufs_i) | reverse | .[0]' output/experiments.jsonl
```

---

## ROI Analysis

**Manual workflow** (10 experiments):
- Configure: 2 min
- Export: 30s
- Verify: 30s
- **Total per experiment**: 3 min
- **10 experiments**: 30 min

**Semi-automated workflow** (10 experiments):
- Auto-configure: 5s
- Export (manual click): 30s
- Auto-verify: 5s
- **Total per experiment**: 40s
- **10 experiments**: 7 min (no early exit)
- **With early exit**: < 7 min (stops when targets hit)

**Speedup**: ~4-5x (even with manual export click)

**If export were automated**: ~15x speedup

---

## Test Plan

### First Test (3 Experiments)

```bash
flaas experiment-run data/experiments/master_sweep.json
```

**Expected flow**:
1. Resolves devices (Glue Compressor, Limiter) on track -1000
2. Resolves params for both devices
3. Sets master fader to 0.0 dB
4. For each of 3 experiments:
   - Sets Glue params (threshold, makeup)
   - Sets Limiter params (ceiling, gain)
   - Pauses for manual export
   - Waits for file to stabilize
   - Verifies LUFS/peak
   - Logs to `output/experiments.jsonl`
   - Early exits if targets hit

**Expected outcome**:
- 1-3 experiments run (early exit possible)
- LUFS gap closed (hit -10.50 ± 0.5)
- Peak safe (≤ -6.00)
- Results logged

### Validate Results

```bash
# View all experiments
cat output/experiments.jsonl | jq .

# Check if any hit targets
jq 'select(.results.pass_lufs and .results.pass_peak)' output/experiments.jsonl
```

---

## Known Limitations

**Not automated**:
- Export trigger (manual File → Export click per experiment)
- Master fader (falls back to manual prompt if OSC fails)

**Automated**:
- Device resolution (by name)
- Parameter resolution (by name)
- Parameter setting (dB conversion)
- File waiting (stabilization)
- Verification (LUFS, peak)
- Logging (JSONL with SHA256)

**Future work**:
- Phase 1.4: Auto-adjustment algorithm (converge to targets)
- Phase 2: Stem export via print/resample

---

## Files Created/Modified

**New files**:
- `src/flaas/experiment_run.py` (278 lines)
- `data/experiments/master_sweep.json` (3 experiments)
- `docs/reference/EXPORT_AUTOMATION_FEASIBILITY.md` (OSC probe)
- `docs/reference/AUTOMATION_ROADMAP.md` (implementation phases)
- `docs/reference/EXPERIMENT_RUNNER_USAGE.md` (usage guide)
- `docs/reference/EXPORT_FINDINGS.md` (16 experiments)
- `docs/reference/SESSION_2026_02_22_EXPORT_AUTOMATION.md` (this file)

**Modified files**:
- `src/flaas/cli.py` (added experiment-run subcommand)
- `STATE.md` (semi-automated runner ready)
- `QUICKSTART.md` (experiment-run workflow)
- `PRIORITY.md` (export loop unblocked)
- `DISCOVERY.md`, `NEXT_CHAPTER.md` (remove blocker)
- `docs/status/STATUS.md` (current state updated)
- `README.md` (status updated)
- `NEW_CHAT_CONTEXT.md` (marked obsolete)
- `docs/reference/ENGINEERING_NOTEBOOK.md` (Section 13 added)

**Total commits this session**: 15

---

## Key Learnings

1. **Export trigger not available** - Verified via OSC probe (`/live/song/export/structure` returns `(1,)`)
2. **Semi-automated still high ROI** - 4-5x speedup even with manual export
3. **Runtime resolution critical** - Device/param IDs vary by set, hardcoding breaks
4. **File stabilization required** - WAV may appear before write completes
5. **Early exit optimization** - Stop when targets hit (saves time)
6. **JSONL receipts valuable** - Machine-readable audit trail for analysis

---

## Next Steps

### Immediate

1. **Test batch runner**:
   ```bash
   flaas experiment-run data/experiments/master_sweep.json
   ```

2. **Validate results**:
   ```bash
   cat output/experiments.jsonl | jq .
   ```

3. **Iterate if needed**:
   - Edit `data/experiments/master_sweep.json`
   - Add more experiments (iter10-15)
   - Run again

### After Targets Hit

1. **Document final settings** in `EXPORT_FINDINGS.md`
2. **Build auto-tune algorithm** (Phase 1.4)
3. **Begin endpoint expansion** (300-500 command goal)

---

**Status**: ✅ Implementation complete. Ready for first semi-automated test run.

**Command**: `flaas experiment-run data/experiments/master_sweep.json`
