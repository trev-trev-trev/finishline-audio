# Finish Line Audio Automation System (FLAAS)

**Technical implementation spec (Cursor handoff)**
Scope: **objective polish only** (no creative changes). Process: **render → measure → adjust → re-render**, max 2 loops.

**Policy Version:** `0.1-mvp`

---

# 0) Critical Prerequisites

## 0.0 Stem Definition (lock this first)

**What is a "stem export" in this system:**

Stems are:
* **Post-fader** (volume automation applied)
* **Post-insert-FX** (track's device chain applied including group FX)
* **Pre-master-chain** (master bus processing NOT included)
* **Returns policy (LOCKED):** Return tracks (reverb, delay) are **always exported as separate stems**. Source stems exclude return FX. This ensures repeatability song-to-song.
* **Routing:** Group tracks only (not individual tracks within groups). Child tracks within groups are summed into the group export.

**Required stem filenames per song (EXACT LIST):**
```
VOCAL_LEAD.wav   (lead vocal group, post-group-FX, post-fader, returns excluded)
VOCAL_BG.wav     (background vocal group, post-group-FX, post-fader, returns excluded)
KICK.wav         (kick group, post-group-FX, post-fader, returns excluded)
DRUMS.wav        (drums group excluding kick, post-group-FX, post-fader, returns excluded)
BASS.wav         (bass group, post-group-FX, post-fader, returns excluded)
MUSIC.wav        (music/instruments group, post-group-FX, post-fader, returns excluded)
FX.wav           (FX/fills group, post-group-FX, post-fader, returns excluded)
REVERB_RETURN.wav (reverb return track only, isolated)
Master.wav       (premaster sum, post-master-chain for reference verification)
```

**Validation enforced:** All 9 files must exist for validation to pass. If a track role doesn't exist in a song (e.g., no VOCAL_BG), export silence or omit and document in config.

This definition is **locked for MVP**. Do not mix individual tracks and groups. Do not vary returns policy.

## 0.1 Export Policy (non-negotiable, machine-verifiable)

All stem/master exports from Ableton MUST use these settings:

* **Normalization: OFF** (critical - invalidates peak/loudness measurements)
* **Dither: None** (or consistent POW-r 1 if bit depth < 32)
* **Sample Rate: 48000 Hz** (must match project SR exactly)
* **Bit Depth: 24-bit minimum** (32-bit float preferred)
* **Start Time: 1.1.1** (consistent across all stems)
* **Length: Same duration** (pad silence at end if needed)
* **Render Format: WAV**
* **Master FX: Pre-master-chain (see stem definition above)**

**If these settings vary between exports, analysis results will be invalid and corrections will be wrong.**

### Export Policy Verification

**Tracking ≠ Verification.** You cannot truly verify export settings from WAV alone (normalization is invisible).

Every `report.json` must include:

```json
{
  "export_policy": {
    "assumed": {
      "normalization": false,
      "sample_rate": 48000,
      "bit_depth": 24,
      "dither": "none",
      "returns_policy": "separate_stems"
    },
    "confirmed": false,
    "confirmation_method": "user_manual",
    "note": "Assumed from config. User must verify manually. Set confirmed=true only after user toggles or Ableton-side verifier implemented."
  }
}
```

**MVP:** `confirmed` stays `false` unless user manually verifies checklist and toggles in config.

**Phase 2:** Programmatic verification via:
* WAV header inspection (sample rate, bit depth - can detect)
* Reference file comparison (normalization - cannot detect reliably)
* Ableton-side script that logs export settings

## 0.2 Action Whitelist (enforces "no taste changes")

**Policy Version 0.1-mvp allows ONLY these parameter changes:**

| Device | Allowed Parameters | Allowed Operations | Notes |
|--------|-------------------|-------------------|-------|
| Utility | Gain | Set dB value | Clamp: ±6 dB per iteration |
| Utility | Bass Mono | Enable (master only) | Boolean on/off |
| EQ Eight | Band 1-2 Gain | Set dB value (cuts only) | Max -3 dB, no boosts |
| EQ Eight | Band 1-2 Frequency | Set Hz value | Range: 20-20000 Hz |
| EQ Eight | Band 1-2 Q | Set Q value | Range: 0.7-4.0 |
| EQ Eight | Band 1-2 On | Enable | Boolean on/off |
| Limiter | Ceiling | Set dB value | Fixed: -1.0 dB |
| Compressor | Threshold | Set dB value (optional) | Max -3 dB shift |

**Anything else is BLOCKED:**
- All "character" params (Drive, Saturation, Color, Warmth)
- All modulation params (Rate, Depth, Width except Utility mono-bass)
- All time-based params (Reverb Size, Delay Time, Attack/Release unless compressor)
- All filter types beyond EQ peaking (no shelves, no high/low-pass in MVP)
- All boosts (only cuts allowed)

If a rule attempts to set a blocked parameter, system must **hard fail** with clear error message.

## 0.3 Naming Convention

Exported stems must match track role names or be mapped in `config.yaml`:

* `VOCAL_LEAD.wav`, `BASS.wav`, `KICK.wav`, etc.
* OR: configure aliases in `tracks.roles` section

---

# 1) System Overview

## 1.1 Inputs

* Ableton Live Set(s) containing standardized stem/group tracks.
* Exported stem WAVs (MVP: manual export from Live).
* Optional reference mixes (WAV) to build `profile.json`.

## 1.2 Outputs

* `model_cache.json`: scanned track/device/parameter map from Live.
* `report.json`: per-song violations + measurements + applied moves + pass/fail status.
* `actions.json`: deterministic "engineer moves" plan (what will be set in Live).
* `timeline.json`: minimal passive artifact for future features (tempo, length, optional markers).
* Final masters (rendered from Live), plus optional processed stems.

## 1.3 Planes

### Control Plane (Python → Live) via **AbletonOSC**

AbletonOSC is a Live control-surface script. It:

* listens on **OSC port 11000**
* replies on **OSC port 11001**
* supports wildcard queries like `/live/clip/get/* 0 0`
  ([GitHub][1])

Key APIs you will use:

* Track list: `/live/song/get/track_names` ([GitHub][1])
* Track devices: `/live/track/get/devices/name <track_id>` ([GitHub][1])
* Device params (bulk): `/live/device/get/parameters/name|min|max|value` ([GitHub][1])
* Set param (single): `/live/device/set/parameter/value <track_id> <device_id> <param_id> <value>` ([GitHub][1])

Installation and enabling in Live:

* Copy AbletonOSC into User Library `Remote Scripts`
* In Live Preferences → **Link/Tempo/MIDI**, select **Control Surface = AbletonOSC**
* Live should show "Listening for OSC on port 11000"
  ([GitHub][1])

### Analysis Plane (Audio → Python)

MVP reads **offline rendered WAVs** and computes:

* peak / true-peak estimate (oversampling)
* integrated loudness (LUFS)
* band energies over time (STFT)
* detectors: rumble, mud, harshness, sibilance, clipping, stereo correlation, reverb tail

---

# 2) Ableton Standardization Contract (required)

## 2.1 Track naming (minimum)

Required stem/group tracks (names must match exactly or be mapped in config):

* `VOCAL_LEAD`
* `VOCAL_BG` (or merged into VOCAL)
* `KICK`
* `DRUMS`
* `BASS`
* `MUSIC`
* `FX`
* Optional: `REVERB_RETURN`
* Master chain track name (recommended): `ALBUM_MASTER` (or use Master track)

## 2.2 Device order per controlled track (deterministic routing)

For every controlled stem/group track:

* **Device 0**: `Utility` (gain trim / mono-bass)
* **Device 1**: `EQ Eight` (corrective EQ)
* **Device 2** (optional): `Compressor` or `Glue Compressor`

Master:

* limiter device present; ceiling set by automation (no "louder" chasing).

## 2.3 Non-goals enforced

* No new devices.
* No changing creative FX tone.
* No "boosting to taste". (MVP: **no boosts**; only cuts + gain trim.)

---

# 3) Targets and Guardrails (defaults)

## 3.1 Master targets

* Integrated loudness: **-10.5 LUFS**
* True-peak ceiling: **-1.0 dBFS**
* Mono below: **120 Hz**

## 3.2 Stem headroom targets (pre-master)

* Any stem/group peak ≤ **-6 dBFS**

## 3.3 Corrective action clamps

* Utility gain move: ±6 dB max per iteration
* EQ moves per stem: max 2
* EQ cut depth: 1–3 dB (mud), 1–2 dB (harsh/sibilance)
* No EQ boosts in MVP
* Stop after max 2 iterations

---

# 4) Repository Layout (Cursor should generate this)

```
finishline_audio/
  README.md
  requirements.txt
  config.yaml
  src/
    cli.py
    config.py
    log.py

    osc/
      rpc.py
      types.py

    ableton/
      api.py
      scan.py
      cache.py
      find.py
      apply.py
      devices/
        utility.py
        eq8.py
        limiter.py
        compressor.py

    analysis/
      io.py
      windows.py
      loudness.py
      true_peak.py
      stft.py
      bands.py
      detectors.py
      features.py

    rules/
      schema.py
      ruleset.py
      engine.py
      profile.py

    jobs/
      polish_song.py
      polish_album.py

  data/
    profiles/
    caches/
    reports/
    actions/
  input/
    <SongName>/
      stems/
        *.wav
      refs/ (optional)
  output/
    <SongName>/
```

---

# 5) Dependencies

`requirements.txt` (MVP + accurate loudness):

* `python-osc` (OSC client/server) ([python-osc.readthedocs.io][2])
* `numpy`
* `scipy`
* `soundfile`
* `pyloudnorm` (EBU-R128 LUFS; simplest accurate path)
* `pyyaml`

Optional later:

* `fastapi`, `uvicorn` (UI)
* `librosa` (not required)

---

# 6) Configuration (`config.yaml`)

```yaml
ableton:
  host: "127.0.0.1"
  port_in: 11000      # AbletonOSC listens here
  port_out: 11001     # AbletonOSC replies here
  timeout_s: 1.0
  retries: 2

project:
  sample_rate: 48000
  stems_root: "./input"
  output_root: "./output"
  cache_root: "./data/caches"
  reports_root: "./data/reports"
  actions_root: "./data/actions"

tracks:
  # filename matching OR track-name matching rules
  roles:
    VOCAL_LEAD: ["VOCAL_LEAD", "VOCAL"]
    VOCAL_BG: ["VOCAL_BG"]
    KICK: ["KICK"]
    DRUMS: ["DRUMS"]
    BASS: ["BASS"]
    MUSIC: ["MUSIC"]
    FX: ["FX"]
    REVERB_RETURN: ["REVERB_RETURN", "REVERB"]
  master_name_candidates: ["ALBUM_MASTER", "MASTER"]

devices:
  utility_name: "Utility"
  eq8_name: "EQ Eight"
  limiter_name_candidates: ["Limiter", "Limiter (Master)"]
  compressor_name_candidates: ["Compressor", "Glue Compressor"]

targets:
  master_lufs_i: -10.5
  master_true_peak_db: -1.0
  stem_peak_db: -6.0
  mono_below_hz: 120

rules:
  max_iterations: 2
  max_eq_moves_per_track: 2
  allow_boosts: false
  max_total_db_cut_per_track: 4.0  # action budget: max total EQ cut depth per track per iteration
  report_only_for_mild: true  # if severity < 0.5, report but don't apply action
  
# Per-detector confidence thresholds (not one-size-fits-all)
confidence_thresholds:
  rumble: 0.8  # high confidence required (distinguish from bass)
  mud: 0.7     # medium confidence
  harsh: 0.7   # medium confidence
  sibilance: 0.75  # higher confidence (distinguish from intentional brightness)
  headroom: 0.9    # very high confidence (peak measurement is reliable)
  stereo: 0.6      # lower confidence (correlation can vary intentionally)
  reverb_tail: 0.7 # medium confidence

# Severity thresholds (when to act)
severity_thresholds:
  mild: 0.3     # report-only if enabled
  medium: 0.5   # apply conservative correction
  severe: 0.7   # apply full correction (within clamps)

debug:
  verbose_osc: false
  verify_after_set: true
  log_detections: true

analysis:
  stft_window_size: 4096  # for 48kHz
  stft_hop_size: 1024
  oversample_factor: 4    # for true-peak estimate
  silence_threshold_db: -50.0  # activity mask threshold

thresholds:
  rumble:
    non_bass_cutoff_hz: 90
    low_band_ratio_max: 0.12  # energy(20-90)/energy(90-2000)
  mud:
    band_hz: [250, 500]
    ratio_max: 0.18
  harsh:
    band_hz: [2500, 5000]
    burst_db_over_median: 6.0
  sibilance:
    band_hz: [5000, 8000]
    burst_db_over_median: 7.0
  stereo:
    correlation_min: 0.0
  reverb_tail:
    tail_seconds_max: 2.5
    tail_threshold_db: -35.0
```

---

# 7) OSC Transport Layer (reliable request/response)

## 7.1 Requirements

* Send UDP OSC messages to AbletonOSC (11000)
* Receive replies on local UDP port 11001 ([GitHub][1])
* Provide a blocking `call()` that waits for expected reply

## 7.2 Implementation (`src/osc/rpc.py`)

Key design:

* Start an OSC server (thread) listening on `port_out`
* Dispatcher routes all addresses to a single handler
* Handler pushes `(address, args)` into a thread-safe queue
* `call()` sends message then waits for matching response address (and optionally leading indices)

Skeleton:

```python
# src/osc/rpc.py
from __future__ import annotations
import threading, time
from dataclasses import dataclass
from queue import Queue, Empty
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

@dataclass(frozen=True)
class OscConfig:
    host: str
    port_in: int
    port_out: int
    timeout_s: float = 1.0
    retries: int = 2

class OscRpc:
    def __init__(self, cfg: OscConfig):
        self.cfg = cfg
        self.client = udp_client.SimpleUDPClient(cfg.host, cfg.port_in)
        self.q: "Queue[tuple[str, tuple]]" = Queue()
        self._server = None
        self._thread = None

    def start(self):
        disp = Dispatcher()
        disp.set_default_handler(self._on_msg)
        self._server = ThreadingOSCUDPServer(("0.0.0.0", self.cfg.port_out), disp)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()

    def _on_msg(self, address, *args):
        self.q.put((address, args))

    def call(self, address: str, *args, expect: str | None = None) -> tuple:
        expect_addr = expect or address
        last_err = None
        for _ in range(self.cfg.retries + 1):
            self.client.send_message(address, list(args))
            t0 = time.time()
            while time.time() - t0 < self.cfg.timeout_s:
                try:
                    addr, a = self.q.get(timeout=0.05)
                except Empty:
                    continue
                if addr == expect_addr:
                    return a
            last_err = TimeoutError(f"OSC timeout: {expect_addr}")
        raise last_err
```

Acceptance test call:

* send `/live/test` → expect reply `/live/test` with `ok` ([GitHub][1])

---

# 8) AbletonOSC API Wrapper Layer

## 8.1 Wrapper goals

* Hide OSC addresses behind typed functions
* Provide caching and search-by-name
* Provide safe setters with clamps

## 8.2 Core endpoints used (stable)

* `/live/song/get/track_names` ([GitHub][1])
* `/live/track/get/num_devices <track_id>` and `/live/track/get/devices/name <track_id>` ([GitHub][1])
* `/live/device/get/parameters/name|min|max|value <track_id> <device_id>` ([GitHub][1])
* `/live/device/set/parameter/value <track_id> <device_id> <param_id> <value>` ([GitHub][1])

## 8.3 Data model (`src/ableton/cache.py`)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ParamSpec:
    idx: int
    name: str
    min: float
    max: float
    value: float
    is_quantized: bool

@dataclass
class DeviceSpec:
    idx: int
    name: str
    class_name: str | None
    type: int | None
    params: List[ParamSpec]

@dataclass
class TrackSpec:
    idx: int
    name: str
    devices: List[DeviceSpec]

@dataclass
class LiveModel:
    tracks: List[TrackSpec]
    version: str | None
    fingerprint: str  # hash of (track_names + device_counts) for cache invalidation
    timestamp: float  # when this scan was performed
```

## 8.5 Cache Validation & Fingerprinting

Before applying actions, validate cache is still current:

1. Compute fingerprint: `hash((track_names, [len(t.devices) for t in tracks]))`
2. Compare to cached fingerprint
3. If mismatch: refuse to apply, force rescan with error message

This prevents applying actions to a modified set where indices have changed.

## 8.4 Scanner (`src/ableton/scan.py`)

Algorithm:

1. `track_names = /live/song/get/track_names`
2. For each `track_id`:

   * `device_names = /live/track/get/devices/name track_id`
   * For each `device_id`:

     * bulk fetch: param names/min/max/value/is_quantized using `/live/device/get/parameters/*` ([GitHub][1])
3. Save `LiveModel` → `data/caches/<setname>_model_cache.json`

---

# 9) Device Adapters (Utility / EQ Eight / Limiter / Compressor)

## 9.1 Problem: parameter indices vary

Solution:

* Find parameters by **name matching** (regex / candidates).
* Cache the resulting param indices for this set.

## 9.2 Utility adapter (`src/ableton/devices/utility.py`)

Needs:

* `Gain` param (dB)
* `Bass Mono` param (on/off)
* Optional: `Width`

Implementation:

* Find param index where name matches candidates: `["Gain", "Gain (dB)", "Output"]`
* Use fuzzy matching (case-insensitive, partial match)

Parameter conversion layer (CRITICAL):

```python
class UtilityAdapter:
    def set_gain_db(self, db: float):
        """Set gain in dB (musical units), not raw param value."""
        # Clamp to safe range
        db = max(-35.0, min(35.0, db))
        # Convert dB to Ableton's normalized param range
        raw = self._db_to_raw(db)
        self.rpc.set_param(self.track_id, self.device_id, self.gain_param_id, raw)
    
    def _db_to_raw(self, db: float) -> float:
        # Utility gain: param range is typically 0.0-1.0 mapped to -inf to +35dB
        # Verify exact mapping by scanning a test device
        # Example mapping (verify!): 0.85 ≈ 0dB, 0.0 = -inf, 1.0 = +35dB
        return (db + 35.0) / 70.0  # placeholder, verify actual mapping
```

**Do not expose raw param setters to rule engine. Only expose musical units (dB, Hz, etc.).**

## 9.3 EQ Eight adapter (`src/ableton/devices/eq8.py`)

Strategy:

* Use band 1 or band 2 as "correction band" slots.
* Identify params by common names (examples; verify per set by scan):

  * `"1 Frequency"`, `"1 Gain"`, `"1 Q"`, `"1 On"`, `"1 Filter Type"`
* Expose a function `set_peaking_cut(band, freq_hz, q, gain_db)`.

MVP simplification:

* Use 2 bands maximum, both peaking (or one HPF + one peaking cut if you implement rumble via EQ).
* For rumble: either set EQ HPF if you can map filter type; if not, use a dedicated Auto Filter in chain (avoid if possible).

## 9.4 Limiter adapter (`src/ableton/devices/limiter.py`)

* Find `"Ceiling"` param candidate, set to -1.0 dB.

## 9.5 Compressor adapter (`src/ableton/devices/compressor.py`) (optional MVP)

Only if:

* stem crest factor is extreme AND inconsistent AND you already have the device inserted.
  Minimal move:
* small threshold shift (e.g. -1 to -3 dB)
  Avoid:
* ratio/time changes unless required.

---

# 10) Audio Analysis

## 10.1 IO (`src/analysis/io.py`)

* Read WAV with `soundfile.read`
* Convert to float32
* Preserve stereo

## 10.1.5 Activity Detection with Hysteresis (`src/analysis/activity.py`)

Before running detectors, compute "active audio" mask to prevent silence from breaking ratio-based metrics.

**Use hysteresis to prevent flutter around threshold:**

```python
def compute_activity_mask(
    audio: np.ndarray, 
    sr: int, 
    enter_threshold_db: float = -50.0,
    exit_threshold_db: float = -55.0,
    min_duration_sec: float = 0.2
) -> np.ndarray:
    """
    Returns boolean mask where True = active audio, False = silence.
    Uses hysteresis to prevent flutter.
    
    Args:
        audio: stereo or mono float32 audio
        sr: sample rate
        enter_threshold_db: RMS level to enter "active" state
        exit_threshold_db: RMS level to exit "active" state (must be < enter)
        min_duration_sec: minimum duration to stay in state (prevents rapid toggling)
    
    Returns:
        mask: boolean array, one value per frame (e.g. 50ms frames)
    """
    frame_size = int(0.05 * sr)  # 50ms frames
    hop = frame_size // 2
    min_frames = int(min_duration_sec / (hop / sr))
    
    # Compute RMS per frame
    frames = librosa.util.frame(audio, frame_length=frame_size, hop_length=hop)
    rms = np.sqrt(np.mean(frames ** 2, axis=0))
    rms_db = 20 * np.log10(rms + 1e-10)
    
    # Hysteresis state machine
    mask = np.zeros(len(rms_db), dtype=bool)
    is_active = False
    state_duration = 0
    
    for i, level_db in enumerate(rms_db):
        if not is_active:
            # Inactive → check if we should enter active
            if level_db > enter_threshold_db:
                is_active = True
                state_duration = 0
        else:
            # Active → check if we should exit
            if level_db < exit_threshold_db and state_duration >= min_frames:
                is_active = False
                state_duration = 0
        
        mask[i] = is_active
        state_duration += 1
    
    return mask
```

**All detectors must respect this mask and ignore frames where `mask == False`.**

## 10.2 True-peak estimate (`src/analysis/true_peak.py`)

* Oversample by 4× (or 8×) using `scipy.signal.resample_poly`
* Peak = max(abs(oversampled))
* dBFS = `20 * log10(peak + eps)`

**CRITICAL LABELING:** In all reports and outputs, this must be labeled as:
* `true_peak_estimate_db` (not just "true_peak")
* Include note: "4x oversample estimate, not ITU-R BS.1770-4 compliant"

This prevents false security and future confusion.

## 10.3 LUFS integrated (`src/analysis/loudness.py`)

* Use `pyloudnorm.Meter(sr)` and `integrated_loudness(audio)` (audio as float, shape: [n] mono or [n,2] stereo)
* For stems, you can compute LUFS too, but the main target is master.

## 10.3.5 Crest Factor (dynamics protection)

Compute crest factor to prevent over-optimization of intentionally dynamic material:

```python
def compute_crest_factor(audio: np.ndarray, sr: int) -> float:
    """
    Crest factor = peak_db - rms_db
    High crest factor (>12 dB) = very dynamic (preserve)
    Low crest factor (<6 dB) = already compressed/limited (be careful)
    """
    peak_db = 20 * np.log10(np.max(np.abs(audio)) + 1e-10)
    rms_db = 20 * np.log10(np.sqrt(np.mean(audio ** 2)) + 1e-10)
    return peak_db - rms_db
```

**Guardrail:** If `crest_factor_db < 6.0`:
* Disable compressor threshold adjustments
* Reduce harshness/sibilance burst detection sensitivity (multiply threshold by 1.5x)
* Report: "Material already compressed, limiting corrective actions"

This prevents the system from "optimizing" intentionally loud/dense sound design into flatness.

## 10.4 STFT band energy (`src/analysis/stft.py`, `bands.py`)

* STFT with Hann window (e.g. 2048–8192 depending SR)
* Convert magnitude to power
* Sum power per band per frame
* Convert to dB
* Compute:

  * median band level
  * 95th percentile band level
  * burst detection: (short-window band dB) – (median band dB)

Band definitions (Hz):

* Sub 20–80
* Low 80–120
* Low-mid 120–250
* Mud 250–500
* Mid 500–1k
* Presence 1–2.5k
* Harsh 2.5–5k
* Sibilance 5–8k
* Air 8–12k
* Top 12–18k

## 10.5 Detectors (`src/analysis/detectors.py`)

Each detector returns a standardized `Detection` object:

```python
@dataclass
class Detection:
    violation_id: str  # unique ID: "mud_vocal_lead_001"
    violation: bool
    severity: float  # 0.0-1.0 scaled
    confidence: float  # 0.0-1.0 (how certain is this detection?)
    role_required: List[str]  # ["VOCAL_LEAD", "VOCAL_BG"] - which roles this applies to
    evidence: dict  # metrics that triggered it (ratios, burst counts, etc.)
    recommended_action_candidates: List[dict]  # NOT actions, just suggestions
    track_role: str  # actual role of analyzed track
    persistence_key: str  # for tracking "same violation": f"{detector_type}_{track}_{band}_{freq_approx}"
```

**Persistence key format:**
* Headroom: `"headroom_{track_name}"`
* Mud: `"mud_{track_name}_{freq_bin_center}"`
* Harsh: `"harsh_{track_name}_{freq_bin_center}"`
* Sibilance: `"sibilance_{track_name}_{freq_bin_center}"`

Used to detect "same violation persists" across iterations. If `persistence_key` appears in violation history 2+ times with no improvement, mark unfixable.

**Standardized output schema ensures:**
* Consistent rule engine input
* Easy debugging (violation_id traces through logs)
* Clear separation: detectors suggest, rules decide

**Confidence scoring is critical** - detectors should express uncertainty:
* High confidence (>0.8): clear violation, safe to correct
* Medium confidence (0.5-0.8): borderline, apply conservative correction
* Low confidence (<0.5): uncertain, report-only

Examples of confidence factors:
* Mud detection in sparse arrangement: lower confidence
* Harsh detection on intentional distortion: lower confidence (check crest factor)
* Rumble in non-bass material with clear sub energy: higher confidence
* Sibilance in low crest-factor vocal: lower confidence (might be intentional compression)

Detectors:

### Rumble (non-bass material)

* Compute ratio: `E(20–cutoff)/E(cutoff–2000)`
* If ratio > threshold → suggest HPF or low cut action.

### Mud

* Ratio: `E(250–500)/E(90–2000)` or relative to profile p75
* If high → suggest peaking cut near max-energy bin in 250–500.

### Harshness

* Find frames where `harsh_band_db - median_harsh_db > burst_threshold_db`
* If too frequent → suggest narrow cut at dominant frequency.

### Sibilance (vocals)

* Same as harsh but band 5–8k and higher burst threshold.

### Clipping / headroom

* Stem peak > -6 dBFS → suggest Utility gain trim.

### Stereo/phase (master)

* correlation = corrcoef(L, R)
* if corr < min → flag (MVP: report + optional width/mono-bass only)

### Reverb tail (return stem)

* Identify end-of-file region, compute RMS decay time until below threshold
* if decay too long → suggest lowering return gain

---

# 11) Rule Engine (deterministic actions)

## 11.1 Action schema (`src/rules/schema.py`)

```python
from dataclasses import dataclass
from typing import Literal, Optional

ActionType = Literal[
  "utility_gain_db",
  "eq_peaking_cut",
  "master_limiter_ceiling_db",
  "master_mono_below_hz",
  "reverb_return_gain_db"
]

@dataclass
class Action:
    track_name: str
    type: ActionType
    value_db: Optional[float] = None
    freq_hz: Optional[float] = None
    q: Optional[float] = None
    band_slot: Optional[int] = None
    note: str = ""
```

## 11.2 Rules (`src/rules/ruleset.py`)

Each rule specifies:
* **Detector type** (rumble, mud, harsh, sibilance, etc.)
* **Required track roles** (e.g. `["VOCAL_LEAD", "VOCAL_BG"]`)
* **Confidence minimum** (e.g. 0.7)
* **Severity minimum** (e.g. 0.3)

```python
@dataclass
class Rule:
    name: str
    detector_type: str
    required_roles: List[str]
    confidence_min: float = 0.7
    severity_min: float = 0.3
    max_cut_db: float = 3.0
```

Rule fires ONLY if:
* Track role matches `required_roles`
* `Detection.confidence >= confidence_min`
* `Detection.severity >= severity_min`

Rule order (per stem):

1. **Headroom** (Utility gain to hit peak target) - all roles
2. **Rumble** (HPF or low cut) - roles: `["VOCAL", "DRUMS", "MUSIC", "FX"]` (NOT BASS)
3. **Mud** (1 cut) - roles: `["VOCAL", "MUSIC"]`
4. **Harsh/sibilance** (1 cut) - roles: `["VOCAL"]` for sibilance, `["VOCAL", "DRUMS"]` for harsh

Master rules:

1. limiter ceiling -1.0 dB
2. mono below 120 Hz (Utility on master if present; otherwise report)

Clamp:

* total EQ cuts max 2 per stem
* never boost
* per-cut depth depends on severity bucket:

  * mild (0.3-0.5): -1 dB
  * medium (0.5-0.7): -2 dB
  * severe (0.7-1.0): -3 dB (mud only)

## 11.2.5 Stop Conditions

Iteration loop stops when ANY of:
* Max iterations reached (2)
* No violations above severity threshold remain
* Next action would exceed clamps
* **Same violation persists after 2 attempts** → mark "unfixable", report-only, do not retry

Track violation history to detect persistence.

## 11.3 Produce `actions.json` with Versioning

Structure:

```json
{
  "song": "SongName",
  "iteration": 1,
  "policy_version": "0.1-mvp",
  "ruleset_hash": "sha256:abc123...",
  "analysis_hash": "sha256:def456...",
  "timestamp": "2026-02-22T19:30:00Z",
  "actions": [
    {"track":"VOCAL_LEAD","type":"utility_gain_db","value_db":-2.0},
    {"track":"VOCAL_LEAD","type":"eq_peaking_cut","freq_hz":320,"q":2.0,"value_db":-2.0,"band_slot":1}
  ],
  "action_budget_remaining": {
    "VOCAL_LEAD": {"total_db_cut_used": 2.0, "total_db_cut_budget": 4.0}
  }
}
```

**Hashing:**
* `ruleset_hash`: SHA256 of ruleset code + config thresholds (reproducibility)
* `analysis_hash`: SHA256 of analysis code + activity mask settings (reproducibility)

Allows reproducing exact outcomes later by matching hashes.

---

# 12) Applying Actions to Live (AbletonOSC)

## 12.1 Apply pipeline (`src/ableton/apply.py`)

1. Load `model_cache.json`
2. **Validate cache fingerprint** (see 8.5) - refuse if stale
3. Resolve `track_name` → `track_id`
4. Resolve device indices on that track:

   * Utility = device index where `name == "Utility"`
   * EQ Eight similarly
5. Resolve param indices by name match (cached)
6. Apply actions with **throttling**:

```python
def apply_actions(actions: List[Action]):
    for action in actions:
        apply_single_action(action)
        time.sleep(0.025)  # 25ms throttle between param sets
```

7. **Verify critical parameters** by re-reading after batch apply:

```python
def verify_action(action: Action):
    current_value = read_param(...)
    if abs(current_value - expected_value) > tolerance:
        log_warning(f"Param verification failed: {action}")
```

**Throttling prevents UDP buffer overruns in AbletonOSC. Verification catches failed sets.**

## 12.2 AbletonOSC set/verify calls

* Single param set: `/live/device/set/parameter/value track_id device_id param_id value` ([GitHub][1])
* Bulk read for verify: `/live/device/get/parameters/value track_id device_id` ([GitHub][1])

---

# 13) End-to-End Job Orchestration

## 13.1 `polish_song` job (`src/jobs/polish_song.py`)

Inputs:

* song folder: `input/<SongName>/stems/*.wav`
* optional refs folder

Flow:

1. **Connectivity check**:

   * `/live/test` OK ([GitHub][1])
2. **Scan** (or load cached scan):

   * `model_cache.json`
3. **Validate standardization**:

   * required tracks exist in Live
   * device order exists (Utility=0, EQ=1) on controlled tracks
4. **Analyze stems** → `features.json`
5. **Generate actions** → `actions.json`
6. If `--apply`:

   * Apply actions to Live
7. If `--verify`:

   * re-export stems/premaster manually
   * re-run analysis and check pass/fail criteria (see below)
   * stop if pass OR max iterations reached
8. Emit `report.json` (includes before/after)

### Verification Pass/Fail Criteria

A song passes verification when ALL of:
* **Master LUFS:** within ±0.5 dB of target (-10.5 LUFS default)
* **Master true-peak estimate:** ≤ -1.0 dBFS (with 0.1 dB tolerance)
* **Stem peaks:** all ≤ -6.0 dBFS (with 0.2 dB tolerance)
* **Severe violations:** none remain (severity < 0.7)
* **Unfixable violations:** marked as report-only, not blocking

If fails:
* Log which criteria failed
* If same violations persist → mark unfixable, do not retry
* Report includes "PASS" or "FAIL" status

## 13.2 Album batch (`src/jobs/polish_album.py`)

Loop songs, same flow, same clamp rules.

---

# 14) CLI (what you run)

`src/cli.py` with argparse:

Commands:

* `scan` → writes `model_cache.json`
* `ping` → `/live/test`
* `validate` → checks tracks/devices present
* `analyze --song SongName` → writes report + actions (no apply)
* `apply --song SongName` → applies last actions
* `polish --song SongName --apply --verify` → full loop (verify requires new exports)
* `polish-album --apply` → batch

---

# 15) Reference Profile Mode (optional)

## 15.1 Build profile (`src/rules/profile.py`)

Input: 3 reference WAVs.
Compute:

* master LUFS distribution (median/p25/p75)
* band energies p25/p50/p75 per band

Store to `data/profiles/profile.json`

## 15.2 Use in rules

Instead of fixed `ratio_max`, use:

* "if mud band > ref p75 + margin → cut"
* "if harsh bursts exceed ref p75 burst rate → cut"

---

# 16) Failure Modes (handle explicitly)

* AbletonOSC not installed/enabled → ping fails with clear error message
* Track names mismatch → validation fails (print expected vs found, suggest config aliases)
* Device chain not present → validation fails (print missing device, suggest manual setup)
* Param name mismatch (Live version differences) → adapter raises with list of available param names for that device
* UDP packet loss → RPC retry logic (2 retries, then fail with timeout error)
* Cache fingerprint mismatch → refuse to apply, force rescan
* Export settings violation → cannot detect programmatically (user responsibility, document checklist)
* Silence-heavy audio → activity mask prevents false detections
* Unfixable violations → stop iterating after 2 attempts, mark report-only

---

# 18) Timeline Artifact (future-proofing, minimal implementation)

To support future visual/show-control features without requiring a rewrite, generate a passive `timeline.json` artifact:

```json
{
  "song": "SongName",
  "bpm": 120.0,
  "length_seconds": 240.5,
  "length_bars": 128,
  "time_signature": "4/4",
  "sample_rate": 48000,
  "markers": [
    {"name": "Intro", "time_seconds": 0.0, "bar": 1},
    {"name": "Verse 1", "time_seconds": 16.0, "bar": 17},
    {"name": "Chorus", "time_seconds": 48.0, "bar": 49}
  ]
}
```

**MVP implementation:**
* Extract BPM, length, sample_rate from Live via AbletonOSC (if available)
* Markers: empty array (optional extraction later)
* Store in `data/timelines/<song>_timeline.json`

**No engine, no processing.** Just a data format placeholder so future features (beat-synced visuals, section-aware analysis) can reference it without restructuring.

---

# 19) Known Limitations (MVP)

Document what this system **does not** handle in MVP:

* **True-peak is estimated** (4x oversample), not ITU-R BS.1770-4 compliant
* **Reverb tail detection** requires dedicated `REVERB_RETURN.wav` stem (optional)
* **No cross-song consistency** enforcement (no album median targeting)
* **No section/marker awareness** (full-song analysis only)
* **No creative parameter changes** (FX character, reverb size, distortion, etc. are off-limits)
* **Single loudness target** (no per-song overrides, though profile system can be added later)
* **No undo mechanism** (keep backups of Live sets before running automation)
* **No programmatic export** (manual export required per song)
* **No stem alignment verification** (assumes all stems are same length/start time)

---

# 17) Minimal Acceptance Tests (must pass)

1. **Ping**

   * `/live/test` returns `ok` ([GitHub][1])
2. **Enumerate tracks**

   * `/live/song/get/track_names` returns list ([GitHub][1])
3. **Move a knob**

   * Find `VOCAL_LEAD` track, `Utility`, param `Gain`
   * Set gain by -1 dB and verify it changed via `/live/device/get/parameter/value` ([GitHub][1])
4. **Analyze one stem**

   * Compute peak, LUFS, band energies
5. **Generate actions.json**
6. **Apply actions**
7. **Re-analyze after new export** (verify loop)

---

# Checklist A — Main Events (broad)

1. Install/enable AbletonOSC in Live (ports confirmed). ([GitHub][1])
2. Standardize tracks + device order (Utility then EQ Eight).
3. Create repo + dependencies + config.yaml.
4. Implement OSC RPC client/server (request/response, retries).
5. Implement Ableton scan → model_cache.json.
6. Implement device adapters (Utility, EQ Eight, Limiter).
7. Implement WAV analysis (LUFS, true-peak estimate, STFT band energies).
8. Implement detectors (rumble, mud, harsh, sibilance, clipping, stereo, tails).
9. Implement deterministic rules → actions.json (clamped).
10. Implement apply-to-Live from actions.json + verification reads.
11. Implement polish_song job (iteration loop, max 2).
12. Implement polish_album batch + outputs (reports/actions).
13. Run acceptance tests, then run on one full song, then batch album.

---

# Checklist B — Granular "every step" Implementation

## B1) Live-side setup

1. Download AbletonOSC repo zip and rename folder to `AbletonOSC`. ([GitHub][1])
2. Create `Remote Scripts` folder in Ableton User Library if missing. ([Ableton Help][3])
3. Copy `AbletonOSC` folder into `User Library/Remote Scripts`. ([GitHub][1])
4. Restart Ableton Live. ([GitHub][1])
5. Preferences → Link/Tempo/MIDI → Control Surface dropdown → select **AbletonOSC**. ([GitHub][1])
6. Confirm Live status message indicates listening on **11000**. ([GitHub][1])

## B2) Ableton set standardization

7. Rename group/stem tracks to required names (or match your config role aliases).
8. On each controlled track: insert **Utility** first, **EQ Eight** second.
9. On master or ALBUM_MASTER: ensure a limiter device exists.
10. If using REVERB_RETURN: isolate reverb on its own return track or printed return stem.

## B3) Repo bootstrap

11. Create `finishline_audio/` folder.
12. Add the directory tree exactly as specified.
13. Write `requirements.txt`.
14. Create Python venv, install deps.
15. Write `config.yaml`.

## B4) OSC layer

16. Implement `OscConfig` and `OscRpc` (client + server + queue).
17. Start server on port 11001 (must match AbletonOSC reply port). ([GitHub][1])
18. Implement `ping()` calling `/live/test` and asserting reply contains `ok`. ([GitHub][1])
19. Add retry + timeout.

## B5) Ableton API wrapper

20. Implement `get_track_names()` → `/live/song/get/track_names`. ([GitHub][1])
21. Implement `get_track_devices(track_id)` → `/live/track/get/devices/name`. ([GitHub][1])
22. Implement `get_device_params(track_id, device_id)` bulk calls:

    * `/live/device/get/parameters/name|min|max|value|is_quantized` ([GitHub][1])
23. Implement `set_param(track_id, device_id, param_id, value)` → `/live/device/set/parameter/value`. ([GitHub][1])

## B6) Scanner + cache

24. Build `LiveModel` dataclasses.
25. Scan tracks → devices → params and store in memory.
26. Serialize to JSON in `data/caches/..._model_cache.json`.
27. Add `scan` CLI command.

## B7) Find helpers

28. Implement `find_track_id_by_name(model, candidates)` (exact match, then case-insensitive).
29. Implement `find_device_id_by_name(track, device_name)` (exact match).
30. Implement `find_param_id_by_candidates(device, ["Gain", "Ceiling", ...])`.
31. Add "print available params on failure".

## B8) Device adapters

32. Utility adapter:

    * resolve Gain param id
    * implement `set_gain_db(delta_or_absolute)` with clamp to param min/max
    * resolve Bass Mono param id (if exists) and set on master
33. EQ Eight adapter:

    * resolve per-band param ids using regex matching
    * implement `set_band_cut(band_slot, freq_hz, q, gain_db)`
    * choose band slots 1 and 2 as correction slots (configurable)
34. Limiter adapter:

    * resolve Ceiling param id and set to -1.0 dB

## B9) Audio analysis core

35. Implement WAV load (soundfile).
36. Implement peak (sample peak).
37. Implement true-peak estimate (oversample).
38. Implement LUFS integrated (pyloudnorm).
39. Implement STFT (scipy) and band-power extraction.
40. Compute per-band median and burst stats.

## B10) Detectors

41. Rumble detector (non-bass):

    * compute low-band ratio vs threshold
    * output suggested cutoff + severity
42. Mud detector:

    * locate dominant freq bin in 250–500
    * output suggested freq + depth bucket
43. Harsh detector:

    * compute burst count/frequency
    * output suggested freq + depth bucket
44. Sibilance detector (vocals):

    * same logic, 5–8k
45. Headroom detector:

    * if peak > -6 dBFS, propose Utility trim
46. Stereo/phase detector (master):

    * compute correlation; flag if below threshold
47. Reverb tail detector:

    * decay time above threshold; propose return gain reduction

## B11) Rules + actions

48. Define Action dataclass + JSON serialization.
49. Implement rules in fixed order with clamp logic.
50. Enforce max 2 EQ moves, no boosts.
51. Emit `actions.json`.

## B12) Apply actions to Live

52. Load model_cache.json.
53. Resolve track/device/param ids via adapters.
54. Apply each Action via `/live/device/set/parameter/value`. ([GitHub][1])
55. Optionally re-read param values for verification.

## B13) Reporting

56. Build `report.json` with:

    * measured metrics (before)
    * detected violations
    * actions applied
    * measured metrics (after) if verify export provided

## B14) Polish job + iteration loop

57. `polish_song`:

    * validate Live set
    * analyze stems
    * generate actions
    * apply (if enabled)
    * stop at iteration cap
58. `polish_album`:

    * loop songs directory
    * per-song outputs to dedicated folders

## B15) Final workflow execution

59. For a song: export stems from Live into `input/SongName/stems/`.
60. Run `python -m src.cli scan`.
61. Run `python -m src.cli validate`.
62. Run `python -m src.cli analyze --song SongName`.
63. Run `python -m src.cli apply --song SongName`.
64. Re-export premaster/master from Live.
65. Run `python -m src.cli analyze --song SongName` again to confirm in-range.
66. Repeat for all songs, then export final masters album-wide.

---

If you want Cursor to generate code faster: tell it to implement **only** Utility gain trim + Limiter ceiling + one EQ mud cut first (end-to-end), then add the other detectors after the pipeline works.

[1]: https://github.com/ideoforms/AbletonOSC "GitHub - ideoforms/AbletonOSC: Control Ableton Live via Open Sound Control (OSC)"
[2]: https://python-osc.readthedocs.io/?utm_source=chatgpt.com "Python-osc - OSC server and client in pure python — python ..."
[3]: https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts?utm_source=chatgpt.com "Installing third-party remote scripts"
