# FLAAS Engineering Notebook

**Comprehensive technical reference for Finish Line Audio Automation System**

**Updated**: 2026-02-22 19:05 UTC  
**Version**: 0.0.2  
**Commit**: 0a64c50  
**Repo**: https://github.com/trev-trev-trev/finishline-audio

**CRITICAL**: See `STATE.md` for current operational state. This notebook is technical reference only.

---

## Table of Contents

1. [Codebase Index](#codebase-index)
2. [API / Function Catalog](#api--function-catalog)
3. [OSC Contract Sheet](#osc-contract-sheet)
4. [Data Artifacts + Schemas](#data-artifacts--schemas)
5. [CLI Command Sheet](#cli-command-sheet)
6. [Call Graph + Boundaries](#call-graph--boundaries)
7. [Determinism + Reproducibility](#determinism--reproducibility)
8. [Testing Map](#testing-map)
9. [Reliability Patterns](#reliability-patterns)
10. [Troubleshooting Playbook](#troubleshooting-playbook)
11. [Contribution Rules](#contribution-rules)

---

## 1. Codebase Index

### Repository Structure
```
/
├── src/flaas/          # Core package
│   ├── __init__.py
│   ├── cli.py          # CLI entry point + arg parsing
│   ├── osc.py          # Fire-and-forget OSC
│   ├── osc_rpc.py      # Request/response OSC
│   ├── scan.py         # Live set scanning
│   ├── audio_io.py     # WAV file I/O
│   ├── analyze.py      # Audio analysis (peak+LUFS)
│   ├── targets.py      # Compliance targets
│   ├── check.py        # Compliance checking
│   ├── actions.py      # Action data structures
│   ├── plan.py         # Gain planning
│   ├── param_map.py    # Parameter range mapping
│   ├── util.py         # Utility device control
│   ├── apply.py        # Action execution
│   ├── verify.py       # Parameter readback
│   ├── loop.py         # Orchestration loop
│   ├── export_guide.py # Export instructions
│   ├── verify_audio.py # Audio verification
│   └── inspect_selected_device.py # Device param inspector
├── data/               # Generated artifacts (gitignored)
│   ├── caches/         # model_cache.json
│   ├── reports/        # analysis.json, check.json
│   ├── actions/        # actions.json
│   ├── timelines/      # (future)
│   └── profiles/       # (future)
├── input/              # Test audio (gitignored)
├── output/             # Exported renders (gitignored)
├── tests/              # Test suite
├── docs/               # Documentation
│   ├── project/        # Vision, planning
│   ├── architecture/   # Technical specs
│   ├── workflow/       # Dev workflows
│   ├── reference/      # This file, state snapshots
│   └── archive/        # Original docs
├── pyproject.toml      # Package config
├── Makefile            # Dev commands
└── README.md           # User-facing quickstart
```

### File Manifest with Responsibilities

#### `src/flaas/cli.py` (167 lines)
**Purpose**: CLI entry point and command routing  
**Key responsibilities**:
- Parse command-line arguments with argparse
- Route to appropriate module functions
- Handle exit codes for scripting  
**Key dependencies**: All flaas modules  
**Side effects**: None (pure routing)

#### `src/flaas/osc.py` (13 lines)
**Purpose**: Fire-and-forget OSC messaging  
**Key responsibilities**:
- Send OSC messages without waiting for reply  
**Key dependencies**: `pythonosc.udp_client`  
**Side effects**: Network I/O (UDP send to AbletonOSC)

#### `src/flaas/osc_rpc.py` (52 lines)
**Purpose**: Request/response OSC communication  
**Key responsibilities**:
- Send OSC message and wait for reply
- Manage temporary OSC server for receiving replies
- Handle timeouts and cleanup  
**Key dependencies**: `pythonosc` (dispatcher, server, client)  
**Side effects**: Network I/O (UDP send/receive), thread creation

#### `src/flaas/scan.py` (91 lines)
**Purpose**: Live set structure scanning  
**Key responsibilities**:
- Query tracks, devices, and metadata from Ableton
- Compute SHA256 fingerprint of set structure
- Write model_cache.json with error handling  
**Key dependencies**: `osc_rpc.request_once`  
**Side effects**: Network I/O (OSC queries), filesystem write

#### `src/flaas/audio_io.py` (29 lines)
**Purpose**: Audio file I/O primitives  
**Key responsibilities**:
- Read WAV metadata (sr, channels, samples)
- Load audio as mono float32 numpy array  
**Key dependencies**: `soundfile`, `numpy`  
**Side effects**: Filesystem read, memory allocation for audio buffers

#### `src/flaas/analyze.py` (52 lines)
**Purpose**: Audio analysis (peak + LUFS)  
**Key responsibilities**:
- Compute peak dBFS (20*log10(peak))
- Compute LUFS-I (BS.1770 integrated loudness)
- Write analysis.json report  
**Key dependencies**: `audio_io`, `numpy`, `pyloudnorm`  
**Side effects**: Filesystem read (audio), filesystem write (JSON), CPU-intensive DSP

#### `src/flaas/targets.py` (58 lines) **UPDATED 2026-02-22**
**Purpose**: Compliance target definitions + master track utilities  
**Key responsibilities**:
- Define master_lufs (-10.5), true_peak_ceiling (-1.0), stem_peak_ceiling (-6.0)
- Define MASTER_TRACK_ID = -1000
- Provide resolve_utility_device_id() for dynamic Utility device resolution  
**Key dependencies**: `osc_rpc`  
**Side effects**: OSC queries (resolve_utility_device_id), SystemExit(20) on Utility not found

**Critical addition**: Shared resolver eliminates code duplication across plan.py, apply.py, verify.py

#### `src/flaas/check.py` (38 lines)
**Purpose**: Compliance checking against targets  
**Key responsibilities**:
- Compare analysis results against targets
- Compute pass/fail flags (LUFS ±0.5 LU, peak <= ceiling)
- Write check.json report  
**Key dependencies**: `analyze`, `targets`  
**Side effects**: Filesystem write (JSON)

#### `src/flaas/actions.py` (38 lines)
**Purpose**: Action data structures and serialization  
**Key responsibilities**:
- Define GainAction and ActionsFile schemas
- Serialize actions to JSON with schema version + fingerprint
- Create parent directories as needed  
**Key dependencies**: None (pure data + JSON)  
**Side effects**: Filesystem write (JSON)

#### `src/flaas/param_map.py` (22 lines)
**Purpose**: Parameter range mapping (linear ↔ normalized)  
**Key responsibilities**:
- Query parameter min/max from AbletonOSC
- Map linear values to normalized 0..1
- Handle edge cases (equal min/max, clamping)  
**Key dependencies**: `osc_rpc.request_once`  
**Side effects**: Network I/O (OSC queries)

#### `src/flaas/plan.py` (71 lines)
**Purpose**: Gain planning (LUFS error → linear delta)  
**Key responsibilities**:
- Query current Utility Gain state
- Compute LUFS error (target - measured)
- Map error to bounded linear delta (err/12, clamp ±0.25)
- Write actions.json with Live fingerprint
- Print current state + planned delta  
**Key dependencies**: `analyze`, `targets`, `actions`, `scan`, `osc_rpc`, `param_map`  
**Side effects**: Network I/O (OSC queries), filesystem write (JSON), stdout print

#### `src/flaas/util.py` (21 lines)
**Purpose**: Direct Utility Gain parameter control  
**Key responsibilities**:
- Set Utility Gain normalized (0..1)
- Set Utility Gain linear (uses param_map)  
**Key dependencies**: `osc_rpc`, `param_map`  
**Side effects**: Network I/O (OSC set commands)

#### `src/flaas/apply.py` (73 lines)
**Purpose**: Action execution engine  
**Key responsibilities**:
- Load actions from JSON
- Validate Live fingerprint
- Apply relative delta (read current → add delta → set new)
- Print before/after state  
**Key dependencies**: `osc_rpc`, `param_map`, `scan`  
**Side effects**: Network I/O (OSC queries + sets), stdout print

#### `src/flaas/verify.py` (32 lines) **UPDATED 2026-02-22**
**Purpose**: Parameter readback  
**Key responsibilities**:
- Read current Utility Gain normalized value
- Default to master track (-1000) with dynamic Utility device resolution  
**Key dependencies**: `osc_rpc`, `targets` (MASTER_TRACK_ID, resolve_utility_device_id)  
**Side effects**: Network I/O (OSC query), SystemExit(20) if Utility not found

**Critical change**: track_id and device_id now optional (default None), auto-resolves to master

#### `src/flaas/loop.py` (27 lines)
**Purpose**: Orchestration loop (analyze → plan → apply)  
**Key responsibilities**:
- Pre-flight check (stop if Utility near max)
- Run full workflow in sequence
- Post-apply verification
- Support dry-run mode  
**Key dependencies**: `analyze`, `plan`, `apply`, `verify`  
**Side effects**: All effects of called modules + stdout print

#### `src/flaas/export_guide.py` (14 lines)
**Purpose**: Ableton export settings reference  
**Key responsibilities**:
- Print standardized export settings  
**Key dependencies**: None  
**Side effects**: Stdout print only

#### `src/flaas/verify_audio.py` (15 lines)
**Purpose**: Combined audio analysis + compliance check  
**Key responsibilities**:
- Run analyze + check in one command
- Print summary with PASS/FAIL
- Return exit code for scripting  
**Key dependencies**: `analyze`, `check`  
**Side effects**: All effects of analyze/check + stdout print

#### `src/flaas/inspect_selected_device.py` (58 lines)
**Purpose**: Device parameter introspection (discovery tool)  
**Key responsibilities**:
- Query selected device from Live view
- Fetch all parameter metadata (name, value, min, max, is_quantized)
- Print formatted table or raw tuples  
**Key dependencies**: `osc_rpc`  
**Side effects**: Network I/O (OSC queries), stdout print

---

## 2. API / Function Catalog

### `osc.send_ping`
**Signature**:
```python
def send_ping(target: OscTarget, address: str = "/live/test", value: Any = "ok") -> None
```

**What it does**:
- Sends fire-and-forget OSC message to AbletonOSC
- Default: `/live/test` with value `"ok"`
- No reply expected

**Inputs**:
- `target`: OscTarget (host, port)
- `address`: OSC endpoint path
- `value`: Payload (Any type)

**Outputs**: None

**Side effects**: UDP packet sent to target

**Failure modes**: None (fire-and-forget)

**Example**:
```python
from flaas.osc import OscTarget, send_ping
send_ping(OscTarget(host="127.0.0.1", port=11000))
```

**Where used**: `cli.py` (ping command without `--wait`)

**How to validate**: `flaas ping` (prints "sent")

---

### `osc_rpc.request_once`
**Signature**:
```python
def request_once(
    target: OscTarget,
    address: str,
    value: Any = 1,
    listen_port: int = 11001,
    timeout_sec: float = 2.0,
) -> tuple[Any, ...]
```

**What it does**:
- Sends OSC message and waits for one reply
- Starts temporary OSC server on `listen_port`
- Returns reply arguments as tuple
- Cleans up server after reply or timeout

**Inputs**:
- `target`: OscTarget for sending
- `address`: OSC endpoint path
- `value`: Request payload
- `listen_port`: Port to listen for reply (default 11001)
- `timeout_sec`: Max wait time (default 2.0)

**Outputs**: `tuple[Any, ...]` - reply arguments from AbletonOSC

**Side effects**:
- UDP send to target
- Temporary OSC server on listen_port
- Thread creation (daemon)
- Server cleanup on completion

**Failure modes**:
- `TimeoutError`: No reply within timeout_sec
- Port bind failure if listen_port already in use

**Invariants**:
- Server always cleaned up (shutdown + server_close)
- Thread is daemon (won't block process exit)

**Example**:
```python
from flaas.osc_rpc import OscTarget, request_once
resp = request_once(OscTarget(), "/live/test", "ok", timeout_sec=3.0)
# resp = ('ok',)
```

**Where used**:
- `cli.py` (ping --wait)
- `scan.py` (all Live queries)
- `param_map.py` (get_param_range)
- `plan.py` (_get_current_utility_linear)
- `apply.py` (fingerprint check, read current value)
- `verify.py` (verify_master_utility_gain)

**How to validate**: `flaas ping --wait` (should print `ok: ('ok',)`)

---

### `scan.scan_live`
**Signature**:
```python
def scan_live(target: OscTarget = OscTarget(), timeout_sec: float = 2.0) -> ScanResult
```

**What it does**:
- Queries Ableton Live set structure via AbletonOSC
- Fetches: num_tracks, track_names, per-track device counts, device names/class_names
- Computes SHA256 fingerprint of structure
- Returns structured ScanResult with all metadata

**Inputs**:
- `target`: OscTarget (default localhost:11000)
- `timeout_sec`: Per-request timeout (default 2.0)

**Outputs**: `ScanResult` dataclass containing:
- `ok`: bool (success flag)
- `note`: str (description)
- `created_at_utc`: str (ISO timestamp)
- `num_tracks`: int
- `tracks`: list[TrackInfo] (track_id, name, num_devices, devices[])
- `fingerprint`: str (SHA256 hex)

**Side effects**:
- Multiple OSC requests (N+1+3N where N=num_tracks)
- No filesystem I/O

**Failure modes**:
- `TimeoutError`: AbletonOSC not responding
- `IndexError`: Malformed reply (too few elements)
- Any exception caught by caller (write_model_cache)

**Invariants**:
- Fingerprint is deterministic for given Live set structure
- track_id is 0-indexed and matches Ableton track order

**Example**:
```python
from flaas.scan import scan_live
result = scan_live()
print(f"Tracks: {result.num_tracks}, Fingerprint: {result.fingerprint}")
```

**Where used**:
- `plan.write_plan_gain_actions` (get fingerprint)
- `apply.apply_actions_osc` (validate fingerprint)

**How to validate**:
```bash
flaas scan
cat data/caches/model_cache.json
```

---

### `scan.write_model_cache`
**Signature**:
```python
def write_model_cache(path: str | Path = "data/caches/model_cache.json") -> Path
```

**What it does**:
- Calls `scan_live()` with error handling
- Writes ScanResult to JSON file
- Creates parent directories if needed
- Returns Path to written file

**Inputs**:
- `path`: Output JSON path (default: data/caches/model_cache.json)

**Outputs**: `Path` object of written file

**Side effects**:
- OSC queries (via scan_live)
- Filesystem write (JSON)
- Directory creation

**Failure modes**:
- Catches all exceptions from `scan_live()`
- Writes failed scan result with error message
- Never raises (defensive)

**Example**:
```python
from flaas.scan import write_model_cache
path = write_model_cache()
print(f"Wrote {path}")
```

**Where used**: `cli.py` (scan command)

**How to validate**:
```bash
flaas scan
test -f data/caches/model_cache.json && echo "exists"
```

---

### `audio_io.read_audio_info`
**Signature**:
```python
def read_audio_info(path: str | Path) -> AudioData
```

**What it does**:
- Reads WAV file metadata without loading audio data
- Returns sample rate, channels, sample count

**Inputs**:
- `path`: Path to WAV file

**Outputs**: `AudioData` dataclass:
- `path`: str (resolved path)
- `sr`: int (sample rate)
- `channels`: int (channel count)
- `samples`: int (total frames)

**Side effects**: Filesystem read (metadata only)

**Failure modes**:
- `FileNotFoundError`: File doesn't exist
- `soundfile` exceptions: Invalid/corrupt WAV

**Example**:
```python
from flaas.audio_io import read_audio_info
info = read_audio_info("input/test.wav")
print(f"SR={info.sr} channels={info.channels} samples={info.samples}")
```

**Where used**: `analyze.analyze_wav`

**How to validate**:
```python
python3 -c "from flaas.audio_io import read_audio_info; print(read_audio_info('input/test.wav'))"
```

---

### `audio_io.read_mono_float`
**Signature**:
```python
def read_mono_float(path: str | Path) -> tuple[np.ndarray, int]
```

**What it does**:
- Loads audio file as float32 numpy array
- Converts to mono by averaging channels
- Returns (mono_audio, sample_rate)

**Inputs**:
- `path`: Path to audio file

**Outputs**:
- `tuple[np.ndarray, int]`: (mono float32 array, sample rate)

**Side effects**:
- Filesystem read (full audio data)
- Memory allocation (numpy array)

**Failure modes**:
- `FileNotFoundError`: File doesn't exist
- `MemoryError`: File too large
- `soundfile` exceptions: Invalid audio format

**Invariants**:
- Output is always 1D (mono)
- Output dtype is float32
- Sample rate matches file metadata

**Example**:
```python
from flaas.audio_io import read_mono_float
audio, sr = read_mono_float("input/test.wav")
print(f"Loaded {audio.shape[0]} samples at {sr} Hz")
```

**Where used**: `analyze.analyze_wav`

**How to validate**:
```python
python3 -c "from flaas.audio_io import read_mono_float; a,sr=read_mono_float('input/test.wav'); print(f'shape={a.shape} sr={sr}')"
```

---

### `analyze.analyze_wav`
**Signature**:
```python
def analyze_wav(path: str | Path) -> AnalysisResult
```

**What it does**:
- Reads audio file
- Computes peak dBFS: `20*log10(max(abs(audio)))`
- Computes LUFS-I using BS.1770 meter
- Returns structured result with timestamp

**Inputs**:
- `path`: Path to WAV file

**Outputs**: `AnalysisResult` dataclass:
- `file`: str
- `sr`: int
- `channels`: int
- `samples`: int
- `duration_sec`: float
- `peak_dbfs`: float
- `lufs_i`: float
- `created_at_utc`: str (ISO timestamp)

**Side effects**:
- Filesystem read
- CPU-intensive (LUFS calculation)
- Memory allocation

**Failure modes**:
- `ValueError("empty audio")`: Audio has zero samples
- `FileNotFoundError`: File doesn't exist
- Propagates audio_io exceptions

**Invariants**:
- peak_dbfs is -inf if audio is all zeros
- lufs_i uses BS.1770 standard (pyloudnorm.Meter)
- duration_sec = samples / sr

**Example**:
```python
from flaas.analyze import analyze_wav
result = analyze_wav("input/test.wav")
print(f"LUFS={result.lufs_i:.2f} peak={result.peak_dbfs:.2f}")
```

**Where used**:
- `check.check_wav`
- `plan.plan_utility_gain_delta_for_master`
- `loop.run_loop`
- `verify_audio.verify_audio`

**How to validate**:
```bash
flaas analyze input/test.wav
cat data/reports/analysis.json | jq '{lufs_i, peak_dbfs}'
```

---

### `check.check_wav`
**Signature**:
```python
def check_wav(path: str | Path, targets: Targets = DEFAULT_TARGETS) -> CheckResult
```

**What it does**:
- Analyzes WAV file
- Compares against compliance targets
- Returns pass/fail flags for LUFS and peak

**Inputs**:
- `path`: WAV file path
- `targets`: Targets object (optional, defaults to DEFAULT_TARGETS)

**Outputs**: `CheckResult` dataclass:
- `file`: str
- `pass_lufs`: bool (true if |measured - target| <= 0.5)
- `pass_peak`: bool (true if peak <= target)
- `lufs_i`: float (measured)
- `peak_dbfs`: float (measured)
- `target_lufs`: float
- `target_peak_dbfs`: float

**Side effects**: All effects of `analyze_wav`

**Failure modes**: Propagates analyze_wav exceptions

**Invariants**:
- LUFS tolerance is ±0.5 LU (hardcoded)
- Peak check uses stem_peak_ceiling_dbfs (not true_peak yet)

**Example**:
```python
from flaas.check import check_wav
result = check_wav("input/test.wav")
print(f"LUFS pass: {result.pass_lufs}, Peak pass: {result.pass_peak}")
```

**Where used**:
- `verify_audio.verify_audio`

**How to validate**:
```bash
flaas check input/test.wav
cat data/reports/check.json | jq '{pass_lufs, pass_peak}'
```

---

### `param_map.get_param_range`
**Signature**:
```python
def get_param_range(track_id: int, device_id: int, param_id: int, target: OscTarget = OscTarget(), timeout_sec: float = 3.0) -> ParamRange
```

**What it does**:
- Queries `/live/device/get/parameters/min` and `/parameters/max`
- Extracts min/max for specific param_id
- Returns ParamRange(min, max)

**Inputs**:
- `track_id`: Track index
- `device_id`: Device index on track
- `param_id`: Parameter index
- `target`: OscTarget
- `timeout_sec`: Timeout per request

**Outputs**: `ParamRange(min: float, max: float)`

**Side effects**: 2 OSC queries

**Failure modes**:
- `TimeoutError`: OSC timeout
- `IndexError`: param_id out of range (implicit, would fail on array access)

**Invariants**:
- Response format: `(track_id, device_id, val0, val1, val2, ...)`
- Index calculation: `idx = 2 + param_id`
- Min/max are in "linear" units (for Utility Gain, typically -1..+1)

**Example**:
```python
from flaas.param_map import get_param_range
from flaas.osc_rpc import OscTarget
pr = get_param_range(0, 0, 9)  # Track 0, device 0, param 9
print(f"Range: {pr.min} to {pr.max}")
```

**Where used**:
- `util.set_utility_gain_linear`
- `plan._get_current_utility_linear`
- `apply.apply_actions_osc`

**How to validate**:
```python
python3 -c "from flaas.param_map import get_param_range; print(get_param_range(0,0,9))"
```

---

### `param_map.linear_to_norm`
**Signature**:
```python
def linear_to_norm(x: float, pr: ParamRange) -> float
```

**What it does**:
- Maps linear value in [pr.min, pr.max] to normalized [0, 1]
- Clamps input to range
- Handles degenerate case (min == max)

**Inputs**:
- `x`: Linear value
- `pr`: ParamRange with min/max

**Outputs**: float in [0.0, 1.0]

**Side effects**: None (pure function)

**Failure modes**: None (defensive)

**Invariants**:
- Returns 0.0 if pr.max == pr.min
- Output always in [0, 1]
- Formula: `(clamp(x, min, max) - min) / (max - min)`

**Example**:
```python
from flaas.param_map import ParamRange, linear_to_norm
pr = ParamRange(min=-1.0, max=1.0)
norm = linear_to_norm(0.5, pr)  # 0.5 -> 0.75
```

**Where used**:
- `util.set_utility_gain_linear`
- `apply.apply_actions_osc`

**How to validate**:
```python
python3 -c "from flaas.param_map import *; pr=ParamRange(-1,1); print(linear_to_norm(0, pr))"  # Should print 0.5
```

---

### `plan.plan_utility_gain_delta_for_master`
**Signature**:
```python
def plan_utility_gain_delta_for_master(
    wav: str | Path,
    targets: Targets = DEFAULT_TARGETS,
    clamp_linear: float = 0.25,
    target_osc: OscTarget = OscTarget(),
) -> PlanGainResult
```

**What it does**:
- Analyzes WAV to get LUFS
- Queries current Utility Gain linear value
- Computes LUFS error: `target - measured`
- Maps error to linear delta: `err_db / 12.0`
- Clamps delta to ±clamp_linear
- Returns result with clamped flag

**Inputs**:
- `wav`: Path to WAV file for analysis
- `targets`: Compliance targets
- `clamp_linear`: Max delta magnitude (default 0.25)
- `target_osc`: OSC target for querying Ableton

**Outputs**: `PlanGainResult` dataclass:
- `delta_linear`: float (clamped)
- `lufs_i`: float (measured)
- `target_lufs`: float
- `clamped`: bool (true if delta was limited)
- `cur_linear`: float (current Utility Gain)

**Side effects**:
- Filesystem read (audio analysis)
- OSC queries (get current Utility state)
- CPU-intensive (LUFS calculation)

**Failure modes**:
- Propagates `analyze_wav` exceptions
- Propagates OSC timeout errors

**Invariants**:
- Delta magnitude never exceeds clamp_linear
- Error-to-delta scaling: `delta ≈ err_db / 12`
- Reads current state before planning (idempotent planning)

**Example**:
```python
from flaas.plan import plan_utility_gain_delta_for_master
result = plan_utility_gain_delta_for_master("input/test.wav")
print(f"Current: {result.cur_linear:.3f}, Delta: {result.delta_linear:.3f}")
```

**Where used**: `plan.write_plan_gain_actions`

**How to validate**:
```bash
flaas plan-gain input/test.wav
# Should print: CUR_LINEAR: X.XXX  DELTA: Y.YYY
```

---

### `plan.write_plan_gain_actions`
**Signature**:
```python
def write_plan_gain_actions(wav: str | Path, out_actions: str | Path = "data/actions/actions.json") -> Path
```

**What it does**:
- Calls `plan_utility_gain_delta_for_master`
- Creates GainAction for MASTER Utility Gain
- Scans Live to get current fingerprint
- Writes actions.json with schema version + fingerprint
- Prints warning if clamped
- Prints current linear + delta

**Inputs**:
- `wav`: Path to WAV file
- `out_actions`: Output JSON path

**Outputs**: `Path` to written actions file

**Side effects**:
- All effects of plan + analyze + scan
- Filesystem write (actions.json)
- Stdout print (current state + delta)

**Failure modes**:
- Propagates all upstream exceptions

**Example**:
```python
from flaas.plan import write_plan_gain_actions
path = write_plan_gain_actions("input/test.wav")
```

**Where used**:
- `cli.py` (plan-gain command)
- `loop.run_loop`

**How to validate**:
```bash
flaas plan-gain input/test.wav
cat data/actions/actions.json | jq '.live_fingerprint, .actions[0].delta_db'
```

---

### `apply.apply_actions_osc`
**Signature**:
```python
def apply_actions_osc(
    actions_path: str | Path = "data/actions/actions.json",
    target: OscTarget = OscTarget(),
    enforce_fingerprint: bool = True,
) -> None
```

**What it does**:
- Loads actions from JSON
- Validates Live fingerprint (if enforce_fingerprint=True)
- For each MASTER Utility Gain action:
  - Reads current normalized value
  - Converts to linear using param range
  - Adds delta
  - Converts back to normalized
  - Sets new value via OSC
  - Prints before/after
- Skips unsupported actions

**Inputs**:
- `actions_path`: Path to actions.json
- `target`: OscTarget for OSC commands
- `enforce_fingerprint`: Validate fingerprint (default True)

**Outputs**: None

**Side effects**:
- OSC queries (scan for fingerprint, get param range, get current value)
- OSC sets (parameter value changes)
- Stdout print (application results)

**Failure modes**:
- `RuntimeError`: Fingerprint mismatch (if enforce_fingerprint=True)
- `FileNotFoundError`: actions.json doesn't exist
- `json.JSONDecodeError`: Malformed actions.json
- `TimeoutError`: OSC communication failure

**Invariants**:
- Only applies MASTER Utility Gain (hardcoded track 0 device 0)
- Applies relative delta (not absolute)
- Reads current before setting new
- UTILITY_GAIN_PARAM_ID = 9

**Example**:
```python
from flaas.apply import apply_actions_osc
apply_actions_osc("data/actions/actions.json")
```

**Where used**:
- `cli.py` (apply command without --dry)
- `loop.run_loop`

**How to validate**:
```bash
flaas apply --dry  # Preview
flaas apply        # Execute
flaas verify       # Confirm change
```

---

### `loop.run_loop`
**Signature**:
```python
def run_loop(wav: str | Path, dry: bool = False) -> None
```

**What it does**:
- Pre-flight: Check if Utility Gain already near max (norm >= 0.99)
- Analyze WAV file
- Plan gain actions
- Apply actions (or dry-run)
- Post-verify Utility Gain (if not dry)
- Print status at each step

**Inputs**:
- `wav`: Path to WAV file for analysis
- `dry`: If True, skip OSC application

**Outputs**: None

**Side effects**:
- All effects of analyze + plan + apply
- Stdout print (progress messages)
- Early return if Utility near max

**Failure modes**:
- Propagates all upstream exceptions
- Early exit (not failure) if norm >= 0.99

**Stop conditions**:
- Utility Gain normalized >= 0.99 (hard stop, prints message)

**Example**:
```python
from flaas.loop import run_loop
run_loop("input/test.wav", dry=True)  # Preview
run_loop("input/test.wav")  # Execute
```

**Where used**: `cli.py` (loop command)

**How to validate**:
```bash
flaas reset  # Start from known state
flaas loop input/test.wav --dry
```

---

### `verify.verify_master_utility_gain`
**Signature**:
```python
def verify_master_utility_gain(track_id: int = 0, device_id: int = 0, target: OscTarget = OscTarget()) -> float
```

**What it does**:
- Queries `/live/device/get/parameter/value` for Utility Gain
- Returns normalized value (0..1)

**Inputs**:
- `track_id`: Track index (default 0)
- `device_id`: Device index (default 0)
- `target`: OscTarget

**Outputs**: float (normalized 0..1)

**Side effects**: OSC query

**Failure modes**:
- `TimeoutError`: OSC timeout
- `IndexError`: Malformed response

**Invariants**:
- UTILITY_GAIN_PARAM_ID = 9
- Response format: `(track_id, device_id, param_id, value)`
- Returns value at index 3

**Example**:
```python
from flaas.verify import verify_master_utility_gain
norm = verify_master_utility_gain()
print(f"Current normalized: {norm}")
```

**Where used**:
- `loop.run_loop` (pre-flight + post-apply)

**How to validate**:
```bash
flaas verify
```

---

### `verify_audio.verify_audio`
**Signature**:
```python
def verify_audio(path: str | Path) -> int
```

**What it does**:
- Analyzes WAV
- Checks compliance
- Prints summary (FILE, LUFS, PEAK, PASS/FAIL)
- Returns exit code

**Inputs**:
- `path`: WAV file path

**Outputs**: int (0 = PASS, 1 = FAIL)

**Side effects**:
- All effects of analyze + check
- Stdout print

**Failure modes**:
- Propagates analyze/check exceptions

**Invariants**:
- Exit code 0 iff both pass_lufs and pass_peak are True

**Example**:
```python
from flaas.verify_audio import verify_audio
import sys
sys.exit(verify_audio("output/master.wav"))
```

**Where used**: `cli.py` (verify-audio command)

**How to validate**:
```bash
flaas verify-audio input/test.wav
echo $?  # Check exit code
```

---

### `inspect_selected_device.inspect_selected_device`
**Signature**:
```python
def inspect_selected_device(target: OscTarget = OscTarget(), timeout_sec: float = 5.0, raw: bool = False) -> None
```

**What it does**:
- Queries currently selected device in Ableton Live view
- Fetches all parameter metadata (name, value, min, max, is_quantized)
- Prints formatted table or raw OSC tuples

**Inputs**:
- `target`: OscTarget (host, port)
- `timeout_sec`: Timeout per OSC query
- `raw`: Print raw tuples if True

**Outputs**: None (stdout only)

**Side effects**:
- 6 OSC queries (selected_device + 5 param metadata queries)
- Stdout print

**Failure modes**:
- `TimeoutError`: No device selected or OSC timeout

**Invariants**:
- Parameter responses: `(track_id, device_id, val0, val1, ...)`
- Data sliced from index 2 (skip track_id, device_id prefix)

**Example**:
```python
from flaas.inspect_selected_device import inspect_selected_device
inspect_selected_device()  # Prints table
inspect_selected_device(raw=True)  # Prints raw tuples
```

**Where used**: `cli.py` (inspect-selected-device command)

**How to validate**:
```bash
flaas inspect-selected-device  # Select device in Ableton first
```

---

## 3. OSC Contract Sheet

### Ports
- **AbletonOSC listen**: UDP 11000 (configurable via --port)
- **AbletonOSC reply**: UDP 11001 (configurable via --listen-port)

### Request/Response Rules
- **Fire-and-forget** (`osc.send_ping`): No reply expected
- **Request/response** (`osc_rpc.request_once`): Waits for reply on listen_port
- **Timeout**: Default 2.0s (3.0s for param queries)
- **Retries**: None (fail fast)
- **Message ordering**: No ordering guarantees

### Endpoints Used

#### Health Check
**`/live/test`**
- **Request**: `("ok",)` or custom string
- **Response**: `("ok",)` (echoes back)
- **Purpose**: Connectivity test
- **Wrapper**: `osc.send_ping` (fire-and-forget), `osc_rpc.request_once` (RPC)

#### Song Query
**`/live/song/get/num_tracks`**
- **Request**: `None` or `[]`
- **Response**: `(num_tracks,)` - single int
- **Purpose**: Get track count
- **Wrapper**: `request_once(target, "/live/song/get/num_tracks", None)`

**`/live/song/get/track_names`**
- **Request**: `[]`
- **Response**: `(name1, name2, ..., nameN)` - tuple of strings
- **Purpose**: Get all track names
- **Wrapper**: `request_once(target, "/live/song/get/track_names", [])`

#### View Selection Query
**`/live/view/get/selected_device`**
- **Request**: `[]` (empty list)
- **Response**: `(track_id, device_id)`
- **Purpose**: Get currently selected device in Ableton Live view
- **Note**: User must have device selected in Live
- **Wrapper**: `inspect_selected_device.inspect_selected_device`

#### Track Query
**`/live/track/get/num_devices`**
- **Request**: `[track_id]`
- **Response**: `(track_id, num_devices)`
- **Purpose**: Get device count for track
- **Wrapper**: `request_once(target, "/live/track/get/num_devices", [tid])`

**`/live/track/get/devices/name`** **CRITICAL QUIRK - UPDATED 2026-02-22**
- **Request**: `[track_id]`
- **Response**: `(track_id, name0, name1, name2, ...)`
- **Purpose**: Get all device names for track
- **Wrapper**: `request_once(target, "/live/track/get/devices/name", [tid])`
- **CRITICAL**: Response includes track_id as FIRST element
  - **WRONG**: `device_id = response.index("Utility")`
  - **WRONG**: `names = response[2:]` (skips track_id AND first device)
  - **RIGHT**: `names = list(response)[1:]` (skip only track_id)
  - **RIGHT**: `device_id = names.index("Utility")` (now correctly 0 for first device)
- **Used in**: `targets.resolve_utility_device_id()` - shared resolver for plan/apply/verify

**`/live/track/get/devices/class_name`**
- **Request**: `[track_id]`
- **Response**: `(track_id, class1, class2, ..., classN)`
- **Purpose**: Get all device class names for track
- **Wrapper**: `request_once(target, "/live/track/get/devices/class_name", [tid])`

#### Device Parameter Query
**`/live/device/get/parameters/min`**
- **Request**: `[track_id, device_id]`
- **Response**: `(track_id, device_id, min0, min1, ..., minN)`
- **Purpose**: Get all parameter min values for device
- **Note**: Values at index 2+ are parameter mins
- **Wrapper**: `request_once(target, "/live/device/get/parameters/min", [tid, did])`

**`/live/device/get/parameters/max`**
- **Request**: `[track_id, device_id]`
- **Response**: `(track_id, device_id, max0, max1, ..., maxN)`
- **Purpose**: Get all parameter max values for device
- **Note**: Values at index 2+ are parameter maxs
- **Wrapper**: `request_once(target, "/live/device/get/parameters/max", [tid, did])`

**`/live/device/get/parameters/value`**
- **Request**: `[track_id, device_id]`
- **Response**: `(track_id, device_id, val0, val1, ..., valN)`
- **Purpose**: Get all parameter normalized values for device
- **Note**: Values at index 2+ are parameter values (normalized 0..1)
- **Wrapper**: Used in `inspect_selected_device`

**`/live/device/get/parameters/is_quantized`**
- **Request**: `[track_id, device_id]`
- **Response**: `(track_id, device_id, q0, q1, ..., qN)`
- **Purpose**: Get quantized flag for each parameter (True=stepped, False=continuous)
- **Note**: Values at index 2+ are boolean flags
- **Wrapper**: Used in `inspect_selected_device`

**`/live/device/get/parameter/value`**
- **Request**: `[track_id, device_id, param_id]`
- **Response**: `(track_id, device_id, param_id, value)`
- **Purpose**: Get single parameter normalized value
- **Note**: Value is normalized 0..1
- **Wrapper**: `request_once(target, "/live/device/get/parameter/value", [tid, did, pid])`

#### Device Parameter Set
**`/live/device/set/parameter/value`**
- **Request**: `[track_id, device_id, param_id, value]`
- **Response**: None (fire-and-forget)
- **Purpose**: Set parameter to normalized value
- **Note**: Value must be in [0, 1]
- **Wrapper**: `SimpleUDPClient.send_message(...)`

### Known AbletonOSC Quirks

#### Quirk 1: Plural vs. Singular Endpoints
- **Wrong**: `/live/device/get/parameter/min` (singular, doesn't exist)
- **Right**: `/live/device/get/parameters/min` (plural, returns all)
- **Mitigation**: Use plural endpoints and index into results

#### Quirk 2: Response Format Inconsistency
- Some endpoints return `(value,)` (single tuple element)
- Some return `(id, value)` (prefixed with track/device ID)
- Some return `(id1, id2, value1, value2, ...)` (multiple IDs + values)
- **Mitigation**: Document expected format per endpoint, index carefully

#### Quirk 3: Normalized Parameter Values
- All `/live/device/*/parameter/value` endpoints use normalized 0..1
- Min/max from `/parameters/min|max` are in "linear" units (device-specific)
- For Utility Gain: linear is typically -1..+1, but NOT dB
- **Mitigation**: Use `param_map` module for conversions, never assume dB

#### Quirk 4: No Batch Operations
- Must query each track individually for devices
- No single endpoint to get full device tree
- **Mitigation**: Accept O(N) complexity, cache results in model_cache.json

#### Quirk 5: No Transaction Support
- Each set is immediate and independent
- No way to rollback or batch commits
- **Mitigation**: Plan carefully, use fingerprints to detect set changes

### Usage Patterns

#### Pattern: Fire-and-Forget
```python
from flaas.osc import OscTarget, send_ping
send_ping(OscTarget(host="127.0.0.1", port=11000), "/live/test", "ok")
```
**When**: Testing connectivity, don't care about reply

#### Pattern: Request/Response
```python
from flaas.osc_rpc import OscTarget, request_once
result = request_once(
    OscTarget(host="127.0.0.1", port=11000),
    "/live/song/get/num_tracks",
    None,
    listen_port=11001,
    timeout_sec=3.0
)
num_tracks = int(result[0])
```
**When**: Need data back from Ableton

#### Pattern: Parameter Set
```python
from pythonosc.udp_client import SimpleUDPClient
client = SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/device/set/parameter/value", [0, 0, 9, 0.5])
```
**When**: Setting device parameters (no reply needed)

#### Pattern: Read-Modify-Write
```python
# Read current
cur_resp = request_once(target, "/live/device/get/parameter/value", [0, 0, 9])
cur_norm = float(cur_resp[3])

# Modify
new_norm = cur_norm + 0.1  # Delta

# Write
client.send_message("/live/device/set/parameter/value", [0, 0, 9, new_norm])
```
**When**: Relative adjustments (apply.py pattern)

---

## 4. Data Artifacts + Schemas

### `data/caches/model_cache.json`

**Schema** (as of schema version - inferred):
```json
{
  "ok": bool,
  "note": string,
  "created_at_utc": "ISO8601 timestamp",
  "num_tracks": int,
  "tracks": [
    {
      "track_id": int,
      "name": string,
      "num_devices": int,
      "devices": [
        {
          "index": int,
          "name": string,
          "class_name": string
        }
      ]
    }
  ],
  "fingerprint": "SHA256 hex (64 chars)"
}
```

**Producer**: `scan.write_model_cache()`  
**Consumers**: `plan.write_plan_gain_actions()`, `apply.apply_actions_osc()`  

**Validation rules**:
- `ok` must be `true` for valid scan
- `fingerprint` must be non-empty 64-char hex string
- `tracks` array length must equal `num_tracks`

**Staleness detection**:
- Fingerprint computed from track structure (id:name:num_devices:device_classes)
- Changes if tracks added/removed/reordered or devices changed
- No timestamp-based expiration (structural only)

**Example minimal valid**:
```json
{
  "ok": true,
  "note": "live scan",
  "created_at_utc": "2026-02-22T08:00:00+00:00",
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
  "fingerprint": "abc123..."
}
```

---

### `data/actions/actions.json`

**Schema** (version 1.0):
```json
{
  "schema_version": "1.0",
  "created_at_utc": "ISO8601 timestamp",
  "live_fingerprint": "SHA256 hex or null",
  "actions": [
    {
      "track_role": "MASTER",
      "device": "Utility",
      "param": "Gain",
      "delta_db": float  // Actually linear delta, not dB (legacy name)
    }
  ]
}
```

**Producer**: `plan.write_plan_gain_actions()`  
**Consumers**: `apply.apply_actions_osc()`, `apply.apply_actions_dry_run()`  

**Validation rules**:
- `schema_version` must be "1.0"
- `live_fingerprint` should match current Live set fingerprint
- `actions` array must be present (can be empty)
- `delta_db` is actually linear delta in [-1, 1] (naming is legacy)

**Safety checks**:
- `apply` validates fingerprint by default (enforce_fingerprint=True)
- Raises RuntimeError if mismatch
- Can be bypassed with enforce_fingerprint=False

**Corruption detection**:
- JSON parse failure → `json.JSONDecodeError`
- Missing required fields → `KeyError`
- Fingerprint mismatch → detected at apply time

**Example minimal valid**:
```json
{
  "schema_version": "1.0",
  "created_at_utc": "2026-02-22T08:00:00+00:00",
  "live_fingerprint": "abc123...",
  "actions": [
    {
      "track_role": "MASTER",
      "device": "Utility",
      "param": "Gain",
      "delta_db": 0.25
    }
  ]
}
```

---

### `data/reports/analysis.json`

**Schema** (inferred):
```json
{
  "file": "path/to/file.wav",
  "sr": int,
  "channels": int,
  "samples": int,
  "duration_sec": float,
  "peak_dbfs": float,
  "lufs_i": float,
  "created_at_utc": "ISO8601 timestamp"
}
```

**Producer**: `analyze.write_analysis()`  
**Consumers**: Not directly consumed (ephemeral report)  

**Validation rules**:
- `peak_dbfs` can be `-inf` if audio is silent
- `lufs_i` should be in range [-70, 0] for typical audio
- `duration_sec` must equal `samples / sr`

**Example**:
```json
{
  "file": "input/test.wav",
  "sr": 48000,
  "channels": 1,
  "samples": 96000,
  "duration_sec": 2.0,
  "peak_dbfs": -13.98,
  "lufs_i": -17.72,
  "created_at_utc": "2026-02-22T06:28:10.149401+00:00"
}
```

---

### `data/reports/check.json`

**Schema** (inferred):
```json
{
  "file": string,
  "pass_lufs": bool,
  "pass_peak": bool,
  "lufs_i": float,
  "peak_dbfs": float,
  "target_lufs": float,
  "target_peak_dbfs": float
}
```

**Producer**: `check.write_check()`  
**Consumers**: Not directly consumed (ephemeral report)  

**Validation rules**:
- `pass_lufs` = true iff `|lufs_i - target_lufs| <= 0.5`
- `pass_peak` = true iff `peak_dbfs <= target_peak_dbfs`

**Example**:
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

---

## 5. CLI Command Sheet

### `flaas --version`
**Args**: None  
**Reads**: None  
**Writes**: None  
**Stdout**: `0.0.2`  
**Exit codes**: 0=success  
**Purpose**: Show version

---

### `flaas ping [--wait] [--host HOST] [--port PORT]`
**Args**:
- `--wait`: Wait for reply (optional)
- `--host`: Target host (default 127.0.0.1)
- `--port`: Target port (default 11000)
- `--listen-port`: Reply port (default 11001, only with --wait)
- `--timeout`: Timeout seconds (default 2.0, only with --wait)
- `--arg`: Message argument (default "ok")

**Reads**: None  
**Writes**: None (sends OSC only)  
**Stdout**:
- Without --wait: `sent`
- With --wait: `ok: ('ok',)` or timeout error

**Exit codes**:
- 0=success
- 1=timeout (with --wait)

**Purpose**: Test OSC connectivity

**Failure modes**:
- TimeoutError if AbletonOSC not responding (with --wait)
- No error for fire-and-forget (always succeeds)

---

### `flaas scan [--out PATH]`
**Args**:
- `--out`: Output path (default data/caches/model_cache.json)

**Reads**: OSC queries to AbletonOSC  
**Writes**: model_cache.json  
**Stdout**: Path to written file  
**Exit codes**: 0=success  

**Purpose**: Scan Live set structure and generate fingerprint

**Failure modes**:
- Writes failed scan result with error message (never crashes)
- `ok: false` in JSON if scan failed

---

### `flaas analyze <wav> [--out PATH]`
**Args**:
- `wav`: Path to WAV file (required)
- `--out`: Output path (default data/reports/analysis.json)

**Reads**: WAV file  
**Writes**: analysis.json  
**Stdout**: Path to written file  
**Exit codes**: 0=success, 1=error  

**Purpose**: Measure peak dBFS + LUFS-I

**Failure modes**:
- ValueError if audio is empty
- FileNotFoundError if WAV doesn't exist
- soundfile exceptions for invalid files

---

### `flaas check <wav> [--out PATH]`
**Args**:
- `wav`: Path to WAV file (required)
- `--out`: Output path (default data/reports/check.json)

**Reads**: WAV file  
**Writes**: check.json  
**Stdout**: Path to written file  
**Exit codes**: 0=success, 1=error  

**Purpose**: Check compliance against targets

**Failure modes**: Same as analyze (reuses analyze_wav)

---

### `flaas plan-gain <wav> [--out PATH]`
**Args**:
- `wav`: Path to WAV file (required)
- `--out`: Output path (default data/actions/actions.json)

**Reads**: WAV file + OSC queries (Utility state + Live scan)  
**Writes**: actions.json  
**Stdout**:
- Path to written file
- `CUR_LINEAR: X.XXX  DELTA: Y.YYY`
- Optional: `WARNING: delta clamped to Z.ZZZ`

**Exit codes**: 0=success, 1=error  

**Purpose**: Compute bounded Utility Gain delta

**Failure modes**:
- All modes from analyze + OSC communication
- Clamps delta to ±0.25 (warning, not error)

---

### `flaas apply [--actions PATH] [--dry] [--host HOST] [--port PORT]`
**Args**:
- `--actions`: Actions file path (default data/actions/actions.json)
- `--dry`: Dry-run mode (print only, no OSC sets)
- `--host`: OSC host (default 127.0.0.1)
- `--port`: OSC port (default 11000)

**Reads**: actions.json + OSC queries (fingerprint, param range, current value)  
**Writes**: OSC parameter sets (unless --dry)  
**Stdout**:
- With --dry: `DRY_RUN: ...`
- Without --dry: `APPLIED: Utility.Gain X.XXX -> Y.YYY (norm A.AAA->B.BBB)`
- Or: `SKIP: unsupported action ...`

**Exit codes**:
- 0=success
- 1=fingerprint mismatch or other error

**Purpose**: Execute planned actions

**Failure modes**:
- RuntimeError if Live fingerprint mismatch (with enforce_fingerprint=True)
- TimeoutError for OSC failures
- FileNotFoundError if actions.json missing

---

### `flaas verify [--track-id ID] [--device-id ID] [--host HOST] [--port PORT]`
**Args**:
- `--track-id`: Track index (default 0)
- `--device-id`: Device index (default 0)
- `--host`, `--port`: OSC target

**Reads**: OSC query  
**Writes**: None  
**Stdout**: Normalized value (e.g., `0.625`)  
**Exit codes**: 0=success, 1=error  

**Purpose**: Read current Utility Gain normalized value

---

### `flaas reset [--host HOST] [--port PORT]`
**Args**:
- `--host`, `--port`: OSC target

**Reads**: None  
**Writes**: OSC parameter set  
**Stdout**: `sent`  
**Exit codes**: 0=success  

**Purpose**: Set Utility Gain to center (norm=0.5)

---

### `flaas loop <wav> [--dry]`
**Args**:
- `wav`: Path to WAV file (required)
- `--dry`: Dry-run mode (no OSC sets)

**Reads**: WAV + OSC queries  
**Writes**: actions.json + OSC sets (unless --dry)  
**Stdout**:
- `STOP: ...` (if Utility near max)
- `MEASURE: LUFS=X.XX peak_dBFS=Y.YY`
- `CUR_LINEAR: X.XXX  DELTA: Y.YYY`
- With --dry: `DONE: planned (dry-run, no OSC)`
- Without --dry: `APPLIED: ...`, `DONE: planned+applied (norm=Z.ZZZ)`

**Exit codes**: 0=success, 1=error  

**Purpose**: Full workflow (analyze → plan → apply)

**Stop conditions**:
- Utility Gain norm >= 0.99 (early exit with message)

---

### `flaas verify-audio <wav>`
**Args**:
- `wav`: Path to WAV file (required)

**Reads**: WAV file  
**Writes**: None  
**Stdout**:
```
FILE: path/to/file.wav
LUFS: X.XX (target Y.YY)  pass=True/False
PEAK: X.XX dBFS (limit Y.YY) pass=True/False
PASS or FAIL
```

**Exit codes**:
- 0=PASS (both checks pass)
- 1=FAIL (one or both checks fail)

**Purpose**: Combined analysis + compliance check

---

### `flaas export-guide`
**Args**: None  
**Reads**: None  
**Writes**: None  
**Stdout**: Ableton export settings checklist  
**Exit codes**: 0=success  
**Purpose**: Print standardized export settings

---

### `flaas util-gain-norm <track_id> <device_id> <gain_norm> [--host HOST] [--port PORT]`
**Args**:
- `track_id`: Track index (required)
- `device_id`: Device index on track (required)
- `gain_norm`: Normalized value 0..1 (required)

**Reads**: None  
**Writes**: OSC parameter set  
**Stdout**: `sent`  
**Exit codes**: 0=success  

**Purpose**: Direct Utility Gain control (normalized)

---

### `flaas util-gain-linear <track_id> <device_id> <gain_linear> [--host HOST] [--port PORT]`
**Args**:
- `track_id`: Track index (required)
- `device_id`: Device index on track (required)
- `gain_linear`: Linear value, e.g., -1..+1 (required)

**Reads**: OSC queries (param min/max)  
**Writes**: OSC parameter set  
**Stdout**: `sent`  
**Exit codes**: 0=success  

**Purpose**: Direct Utility Gain control (linear range)

---

## 6. Call Graph + Boundaries

### Golden Path: `flaas loop <wav>`

```
cli.main()
  └─ run_loop(wav)
       ├─ verify_master_utility_gain()  [OSC boundary]
       │    └─ request_once() → AbletonOSC
       ├─ analyze_wav(wav)  [Audio boundary]
       │    ├─ read_audio_info()
       │    └─ read_mono_float()
       ├─ write_plan_gain_actions(wav)  [Planning boundary]
       │    ├─ plan_utility_gain_delta_for_master()
       │    │    ├─ analyze_wav()
       │    │    └─ _get_current_utility_linear()
       │    │         ├─ get_param_range() [OSC boundary]
       │    │         └─ request_once()
       │    ├─ write_actions()  [Filesystem boundary]
       │    └─ scan_live()  [OSC boundary]
       ├─ apply_actions_osc()  [OSC boundary]
       │    ├─ scan_live() (fingerprint check)
       │    ├─ get_param_range()
       │    ├─ request_once() (read current)
       │    └─ send_message() (set new)
       └─ verify_master_utility_gain()  [OSC boundary]
```

### Boundaries

#### OSC Boundary
**Modules**: `osc.py`, `osc_rpc.py`  
**Entry points**: `send_ping()`, `request_once()`  
**Responsibility**: All network communication with AbletonOSC  
**Stability**: Core primitive - changes ripple to all OSC users  
**Testing**: Requires Ableton Live + AbletonOSC running

#### Filesystem Boundary
**Modules**: `audio_io.py`, `actions.py`, `scan.py`, `analyze.py`, `check.py`  
**Entry points**: `read_*`, `write_*` functions  
**Responsibility**: All file I/O  
**Stability**: Core primitive - schemas are versioned  
**Testing**: Unit testable with temp files

#### Audio Analysis Boundary
**Modules**: `audio_io.py`, `analyze.py`  
**Entry points**: `analyze_wav()`  
**Responsibility**: Audio DSP (peak, LUFS)  
**Stability**: Core primitive - uses standard algorithms  
**Testing**: Unit testable with synthetic audio

#### Planning Boundary
**Modules**: `plan.py`, `param_map.py`  
**Entry points**: `plan_utility_gain_delta_for_master()`  
**Responsibility**: Decision logic (error → action)  
**Stability**: Leaf utility - tuning parameters may change  
**Testing**: Unit testable with mocked analyze/OSC

---

## 7. Determinism + Reproducibility

### Nondeterministic Sources

| Command | Nondeterministic Elements | How to Pin |
|---------|---------------------------|------------|
| `scan` | Live set state, timestamp | Not pinnable (external state) |
| `analyze` | Timestamp only | Audio content deterministic |
| `check` | Timestamp only | Results deterministic for same audio |
| `plan-gain` | Current Utility state, Live fingerprint, timestamp | Reset Utility, freeze Live set |
| `apply` | Current Utility state, Live fingerprint | Regenerate actions before apply |
| `loop` | All of the above | Full reset + regeneration |

### Repro Bundle Checklist

To reproduce a failure, attach:
1. **Command executed**: Exact command line
2. **Terminal output**: Full stdout/stderr
3. **Input files**: WAV files used (if applicable)
4. **Artifact files**:
   - `data/caches/model_cache.json`
   - `data/actions/actions.json`
   - `data/reports/*.json`
5. **Ableton state**:
   - Screenshot of track list + devices
   - Control Surface configuration
   - AbletonOSC version (if known)
6. **Environment**:
   - `flaas --version`
   - `python3 --version`
   - `pip list | grep -E "(flaas|python-osc|numpy|soundfile|pyloudnorm)"`

### Logging Fields for Repro

**Minimal**:
- Timestamp (UTC ISO8601)
- Command executed
- Exit code
- Stdout/stderr

**Ideal** (future):
- OSC endpoints called + responses
- File hashes (SHA256 of inputs)
- Fingerprints (Live set state)
- Parameter values (before/after)

---

## 8. Testing Map

### Unit Tests (No Ableton Required)

| Module | Test Focus | Command |
|--------|------------|---------|
| `audio_io` | WAV loading, mono conversion | `pytest tests/test_audio_io.py` |
| `analyze` | Peak/LUFS calculation | `pytest tests/test_analyze.py` |
| `check` | Compliance logic | `pytest tests/test_check.py` |
| `param_map` | Linear↔norm conversion | `pytest tests/test_param_map.py` |
| `actions` | JSON serialization | `pytest tests/test_actions.py` |

**What it proves**: Internal logic correctness  
**What it doesn't prove**: OSC communication, Live set interaction

### Integration Tests (AbletonOSC Required)

| Feature | Test Focus | Command |
|---------|------------|---------|
| OSC ping | Connectivity | `flaas ping --wait` |
| Scan | Live set query | `flaas scan` |
| Verify | Parameter readback | `flaas verify` |
| Util control | Parameter set | `flaas util-gain-norm 0 0 0.5 && flaas verify` |
| Apply | Action execution | `flaas apply --dry` (no Ableton), `flaas apply` (with Ableton) |

**What it proves**: OSC protocol correctness, AbletonOSC integration  
**What it doesn't prove**: Audio analysis correctness

### Smoke Tests (One-Command Environment Checks)

```bash
# Python environment
python3 -m compileall src/flaas/

# Package installation
python3 -c "import flaas; print(flaas.__version__)"

# CLI wiring
flaas --version

# OSC connectivity
flaas ping --wait

# Live set accessibility
flaas scan && cat data/caches/model_cache.json | jq '.ok'

# Parameter control
flaas reset && flaas verify
```

**What it proves**: Environment is correctly configured  
**What it doesn't prove**: Full workflow correctness

---

## 9. Reliability Patterns

### Retry/Backoff Rules

**Current policy**: No retries (fail fast)

**Why**: OSC requests are idempotent; retry logic adds complexity without clear benefit in MVP.

**When retries would be safe**:
- GET requests (`/live/song/get/*`, `/live/device/get/*`)
- Idempotent SETs (absolute value sets)

**When retries are unsafe**:
- Relative adjustments (read-modify-write race)
- No transaction support in AbletonOSC

**Future consideration**: Add retry only for read operations with exponential backoff.

### Cache Invalidation Rules

**Fingerprint-based**:
- `model_cache.json` fingerprint changes when Live set structure changes
- `actions.json` fingerprint must match current Live set
- No timestamp-based expiration

**Schema versioning**:
- `actions.json` includes `schema_version` field
- Future: Reject old schema versions or migrate

**Staleness detection**:
- `apply` compares expected vs. current fingerprint
- Raises RuntimeError on mismatch
- User must re-scan + re-plan

### Safety Invariants (MUST NEVER BYPASS)

1. **Fingerprint enforcement**:
   - `apply_actions_osc()` validates fingerprint by default
   - Only bypass with explicit `enforce_fingerprint=False`

2. **Gain clamps**:
   - Delta clamp: ±0.25 linear (in `plan.py`)
   - Max gain: norm >= 0.99 stops loop (in `loop.py`)
   - Normalized value clamp: [0, 1] (in all set functions)

3. **Parameter range validation**:
   - All normalized values clamped to [0, 1]
   - Linear values clamped to [min, max] from param range

4. **Relative delta application**:
   - `apply` always reads current before setting new
   - Never sets absolute values (except reset and util-gain-* direct commands)

### Safe Defaults

| Parameter | Default | Why |
|-----------|---------|-----|
| OSC timeout | 2.0s | Balance responsiveness vs. reliability |
| Param timeout | 3.0s | Parameter queries can be slower |
| Delta clamp | ±0.25 | Prevent large jumps, enable iteration |
| Loop max norm | 0.99 | Safety margin before absolute maximum |
| LUFS tolerance | ±0.5 LU | Industry standard "close enough" |

---

## 10. Troubleshooting Playbook

### Decision Tree

```
START: Command failed
  │
  ├─ "command not found" → [Packaging]
  │   Next: which flaas || python3 -m flaas.cli --help
  │
  ├─ "ModuleNotFoundError" / "ImportError" → [Packaging]
  │   Next: pip install -e .
  │
  ├─ "TimeoutError" → [Connectivity/Ports]
  │   Next: flaas ping --wait --timeout 5.0
  │
  ├─ "Live fingerprint mismatch" → [Schema Mismatch]
  │   Next: flaas scan && flaas plan-gain <wav>
  │
  ├─ "empty audio" / "FileNotFoundError" → [Audio/Paths]
  │   Next: ls -la input/test.wav && file input/test.wav
  │
  ├─ "PermissionError" → [Paths/Permissions]
  │   Next: ls -la data/ && mkdir -p data/caches data/reports data/actions
  │
  └─ Other → [Ableton Config]
      Next: flaas scan && cat data/caches/model_cache.json
```

### Category: Connectivity/Ports

**Symptoms**:
- `TimeoutError: Timed out waiting for reply`
- No response from AbletonOSC

**Diagnostic command**:
```bash
flaas ping --wait --timeout 5.0
```

**Expected output**: `ok: ('ok',)`

**If fails**:
1. Check Ableton Live is running
2. Check Preferences → Link/Tempo/MIDI → Control Surface: AbletonOSC in slot 1
3. Check AbletonOSC folder exists: `ls ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC`
4. Check ports: `lsof -i :11000 -i :11001`
5. Restart Ableton Live

---

### Category: Ableton Config

**Symptoms**:
- Scan returns 0 tracks or `ok: false`
- Device queries fail
- Utility not found

**Diagnostic command**:
```bash
flaas scan
cat data/caches/model_cache.json | jq '{ok, num_tracks, tracks: .tracks[] | {name, devices: .devices[].class_name}}'
```

**Expected output**: `ok: true`, at least 1 track, track 0 should have Utility device

**If fails**:
1. Verify Live has tracks in current set
2. Verify track 0 (first track) has Utility device in first slot
3. Try creating a simple test set: 1 audio track with Utility in first device slot
4. Re-scan after set changes

---

### Category: Schema Mismatch

**Symptoms**:
- `RuntimeError: Live fingerprint mismatch`
- Actions rejected

**Diagnostic command**:
```bash
flaas scan
cat data/caches/model_cache.json | jq '.fingerprint'
cat data/actions/actions.json | jq '.live_fingerprint'
```

**Expected output**: Both fingerprints should match

**If they don't match**:
```bash
flaas plan-gain input/test.wav  # Regenerate with current fingerprint
flaas apply  # Should now succeed
```

**Root cause**: Live set structure changed between plan and apply

---

### Category: Audio Analysis

**Symptoms**:
- `ValueError: empty audio`
- Unexpected LUFS/peak values
- Analysis crashes

**Diagnostic command**:
```bash
ls -la input/test.wav
file input/test.wav
soxi input/test.wav  # If sox installed
flaas analyze input/test.wav
```

**Expected output**: Valid WAV file, analysis.json with reasonable values

**If fails**, regenerate test file:
```python
import numpy as np, soundfile as sf, os
os.makedirs("input", exist_ok=True)
sr = 48000
t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
x = 0.2*np.sin(2*np.pi*440*t)
sf.write("input/test.wav", x, sr)
print("wrote input/test.wav")
```

---

### Category: Packaging

**Symptoms**:
- `command not found: flaas`
- `ModuleNotFoundError: No module named 'flaas'`

**Diagnostic commands**:
```bash
which flaas
python3 -m flaas.cli --help
pip show flaas
```

**Fix sequence**:
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate  # If venv exists
pip install -e .
python3 -m flaas.cli --version  # Should print 0.0.2
```

---

## 11. Contribution Rules

### Naming Conventions

**Modules**: lowercase_with_underscores  
**Classes**: PascalCase (e.g., `OscTarget`, `AnalysisResult`)  
**Functions**: lowercase_with_underscores  
**Constants**: UPPER_CASE (e.g., `UTILITY_GAIN_PARAM_ID`)  
**Private helpers**: `_leading_underscore`

### Module Layout Rules

**Import order**:
1. `from __future__ import annotations` (always first)
2. Standard library imports
3. Third-party imports (numpy, soundfile, pythonosc, etc.)
4. Local flaas imports

**Module structure**:
1. Imports
2. Constants
3. Dataclasses
4. Helper functions (private)
5. Public functions
6. No module-level side effects

### Docstring Style

**Functions**:
```python
def function_name(arg: Type) -> ReturnType:
    """
    One-line summary (imperative mood).
    
    Optional longer description.
    """
```

**Keep docstrings minimal** - code should be self-explanatory.

### Where to Add Features

**New OSC endpoint**: Add to `osc.py` (fire-and-forget) or `osc_rpc.py` (request/response)  
**New data artifact**: Add schema to `actions.py` or create new module in `src/flaas/`  
**New CLI command**: Add parser + handler in `cli.py`, implement logic in dedicated module  
**New analysis metric**: Add to `analyze.py` or create new module  
**New device control**: Add to `util.py` or create `devices/` package

### "How to Add a Feature" Checklist

1. **Plan**: Define one atomic task with clear validation command
2. **Create module** (if needed): `src/flaas/new_feature.py`
3. **Implement logic**: Pure functions where possible
4. **Add CLI wiring**: Parser in `cli.py`, import at top, handler in main()
5. **Test manually**: Run validation command, paste output
6. **Update docs**: Add to README.md commands list, update this notebook
7. **Commit**: `git add -A && git commit -m "feat: add new feature" && git push`
8. **Paste**: Share git push output

### Edit→Run→Paste Loop

**Standard flow**:
1. Agent edits files
2. Agent runs validation command
3. Agent pastes terminal output
4. Agent commits if success
5. Human provides next task

**On error**:
1. Agent pastes error output
2. Agent diagnoses error class
3. Agent runs single-command probe
4. Agent pastes probe output
5. Agent fixes and re-validates

---

## Appendix: Constants Quick Reference

```python
# Module: flaas/util.py, flaas/apply.py, flaas/verify.py, flaas/plan.py
UTILITY_GAIN_PARAM_ID = 9

# Module: flaas/targets.py
DEFAULT_TARGETS = Targets(
    master_lufs=-10.5,
    true_peak_ceiling_dbfs=-1.0,
    stem_peak_ceiling_dbfs=-6.0
)

# Module: flaas/plan.py (function parameter)
clamp_linear = 0.25  # Max delta magnitude

# Module: flaas/loop.py (hardcoded)
MAX_UTILITY_NORM = 0.99  # Stop condition

# Module: flaas/check.py (hardcoded)
LUFS_TOLERANCE = 0.5  # ± LU

# Master track/device resolution (UPDATED 2026-02-22)
MASTER_TRACK_ID = -1000  # NOT 0!
# Utility device ID is DYNAMIC (query /live/track/get/devices/name)
# Use resolve_utility_device_id() from targets.py
```

---

## Appendix: Common Code Patterns

### Pattern: Read WAV → Analyze → Write JSON
```python
from flaas.audio_io import read_audio_info, read_mono_float
info = read_audio_info(path)
mono, sr = read_mono_float(path)
# ... compute metrics ...
result = SomeResult(...)
Path(out).write_text(json.dumps(asdict(result), indent=2) + "\n")
```
**Used in**: `analyze.py`, `check.py`

### Pattern: OSC Query → Parse → Return
```python
from flaas.osc_rpc import request_once, OscTarget
resp = request_once(OscTarget(), "/some/endpoint", [arg1, arg2])
value = float(resp[expected_index])
return value
```
**Used in**: `scan.py`, `param_map.py`, `verify.py`, `plan.py`

### Pattern: Load JSON → Process → OSC Set
```python
from pathlib import Path
import json
obj = json.loads(Path(path).read_text())
for item in obj.get("some_list", []):
    # ... process ...
    client.send_message("/endpoint", [args])
```
**Used in**: `apply.py`

---

## 12. Unique Line Ledger

For maximum transparency, every unique line of code in the FLAAS codebase has been cataloged with all its occurrences.

### Overview

- **Location**: `docs/reference/unique-lines/`
- **Total unique lines**: 469
- **Total occurrences**: 619 (some lines appear in multiple files)
- **Files processed**: 18 Python modules in `src/flaas/`

### Categories

The ledger is split into 11 category files for easier navigation:

| Category | Unique Lines | Description |
|----------|-------------|-------------|
| **[logic.md](unique-lines/logic.md)** | 278 | Core logic, control flow, computations |
| **[cli_wiring.md](unique-lines/cli_wiring.md)** | 52 | CLI argument parsing, command routing |
| **[imports.md](unique-lines/imports.md)** | 41 | Import statements |
| **[definitions.md](unique-lines/definitions.md)** | 35 | Function and class definitions |
| **[safety.md](unique-lines/safety.md)** | 19 | Assertions, error handling, validation |
| **[osc_calls.md](unique-lines/osc_calls.md)** | 17 | OSC communication (send/receive) |
| **[planning.md](unique-lines/planning.md)** | 12 | Planning and decision logic |
| **[file_io.md](unique-lines/file_io.md)** | 7 | Filesystem operations |
| **[comments.md](unique-lines/comments.md)** | 4 | Inline comments |
| **[constants.md](unique-lines/constants.md)** | 2 | Global constants |
| **[decorators.md](unique-lines/decorators.md)** | 2 | Decorators (@dataclass, etc.) |

### Most Repeated Lines

Top 10 lines that appear in multiple files:

1. `from __future__ import annotations` - 15 occurrences (all modules)
2. `return` - 15 occurrences
3. `)` - 11 occurrences (end of multi-line calls)
4. `from pathlib import Path` - 9 occurrences
5. `"""` - 8 occurrences (docstrings)
6. `@dataclass` - 7 occurrences
7. `from dataclasses import dataclass` - 7 occurrences
8. `@dataclass(frozen=True)` - 7 occurrences
9. `import json` - 5 occurrences
10. `return out` - 5 occurrences

### Usage

**Find all occurrences of a specific line**:
```bash
grep -r "line text" docs/reference/unique-lines/*.md
```

**See all OSC-related code**:
```bash
cat docs/reference/unique-lines/osc_calls.md
```

**Find repeated patterns**:
```bash
jq '.most_repeated' docs/reference/unique-lines/stats.json
```

### Regeneration

To regenerate the ledger (e.g., after code changes):

```bash
python3 scripts/generate_unique_lines.py
```

**When to regenerate**:
- After adding/removing modules
- After significant refactoring
- Before major releases (for audit)

### Purpose

1. **Transparency**: Every line of code is accounted for
2. **Deduplication analysis**: Identify repeated patterns that could be factored out
3. **Refactoring aid**: Find all instances of a pattern to change
4. **Audit trail**: Track every line's usage across the codebase
5. **Code review**: Spot inconsistencies or unexpected duplications

### Example: Finding All Parameter Value Sets

To find everywhere we set OSC parameter values:

```bash
grep "send_message.*parameter/value" docs/reference/unique-lines/osc_calls.md
```

This shows all files/lines where parameters are set via OSC.

---

**End of Engineering Notebook**

For updates or additions, edit this file and commit.  
For questions, cross-reference with source code (src/flaas/).

**Unique Line Ledger**: See [unique-lines/INDEX.md](unique-lines/INDEX.md) for complete line-by-line transparency.
