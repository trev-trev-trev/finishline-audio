# Experiment Runner Usage

**Command**: `flaas experiment-run`  
**Purpose**: Semi-automated batch parameter sweep for master processing  
**Status**: ✅ Implemented

---

## What It Does

**Semi-automated workflow** (10x faster than manual):
1. Resolves device IDs by name (runtime, not hardcoded)
2. Resolves parameter IDs by name (runtime, not hardcoded)
3. Sets parameters via OSC (Glue Compressor, Limiter)
4. Sets master fader to 0.0 dB (attempts OSC, falls back to manual)
5. **Pauses for manual export** (prints filename, waits for file)
6. Waits for file to appear and stabilize
7. Verifies audio (LUFS, peak vs targets)
8. Logs results to `output/experiments.jsonl` (JSONL receipts)
9. **Early exit** on success (pass_lufs && pass_peak)

---

## Usage

```bash
flaas experiment-run data/experiments/master_sweep.json
```

**Example config**: `data/experiments/master_sweep.json` (3 experiments included)

### macOS Auto-Export (Fully Automated)

**Requires** (one-time setup):
1. **System Settings → Privacy & Security → Accessibility**
   - Enable **Terminal** (or iTerm2 if using that)
2. **System Settings → Privacy & Security → Automation**
   - Enable **Terminal → System Events**
3. **Ableton Live**:
   - Export defaults configured: Rendered Track = Master, Normalize = OFF
   - Loop/selection set to desired range (4-8 bars)

**Config**: Set `"auto_export": {"enabled": true, "timeout_s": 600}` (default on macOS)

**Behavior**: Exports triggered automatically via AppleScript UI automation (no manual clicks)

---

## Config Format

**Minimal JSON structure**:

```json
{
  "render_track": "Master",
  "loop": "selection",
  "normalize": false,
  "target_lufs": -10.5,
  "peak_limit_dbfs": -6.0,
  "master_track_id": -1000,
  "device_names": {
    "glue": "Glue Compressor",
    "limiter": "Limiter"
  },
  "runs": [
    {
      "id": "iter7",
      "export_file": "output/master_iter7.wav",
      "glue": { "threshold_db": -30.0, "makeup_db": 15.0 },
      "limiter": { "ceiling_db": -6.5, "gain_db": 28.0 }
    }
  ]
}
```

### Config Fields

**Top-level**:
- `render_track`: "Master" (descriptive, not used by runner)
- `loop`: "selection" (descriptive, manual export setting)
- `normalize`: false (descriptive, manual export setting)
- `target_lufs`: -10.5 (LUFS target for verification)
- `peak_limit_dbfs`: -6.0 (Peak limit for verification)
- `master_track_id`: -1000 (Master track ID)
- `device_names`: Device names to resolve (case-insensitive)
  - `glue`: "Glue Compressor" (or device name on your master track)
  - `limiter`: "Limiter" (or device name on your master track)

**Per-run**:
- `id`: Experiment ID (string, used in logs)
- `export_file`: Output WAV path (relative to repo root)
- `glue`: Glue Compressor settings (dB values)
  - `threshold_db`: Threshold in dB (e.g., -30.0)
  - `makeup_db`: Makeup gain in dB (e.g., 15.0)
  - `ratio`: Ratio (e.g., 4.0) - optional
- `limiter`: Limiter settings (dB values)
  - `ceiling_db`: Ceiling in dB (e.g., -6.5)
  - `gain_db`: Gain in dB (e.g., 28.0)
  - `release`: Release time (e.g., 0.1) - optional

**Parameter name resolution**: Case-insensitive, supports variations
- Config: `threshold_db` → Device param: `Threshold` or `threshold`
- Config: `makeup_db` → Device param: `Makeup` or `makeup`
- Config: `ceiling_db` → Device param: `Ceiling` or `ceiling`
- Config: `gain_db` → Device param: `Gain` or `gain`

**Auto-export config** (optional):
- `auto_export`: Auto-export configuration
  - `enabled`: true (auto via UI automation) or false (manual)
  - `timeout_s`: Timeout for export + file stabilization (default 600)
- **Default**: Enabled on macOS, disabled elsewhere

---

## Workflow Per Experiment

### Phase 1: Setup (Automated)

1. **Resolve device IDs** by name:
   - Query `/live/track/get/devices/name` for master track
   - Find "Glue Compressor" and "Limiter" (case-insensitive)

2. **Resolve parameter IDs** for each device:
   - Query `/live/device/get/parameters/name`
   - Query `/live/device/get/parameters/min`
   - Query `/live/device/get/parameters/max`
   - Build param name → {id, min, max} mapping

3. **Set master fader** to 0.0 dB (0.85 linear):
   - Try `/live/track/set/volume` with `[track_id, 0.85]`
   - If fails: Prompt for manual fader adjustment

4. **Set Glue Compressor params**:
   - Convert dB → normalized [0,1]: `norm = (value - min) / (max - min)`
   - Send `/live/device/set/parameter/value` per param

