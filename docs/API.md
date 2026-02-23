# FLAAS API Reference

**Core Python modules for Ableton Live OSC automation.**

---

## Entry Points

### CLI (`cli.py`)
Command-line interface. Parses arguments and dispatches to appropriate modules.

**Usage:**
```bash
flaas <command> [options]
```

**Key Commands:**
- `master-premium` - Autonomous Waves optimization
- `master-consensus` - Stock Ableton mastering
- `verify-audio` - LUFS/True Peak analysis
- `scan` - Project structure inspection
- `device-set-param` - Direct parameter control

---

## Mastering Engines

### `master_premium.py`
**Autonomous optimization with Waves C6/SSL/L3 + Saturator.**

```python
def master_premium(
    target: OscTarget = OscTarget(),
    auto_export_enabled: bool = True,
    mode: str = "loud_preview",
    skip_prompts: bool = False,
) -> int
```

**Modes:**
- `loud_preview`: -9 LUFS, -1 dBTP (commercial competitive)
- `streaming_safe`: -14 LUFS, -1 dBTP (Spotify official)
- `headroom`: -10 LUFS, -2 dBTP (internal preview)

**Workflow:**
1. Pre-flight checks (master fader, device chain order)
2. Resolve device IDs by name (C6, SSL, Saturator, L3)
3. Set initial parameters (mode-dependent)
4. **Loop** (up to 15 iterations):
   - Set parameters via OSC
   - Auto-export via UI automation
   - Analyze LUFS/True Peak
   - Adapt parameters based on gap to target
   - Stop if converged or diminishing returns
5. Log full history to JSONL

### `master_consensus.py`
**Stock Ableton chain (Utility → EQ → Glue → Saturator → Limiter).**

Similar workflow but with stock devices only. Useful for projects without Waves plugins.

---

## OSC Communication

### `osc_rpc.py`
**Request/response RPC over OSC.**

```python
@dataclass(frozen=True)
class OscTarget:
    host: str = "127.0.0.1"
    port: int = 11000  # AbletonOSC listen port

def request_once(
    target: OscTarget,
    address: str,
    value: Any = 1,
    listen_port: int = 11001,  # Reply port
    timeout_sec: float = 2.0,
) -> tuple[Any, ...]
```

**How it works:**
1. Spin up temporary OSC server on `listen_port`
2. Send message to `target.host:target.port`
3. Wait for reply on `listen_port`
4. Return reply args as tuple
5. Shutdown server

**Critical:** Only one RPC at a time (listen port conflict). For fire-and-forget use `osc.py` instead.

### `osc.py`
**Fire-and-forget OSC messaging (no reply expected).**

```python
def send_ping(target: OscTarget = OscTarget()) -> None
```

---

## Audio Analysis

### `analyze.py`
**LUFS/Peak/True Peak measurement.**

```python
def analyze_wav(wav_path: str | Path) -> dict[str, float]
```

**Returns:**
```python
{
    "lufs_i": float,        # Integrated loudness (LUFS)
    "peak_dbfs": float,     # Sample peak (dBFS)
    "true_peak_dbtp": float # True peak (dBTP, 4x oversample approx)
}
```

**Implementation:**
- LUFS: `pyloudnorm.Meter` (ITU-R BS.1770-4)
- True Peak: `scipy.signal.resample` (4x upsample) + peak detection

### `verify_audio.py`
**CLI wrapper for audio verification.**

```bash
flaas verify-audio <file.wav>
```

Prints LUFS/Peak/True Peak with pass/fail against default targets.

---

## Export Automation

### `ui_export_macos.py`
**macOS UI automation for Ableton export (AppleScript).**

```python
def auto_export_wav(out_path: str | Path, timeout_s: int = 600) -> None
```

**Strategy:**
1. Delete existing file (avoid overwrite prompt)
2. AppleScript to:
   - Bring Ableton frontmost
   - Close plugin windows
   - Open File → Export Audio/Video
   - Click "Export" button
   - Navigate to folder (Cmd+Shift+G)
   - Enter filename
   - Click "Save"
3. Wait for file to appear + stabilize (size/mtime unchanged for 2 checks)
4. Raise error if timeout or file missing

**Requirements:**
- macOS
- Terminal.app has Accessibility + Automation permissions

---

## Pre-flight Checks

### `preflight.py`
**Validates master chain state before optimization.**

```python
def run_preflight_checks(
    track_id: int,
    target: OscTarget = OscTarget(),
    expected_chain: list[str] | None = None,
    skip_prompts: bool = False
) -> bool
```

**Checks:**
1. Master fader at 0.0 dB (via OSC or user confirmation)
2. Device chain order matches expected (case-insensitive, partial match)

**Why:**
- Master fader post-chain defeats limiter ceiling
- Device order affects signal flow (compression before limiting, etc.)

---

## Utilities

### `targets.py`
**Constants and device resolution.**

```python
MASTER_TRACK_ID = -1000

@dataclass(frozen=True)
class Targets:
    master_lufs: float = -10.5
    true_peak_ceiling_dbfs: float = -1.0
    stem_peak_ceiling_dbfs: float = -6.0

def resolve_utility_device_id(target: OscTarget = OscTarget()) -> int
```

### `util.py`
**Common parameter setters.**

```python
UTILITY_GAIN_PARAM_ID = 9

def set_utility_gain_norm(track_id: int, device_id: int, gain_norm_0_1: float, ...)
def set_utility_gain_linear(track_id: int, device_id: int, gain_linear: float, ...)
```

### `param_map.py`
**Parameter range queries and normalization.**

```python
def get_param_range(track_id: int, device_id: int, param_id: int, ...) -> ParamRange
def linear_to_norm(linear_val: float, pr: ParamRange) -> float
```

---

## Track Indexing (AbletonOSC)

**Convention:**
- Regular tracks: `0, 1, 2, ...`
- Return tracks: `-1, -2, -3, ...`
- **Master track: `-1000`**

**Device indexing:** `0, 1, 2, ...` (left to right in chain)

---

## Error Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General failure |
| `10` | Skip only (no failures) |
| `20` | Read failure (OSC timeout, missing data) |
| `30` | Write failure (parameter set failed) |

---

## Testing

```bash
make smoke       # 7s, read-only sanity checks
make write-fast  # 9s, write tests (dev gate)
make write       # 39s, full suite (commit gate)
```

**Smoke tests:** `scripts/run_smoke_tests.sh`

---

## Example: Custom Optimization Loop

```python
from flaas.osc_rpc import OscTarget, request_once
from flaas.targets import MASTER_TRACK_ID
from flaas.analyze import analyze_wav
from pythonosc.udp_client import SimpleUDPClient

target = OscTarget(host="127.0.0.1", port=11000)

# Get device names
resp = request_once(target, "/live/track/get/devices/name", [MASTER_TRACK_ID])
names = list(resp)[1:]  # Drop track_id
limiter_id = names.index("Limiter")

# Set limiter ceiling to -1.0 dB
client = SimpleUDPClient(target.host, target.port)
client.send_message("/live/device/set/parameter/value", 
                    [MASTER_TRACK_ID, limiter_id, 3, 0.5])  # param 3 = ceiling

# Export manually in Ableton

# Analyze
result = analyze_wav("output/test.wav")
print(f"LUFS: {result['lufs_i']:.2f}")
print(f"True Peak: {result['true_peak_dbtp']:.2f} dBTP")
```

---

**See source code for full implementation details.**
