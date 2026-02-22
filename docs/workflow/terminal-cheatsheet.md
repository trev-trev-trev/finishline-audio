# Terminal Cheatsheet

**Quick command reference for FLAAS development and operation.**

## Sanity Checks (Environment Validation)

### Python Environment
```bash
python3 --version  # Should be >=3.11
python3 -m compileall src/flaas/  # Syntax check all modules
```

### Package Installation
```bash
source .venv/bin/activate
pip list | grep flaas  # Should show flaas 0.0.2
python3 -m flaas.cli --help  # Should show all commands
flaas --version  # Should print 0.0.2 (if in PATH)
```

### OSC Connectivity
```bash
flaas ping  # Fire-and-forget (prints "sent")
flaas ping --wait  # Request/response (prints "ok: ('ok',)")
```
**Expected**: `ok: ('ok',)` means AbletonOSC is alive.  
**Failure**: `TimeoutError` means Ableton not running, AbletonOSC not loaded, or ports blocked.

### Live Set Structure
```bash
flaas scan
cat data/caches/model_cache.json
```
**Expected**: JSON with tracks, devices, fingerprint.  
**Failure**: Empty tracks or `ok: false` means scan failed.

## Golden Path Command Chain

### 1. Connectivity Test
```bash
flaas ping --wait
```
**Output**: `ok: ('ok',)`  
**Purpose**: Verify AbletonOSC bidirectional communication

### 2. Scan Live Set
```bash
flaas scan
```
**Output**: `data/caches/model_cache.json`  
**Purpose**: Cache track/device structure + fingerprint

### 3. Analyze Audio
```bash
flaas analyze input/test.wav
```
**Output**: `data/reports/analysis.json`  
**Purpose**: Peak dBFS + LUFS-I measurements

### 4. Check Compliance
```bash
flaas check input/test.wav
```
**Output**: `data/reports/check.json`  
**Purpose**: Pass/fail against targets

### 5. Plan Actions
```bash
flaas plan-gain input/test.wav
```
**Output**: `data/actions/actions.json` + prints current linear + delta  
**Purpose**: Compute bounded Utility Gain delta

### 6. Verify Actions (Dry-Run)
```bash
flaas apply --dry
```
**Output**: `DRY_RUN: MASTER :: Utility.Gain += 0.xxx`  
**Purpose**: Preview planned actions

### 7. Apply Actions (Real)
```bash
flaas apply
```
**Output**: `APPLIED: Utility.Gain 0.000 -> 0.250 (norm 0.500->0.625)`  
**Purpose**: Execute parameter changes via OSC

### 8. Verify Result
```bash
flaas verify
```
**Output**: `0.625` (normalized value)  
**Purpose**: Read back current Utility Gain

### 9. Loop (Automated Chain)
```bash
flaas loop input/test.wav --dry  # Preview
flaas loop input/test.wav        # Execute
```
**Output**: `MEASURE → CUR_LINEAR → DELTA → APPLIED → DONE`  
**Purpose**: analyze → plan → apply in one command

### 10. Audio Verification
```bash
flaas verify-audio output/master.wav
```
**Output**: `PASS` or `FAIL` + exit code  
**Purpose**: Final compliance check

## Command Reference

### Core Commands

| Command | Purpose | Reads | Writes | Exit Code |
|---------|---------|-------|--------|-----------|
| `flaas ping [--wait]` | Test OSC connectivity | - | - | 0=ok |
| `flaas scan` | Query Live tracks/devices | OSC | `model_cache.json` | 0=ok |
| `flaas analyze <wav>` | Measure peak+LUFS | WAV | `analysis.json` | 0=ok |
| `flaas check <wav>` | Compliance check | WAV | `check.json` | 0=ok |
| `flaas plan-gain <wav>` | Compute gain delta | WAV+OSC | `actions.json` | 0=ok |
| `flaas apply [--dry]` | Execute actions | OSC+actions | OSC params | 0=ok, 1=mismatch |
| `flaas verify` | Read Utility gain | OSC | - | 0=ok |
| `flaas reset` | Center Utility gain | OSC | OSC params | 0=ok |
| `flaas loop <wav> [--dry]` | Full iteration | WAV+OSC | actions+OSC | 0=ok, early exit if maxed |
| `flaas verify-audio <wav>` | Final check | WAV | - | 0=PASS, 1=FAIL |
| `flaas export-guide` | Print export settings | - | - | 0=ok |
| `flaas inspect-selected-device` | Show device param table | OSC | - | 0=ok |
| `flaas inspect-selected-track` | Show device list for track | OSC | - | 0=ok |
| `flaas device-param-info <t> <d> --param-id N` | Show single param metadata | OSC | - | 0=ok |
| `flaas eq8-map <t> <d>` | Generate EQ Eight param map JSON | OSC | `registry/*.json` | 0=ok |
| `flaas eq8-set <t> <d> --band N --side A/B --param gain --value V` | Set EQ Eight by semantic name | Map+OSC | OSC params | 0=ok |
| `flaas eq8-reset-gains <t> <d>` | Reset all EQ band gains to 0 dB | Map+OSC | OSC params | 0=ok |
| `flaas eq8-set-param --param-id N --value V` | Set param on selected device | OSC | OSC params | 0=ok |
| `flaas device-set-param <t> <d> --param-id N --value V` | Set any device param (generic) | OSC | OSC params | 0=ok |

### Utility Commands (Direct Control)

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `flaas util-gain-norm <t> <d> <val>` | Set normalized 0..1 | Direct testing |
| `flaas util-gain-linear <t> <d> <val>` | Set linear (e.g. -1..+1) | Known range |

**Example**: `flaas util-gain-norm 0 0 0.5` sets track 0 device 0 to center