5. **Set Limiter params**:
   - Convert dB → normalized [0,1]
   - Send `/live/device/set/parameter/value` per param

### Phase 2: Export (Automatic or Manual)

6. **Export** (automatic on macOS with permissions):
   - **If auto-export enabled**:
     ```
     ──────────────────────────────────────────────────────────────────
     📤 AUTO-EXPORTING: master_iter7.wav
     ──────────────────────────────────────────────────────────────────
     ```
     - Triggers via AppleScript (Cmd+Shift+R → Save dialog → filename)
     - Waits for file to appear and stabilize
     - No manual interaction required
   
   - **If auto-export disabled** (manual fallback):
     ```
     ──────────────────────────────────────────────────────────────────
     📤 EXPORT NOW:
        File → Export Audio/Video
        Rendered Track = Master
        Normalize = OFF
        Filename: output/master_iter7.wav
     ──────────────────────────────────────────────────────────────────
     Press Enter after export completes...
     ```

7. **Wait for file** to appear and stabilize:
   - Poll every 0.5s
   - Wait for 2 consecutive stable size/mtime checks
   - Timeout after 600s (configurable)

### Phase 3: Verify + Log (Automated)

8. **Verify audio**:
   - Run `analyze_wav()` (peak, LUFS)
   - Run `check_wav()` (compare vs targets)
   - Print results

9. **Compute SHA256** hash of exported WAV

10. **Log to JSONL**:
    ```json
    {
      "ts": "2026-02-22T19:10:00Z",
      "id": "iter7",
      "export_file": "output/master_iter7.wav",
      "sha256": "abc123...",
      "params": {
        "master_fader_db": 0.0,
        "glue": { "threshold_db": -30.0, "makeup_db": 15.0 },
        "limiter": { "ceiling_db": -6.5, "gain_db": 28.0 }
      },
      "results": {
        "lufs_i": -12.4,
        "peak_dbfs": -6.3,
        "pass_lufs": false,
        "pass_peak": true
      }
    }
    ```
    Appends to `output/experiments.jsonl`

