# Measurement Contract

**Status**: PERMANENT (canon)  
**Scope**: Single source of truth for audio measurement

---

## Contract

**Input**: WAV file (any sample rate, any duration)

**Output**: Three measurements
1. **LUFS-I** (Integrated Loudness, ITU-R BS.1770)
2. **Sample Peak** (dBFS, highest sample value)
3. **True Peak** (dBTP, oversampled inter-sample peak)

**Validation requirement**: True peak must be validated against reference meter within ±0.5 dB tolerance

---

## Implementation

**File**: `src/flaas/analyze.py`

**Function**: `analyze_wav(path) -> AnalysisResult`

**Algorithm**:
```
1. Read WAV → mono float
2. LUFS-I via pyloudnorm.Meter.integrated_loudness()
3. Sample peak via np.max(np.abs(mono))
4. True peak via 4x oversampling (scipy.signal.resample)
   ⚠️ APPROXIMATION - needs ITU-R BS.1770-4 validation
5. Return AnalysisResult dataclass
```

**Units**:
- LUFS-I: Loudness Units Full Scale (relative to full scale)
- Sample Peak: dBFS (decibels relative to full scale)
- True Peak: dBTP (decibels true peak, oversampled)

---

## Why These Three

**LUFS-I** (Perceptual Loudness):
- Frequency-weighted (K-weighting, models human hearing)
- Gated (ignores silence/quiet passages)
- Industry standard (Spotify, Apple Music, broadcast)
- **Decision signal**: Primary optimization target

**Sample Peak** (Digital Clipping Guard):
- Measures highest sample value
- Prevents 0 dBFS overflow
- Quick sanity check
- **Limitation**: Misses inter-sample peaks

**True Peak** (Codec Safety Guard):
- Measures oversampled peak (4x, detects inter-sample)
- Prevents codec clipping (MP3, AAC, Ogg)
- Streaming services check this
- **Safety constraint**: Must stay under limit

---

## Validation

**Test script**: `tests/validate_true_peak.py`

**Methodology**:
1. Generate sine waves at known levels:
   - 1 kHz at 0 dB → expect TP ≈ 0.0 dBTP
   - 1 kHz at -6 dB → expect TP ≈ -6.0 dBTP
   - 1 kHz at -12 dB → expect TP ≈ -12.0 dBTP

2. Measure with `flaas verify-audio`

3. Compare against reference meter:
   - **Youlean Loudness Meter** (free, accurate, broadcast-grade)
   - **ffmpeg**: `ffmpeg -i file.wav -filter:a ebur128=peak=true -f null -`
   - Any broadcast-grade meter

4. Accept if within ±0.5 dB tolerance

**Status**: ⚠️ PENDING (approximation functional, validation not run)

---

## Decision Logic

**Optimization uses**:
- **Target**: LUFS-I (perceptual loudness)
- **Constraint**: True peak ≤ limit (safety)

**Convergence**:
```python
converged = (
    abs(lufs_i - target_lufs) <= 0.5  # Within 0.5 LU
    AND true_peak_dbtp <= limit        # Peak safe
)
```

**Best result selection** (if convergence not achieved):
```python
best = min(results, key=lambda r: (
    not r.true_peak_safe,     # Priority 1: Peak safety
    abs(r.lufs_i - target)    # Priority 2: Closest to target
))
```

---

## Non-Negotiable Rules

1. **Always measure all three** (LUFS, sample peak, true peak)
2. **No shortcuts**: Read actual audio, don't trust metadata
3. **No stale data**: Re-measure after every export (no caching)
4. **No guessing**: If file missing or measurement fails, abort (don't assume)
5. **Log everything**: Every measurement goes to JSONL (timestamp, sha256, metrics)

---

## Measurement is Cheap

**Typical duration**: < 1 second for 10-second WAV

**Never skip**: Even for debugging, always measure (it's fast and prevents silent bugs)

---

## What's NOT Canon (Tuneable)

**Not permanent**:
- Exact convergence tolerance (0.5 LU is tuneable)
- True peak limit (mode-dependent: -1 vs -2 vs -6)
- Target LUFS (mode-dependent: -14 vs -9 vs -10)

**These vary by**: Mode, genre, user preference

---

**This measurement contract is permanent. All audio decisions flow from these three numbers.**