## Troubleshooting Decision Tree

### Problem: Command not found
```bash
which flaas  # Check if in PATH
python3 -m flaas.cli --help  # Direct module invocation
pip show flaas  # Check installation
```
**Fix**: `pip install -e .` in repo root

### Problem: OSC timeout
```bash
flaas ping --wait --timeout 5.0  # Increase timeout
```
**If still fails**:
- Check Ableton Live is open
- Check Preferences → Link/Tempo/MIDI → Control Surface shows AbletonOSC
- Check AbletonOSC script loaded: Look for "AbletonOSC" in Live's log

### Problem: Fingerprint mismatch
```bash
flaas scan  # Regenerate fingerprint
flaas plan-gain input/test.wav  # Regenerate actions with new fingerprint
flaas apply  # Should now succeed
```

### Problem: Utility gain maxed out
```bash
flaas verify  # Check current value
flaas reset  # Return to center
flaas loop input/test.wav  # Try again
```

### Problem: Analysis fails
```bash
ls -la input/test.wav  # Verify file exists
file input/test.wav  # Check file type
flaas analyze input/test.wav  # Try again with verbose
```
**Fix**: Regenerate test WAV with provided Python snippet

### Problem: Import errors
```bash
python3 -m compileall src/flaas/  # Check syntax
pip install -e .  # Reinstall package
source .venv/bin/activate  # Activate venv
```

## Common Workflows

### Workflow A: First-time Setup
```bash
git clone <repo>
cd finishline-audio
make dev
source .venv/bin/activate
flaas ping --wait  # Verify connectivity
```

### Workflow B: Iterative Gain Refinement
```bash
# In Ableton: Export master to output/master.wav (see flaas export-guide)
flaas verify-audio output/master.wav  # Check compliance
# If FAIL:
flaas loop output/master.wav  # Apply correction
# Repeat export + verify until PASS
```

### Workflow C: Manual Utility Control
```bash
flaas verify  # Check current state
flaas util-gain-linear 0 0 0.3  # Set specific value
flaas verify  # Confirm change
```

### Workflow D: Development / Testing
```bash
# Make code changes
python3 -m compileall src/flaas/  # Check syntax
flaas [command] --help  # Verify CLI wiring
flaas [command] [...args]  # Test functionality
git add -A && git commit -m "..." && git push  # Commit if success
```

## Output Interpretation

### Success Patterns
- `sent` = OSC message dispatched (fire-and-forget)
- `ok: (...)` = OSC reply received
- `APPLIED: ...` = Parameter changed
- `PASS` = Compliance achieved
- `data/[path].json` = File written successfully

### Warning Patterns
- `WARNING: delta clamped` = Requested adjustment exceeds safety limit
- `STOP: utility gain already near max` = Can't increase further
- `SKIP: unsupported action` = Action type not implemented

### Failure Patterns
- `TimeoutError` = OSC communication failed
- `RuntimeError: Live fingerprint mismatch` = Set changed since planning
- `FAIL` = Compliance check failed
- `ValueError: empty audio` = Invalid or empty WAV file

## Data Artifact Locations

### Generated (gitignored)
- `data/caches/model_cache.json` - Live set scan result
- `data/reports/analysis.json` - Audio measurements
- `data/reports/check.json` - Compliance check results
- `data/actions/actions.json` - Planned parameter changes
- `input/*.wav` - Test audio (gitignored)
- `output/*.wav` - Exported renders (gitignored)

### Quick inspection
```bash
cat data/caches/model_cache.json | jq '.fingerprint'
cat data/actions/actions.json | jq '.actions[0].delta_db'
cat data/reports/analysis.json | jq '.lufs_i'
```

## Constants Reference (Quick Lookup)

| Constant | Value | Source |
|----------|-------|--------|
| `UTILITY_GAIN_PARAM_ID` | 9 | Discovered via `/live/device/get/parameters/name` |
| Master track ID | 0 | Assumed (first track) |
| Utility device ID | 0 | Assumed (first device on master) |
| AbletonOSC listen port | 11000 | Standard |
| AbletonOSC reply port | 11001 | Standard |
| Target LUFS | -10.5 | `targets.py` |
| LUFS tolerance | ±0.5 LU | `check.py` |
| Stem peak ceiling | -6.0 dBFS | `targets.py` |
| Delta clamp | ±0.25 linear | `plan.py` |
| Max gain norm | 0.99 | `loop.py` stop condition |

## Development Commands

### Run Tests (if pytest installed)
```bash
pytest -v
pytest tests/test_[module].py
```

### Check Code Quality
```bash
python3 -m compileall src/
python3 -m pylint src/flaas/ --disable=all --enable=E,F
python3 -m mypy src/flaas/ --ignore-missing-imports
```

### Build Package
```bash
python3 -m build
pip install dist/flaas-0.0.2-py3-none-any.whl
```

### Clean Build Artifacts
```bash
rm -rf src/flaas.egg-info build/ dist/
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Next Command Prediction (Agent Guide)

After each task completion, predict the next validation command:

| Just completed | Next command |
|----------------|--------------|
| Added `foo.py` module | `python3 -c "import flaas.foo"` |
| Added CLI command | `flaas [cmd] --help` |
| Changed OSC endpoint | `flaas ping --wait` |
| Changed param mapping | `flaas verify` |
| Changed analysis | `flaas analyze input/test.wav` |
| Changed planning | `flaas plan-gain input/test.wav && cat data/actions/actions.json` |
| Changed apply | `flaas apply --dry` |
| Fixed bug | Re-run original failing command |
| Added test | `pytest tests/test_[name].py` |

This ensures immediate validation of each change.