11. **Check success**:
    - If `pass_lufs == true` AND `pass_peak == true`:
      - Print success message
      - **Early exit** (don't run remaining experiments)
    - Else: Continue to next experiment

---

## Stop Conditions

Runner halts immediately when:
- ✅ **Success**: `pass_lufs == true` AND `pass_peak == true`
- ✗ **Export failure**: Auto-export fails or file timeout (logs error, continues to next)
- ✗ **OSC write failure**: Parameter set fails (prints failing endpoint + args, exits 30)

**Export failures logged**: Experiments that fail export are logged with `"status": "export_failed"` and error details

---

## Example Session

```bash
$ flaas experiment-run data/experiments/master_sweep.json

Resolving devices on track -1000...
  Glue Compressor: device 2
  Limiter: device 3
Resolving Glue Compressor parameters...
  Found 12 params
Resolving Limiter parameters...
  Found 9 params
Setting master fader to 0.0 dB...
  ✓ Master fader set to 0.0 dB

======================================================================
EXPERIMENT 1/3: iter7
======================================================================

Setting Glue Compressor...
  Setting Threshold = -30.0
    ✓ Threshold set
  Setting Makeup = 15.0
    ✓ Makeup set

Setting Limiter...
  Setting Ceiling = -6.5
    ✓ Ceiling set
  Setting Gain = 28.0
    ✓ Gain set

──────────────────────────────────────────────────────────────────
📤 EXPORT NOW:
   File → Export Audio/Video
   Rendered Track = Master
   Normalize = OFF
   Filename: output/master_iter7.wav
──────────────────────────────────────────────────────────────────
Press Enter after export completes...

Waiting for master_iter7.wav to stabilize...
  ✓ File ready

Verifying master_iter7.wav...
  LUFS: -11.50 (target -10.50) pass=False
  PEAK: -6.20 (limit -6.00) pass=False
  ✓ Logged to output/experiments.jsonl

======================================================================
EXPERIMENT 2/3: iter8
======================================================================
...
```

---

## Output: experiments.jsonl

**Location**: `output/experiments.jsonl`

**Format**: One JSON object per line (JSONL)

**Schema**:
```json
{
  "ts": "ISO-8601 timestamp",
  "id": "experiment ID",
  "export_file": "path to WAV",
  "sha256": "file hash",
  "params": {
    "master_fader_db": 0.0,
    "glue": {"threshold_db": -30.0, "makeup_db": 15.0},
    "limiter": {"ceiling_db": -6.5, "gain_db": 28.0}
  },
  "results": {
    "lufs_i": -11.50,
    "peak_dbfs": -6.20,
    "pass_lufs": false,
    "pass_peak": false
  }
}
```

**Use cases**:
- Audit trail of all experiments
- Machine-readable experiment database
- Filter by success: `jq 'select(.results.pass_lufs and .results.pass_peak)' output/experiments.jsonl`
- Find best LUFS: `jq -s 'sort_by(.results.lufs_i) | reverse | .[0]' output/experiments.jsonl`

---

## ROI Analysis

**Manual workflow** (10 experiments):
- Per experiment: Configure (2 min) + Export (30s) + Verify (30s) = 3 min
- Total: 10 × 3 min = **30 min**

**Fully automated workflow** (10 experiments, macOS):
- Per experiment: Auto-configure (5s) + Auto-export (30s) + Auto-verify (5s) = 40s
- Total: 10 × 40s = **7 min** (assuming no early exit)
- With early exit on success: **< 7 min**

**Speedup**: ~4-5x (compared to manual)

**With manual export** (non-macOS or permissions disabled):
- Per experiment: Auto-configure (5s) + Manual export (30s) + Auto-verify (5s) = 40s
- Still ~4-5x faster (only export click is manual)

---

## Capabilities

**Fully automated (macOS with permissions)**:
- ✅ Device resolution (by name, runtime)
- ✅ Parameter resolution (by name, runtime)
- ✅ Parameter setting (dB → normalized conversion)
- ✅ Export trigger (via AppleScript UI automation)
- ✅ File waiting (stabilization check)
- ✅ Verification (LUFS, peak, pass/fail)
- ✅ Logging (JSONL with SHA256)

**Manual fallback**:
- ⚠️ Master fader (no OSC endpoint, manual prompt before run)
- ⚠️ Export (if auto-export disabled or permissions missing)

---

## Next Steps

### Test Run

```bash
# Test with example config (3 experiments)
flaas experiment-run data/experiments/master_sweep.json
```

**Expected**:
- 3 experiments run
- Each pauses for manual export
- Results logged to `output/experiments.jsonl`
- Early exit if targets hit

### Create Custom Sweep

1. Copy `data/experiments/master_sweep.json` to `data/experiments/my_sweep.json`
2. Edit `runs` array with desired parameter combinations
3. Run: `flaas experiment-run data/experiments/my_sweep.json`

### Analyze Results

```bash
# View all experiments
cat output/experiments.jsonl | jq .

# Filter successful experiments
jq 'select(.results.pass_lufs and .results.pass_peak)' output/experiments.jsonl

# Find best LUFS (closest to -10.5)
jq -s 'sort_by((.results.lufs_i + 10.5) | fabs) | .[0]' output/experiments.jsonl
```

---

## Troubleshooting

### Device not found

**Error**: `Device 'Glue Compressor' not found on track -1000`

**Fix**: Check device name in Ableton, update `device_names` in config

### Parameter not found

**Warning**: `Param 'threshold_db' not found, skipping`

**Fix**: 
1. Generate device map: `flaas device-map -1000 <device_id>`
2. Check param names in `data/registry/device_map_t-1000_d<N>.json`
3. Update config with exact param names

### Master fader OSC fails

**Warning**: `OSC failed - Manually set Master fader to 0.0 dB`

**Action**: In Ableton, set Master fader to 0.0 dB, press Enter

### File timeout

**Error**: `File did not appear or stabilize within 30s`

**Causes**:
- Wrong export folder (check Ableton export settings)
- Export didn't complete (check Ableton)
- Wrong filename in config

---

## Implementation Details

**Module**: `src/flaas/experiment_run.py`

**Key functions**:
- `resolve_device_id_by_name()` - Find device by name (case-insensitive)
- `resolve_device_params()` - Query all param info (min/max/quantized)
- `set_device_param_by_name()` - Convert dB → normalized, send OSC
- `set_master_fader()` - Set track volume (linear 0.0-1.0)
- `wait_for_file()` - Poll for file appearance + size stabilization
- `compute_sha256()` - Hash exported WAV for audit trail
- `experiment_run()` - Main batch runner

**Exit codes**:
- `0`: Success (targets hit or all experiments complete)
- `20`: Read failure (config missing, device not found, OSC timeout)
- `30`: Write failure (OSC parameter set failed)

---

## Future Enhancements

### Phase 1.4: Auto-Adjustment Algorithm

**Command**: `flaas auto-tune-master <input_wav> <output_wav>`

**Logic**:
```python
for iteration in range(10):
    result = verify_audio(output_wav)
    if result.pass_lufs and result.peak_pass:
        return  # Success
    
    if result.peak > -6.0:
        limiter_gain -= 1.0  # Reduce gain
    elif result.lufs < -10.5:
        glue_threshold -= 1.0  # More compression
        glue_makeup += 1.0
        limiter_gain += 1.0
    
    # Pause for export
    # Continue
```

**ROI**: Eliminates guesswork, converges to targets

### Phase 2: Stem Export

**Command**: `flaas stem-export-all`

**Approach**: Print/resample (in-session recording)
- Solo each track
- Record to new audio track
- Export recorded track
- Restore solo/mute state

**Complexity**: High (timing, routing, state restoration)

**Deferral**: After Master workflow proven

---

**Status**: ✅ Implemented and ready to test

**Next**: Run first batch experiment to close 3.09 LU gap
