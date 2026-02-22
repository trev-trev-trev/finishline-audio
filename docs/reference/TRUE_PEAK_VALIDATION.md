# True Peak Validation Status

**Date**: 2026-02-22  
**Status**: ⚠️ APPROXIMATION (needs validation)

---

## Current Implementation

**File**: `src/flaas/analyze.py`

**Method**: 4x oversampling via `scipy.signal.resample`

**Code**:
```python
from scipy import signal
oversampled = signal.resample(mono, len(mono) * 4)
true_peak = float(np.max(np.abs(oversampled)))
true_peak_dbtp = 20.0 * np.log10(true_peak)
```

**Status**: This is an APPROXIMATION, not a full ITU-R BS.1770-4 implementation.

---

## ITU-R BS.1770-4 Specification

**Official true peak algorithm**:
1. **4x oversampling** (192 kHz for 48 kHz source)
2. **Proper lowpass filter** (anti-aliasing)
3. **Inter-sample peak detection** (finds peaks between samples)
4. **Output**: True peak level in dBTP (decibels relative to full scale)

**Why it matters**:
- Codec conversion (MP3, AAC) can introduce inter-sample peaks
- Even if sample peak is safe (-6 dBFS), true peak may clip (e.g., -4.5 dBTP)
- Streaming services require true peak compliance to avoid distortion

---

## Validation Needed

**Test script**: `tests/validate_true_peak.py`

**Methodology**:
1. Generate known test signals (1 kHz sine at 0 dB, -6 dB, -12 dB)
2. Measure with our implementation (`flaas verify-audio`)
3. Measure same files with reference meter:
   - **Youlean Loudness Meter** (free, accurate, broadcast-grade)
   - **ffmpeg**: `ffmpeg -i <file> -filter:a ebur128=peak=true -f null -`
   - Any broadcast-grade meter
4. Compare results
5. **Tolerance**: ±0.5 dB acceptable

**Expected results**:
- `sine_1khz_full_scale.wav`: TP ≈ 0.0 dBTP
- `sine_1khz_minus6db.wav`: TP ≈ -6.0 dBTP
- `sine_1khz_minus12db.wav`: TP ≈ -12.0 dBTP

**Run validation**:
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
python tests/validate_true_peak.py

# Then measure each file with reference meter
# Compare against flaas verify-audio output
```

---

## If Validation Fails

**Option 1: Use ffmpeg subprocess** (most reliable):
```python
import subprocess
import json

def get_true_peak_ffmpeg(path: str) -> float:
    cmd = [
        'ffmpeg', '-i', path,
        '-filter:a', 'ebur128=peak=true:framelog=quiet',
        '-f', 'null', '-'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Parse stderr for "True peak: X.XX dBTP"
    # (requires parsing ffmpeg output)
```

**Option 2: Use pyebur128** (requires API fix):
- Library exists but API is unclear
- Would need proper integration

**Option 3: Implement proper ITU-R algorithm**:
- 4x oversample with proper FIR lowpass filter
- Use SciPy or custom filter
- Follow spec exactly

---

## Current Risk Assessment

**Risk**: Medium

**Mitigation**:
- Our approximation likely within 0.5-1.0 dB of true value
- Conservative true peak limits (-2 dBTP for loud_preview) provide buffer
- Sample peak is still measured (catches most issues)
- Validation script exists for future testing

**Action required**: Run validation test when reference meter is available.

---

**Status**: Functional approximation, validation pending.
