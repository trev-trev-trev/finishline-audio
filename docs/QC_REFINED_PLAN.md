# QC & Loudness Plan (Refined)

**Refined**: 2026-02-23  
**Based on**: ChatGPT feedback + internal review

---

## Agree (ChatGPT Feedback)

| Point | Verdict |
|-------|---------|
| **-1.08 dBTP** is a good safety ceiling | ✅ Agree |
| **-16.32 LUFS** is accurately "conservative" | ✅ Agree |
| **PERFECT_MASTER (-0.38 dBTP)** is risky | ✅ Agree |

---

## Disagree / Clarify (ChatGPT Feedback)

### 1. "Apple Music -16 LUFS standard"

**ChatGPT**: Apple doesn't require a delivery LUFS; that's playback normalization, not a mastering spec.

**Verdict**: ✅ **Agree with ChatGPT**

- Apple Music accepts masters at any loudness
- -16 LUFS is their *playback* normalization target, not a delivery requirement
- We should stop saying "Apple Music perfect match" — it's misleading
- **Correction**: Say "within Apple Music playback normalization range" or "conservative delivery"

---

### 2. "Too quiet for Spotify/YouTube"

**ChatGPT**: Those "optimal ranges" are not requirements; they're playback targets that vary by user settings/mode.

**Verdict**: ✅ **Agree with ChatGPT**

- Spotify/YouTube don't *reject* quiet masters
- They normalize on playback; user can disable normalization
- "Too quiet" implies non-compliance — we should say "quieter than typical commercial releases" or "conservative"

---

### 3. "Normalize up automatically = safe"

**ChatGPT**: If Spotify/YouTube turn it up ~+2.3 dB, true peak would become roughly +1.2 dBTP (unsafe) unless they apply limiting.

**Verdict**: ✅ **Agree with ChatGPT — Critical correction**

- **Math**: -16.32 LUFS + 2.32 dB gain → -14 LUFS. True peak: -1.08 + 2.32 = **+1.24 dBTP** (clipping)
- Platforms *do* apply limiting when normalizing, but we cannot assume it
- **"Safe" at delivery does NOT guarantee safe after normalization**
- We must add: **"If gain-matched to -14 LUFS, projected true peak = X dBTP"** to all reports

---

### 4. "Missing the biggest red flag"

**ChatGPT**: Optimizer target was -9 LUFS (loud_preview). Export at -16.3 LUFS suggests loop/export behavior or measurement is wrong.

**Verdict**: ⚠️ **Partially agree — Context matters**

- **iter2 was from `streaming_safe` mode**, not loud_preview (see `stand_tall_premium_streaming_safe.jsonl`)
- streaming_safe target: **-14 LUFS**
- iter2 achieved: **-16.32 LUFS** → **2.32 LU below target**
- **Red flag stands**: Optimizer is failing to reach -14 LUFS; stuck at ~-16.3 LUFS
- Possible causes:
  - Plugin chain not responding as expected
  - L3 limiter ceiling too conservative
  - Measurement is correct (full 4.7 min) — optimizer logic may be wrong
- **Action**: Add target-vs-actual comparison to QC report

---

## Refined Plan: Additions

### 1. Short-term LUFS (3s) + Momentary LUFS (400ms)

**Purpose**: Detect sections that spike or dip; integrated LUFS can hide problems.

**Implementation**:
- Use `pyebur128` (already in requirements): `get_loudness_shortterm`, `get_loudness_momentary`
- Report: min/max/mean short-term, min/max momentary across sections

**Deliverable**: Section-by-section breakdown (e.g., verse/chorus if detectable, or time-based windows)

---

### 2. LRA + Crest Factor + Band Ratios

**Purpose**: Correlate with "smooth" vs "harsh" perception.

**Metrics**:
- **LRA** (Loudness Range): `pyloudnorm.Meter.loudness_range()` or pyebur128
- **Crest factor**: peak_RMS / RMS (dynamic range indicator)
- **Band ratios** (optional): low/mid/high energy balance (harshness vs mud)

**Deliverable**: LRA, crest factor in QC report

---

### 3. Gain-Match Simulation

**Purpose**: Answer "if we gain-match to -14 or -9, what does true peak become?"

**Formula**:
```
gain_db = target_lufs - actual_lufs_i
projected_true_peak_dbtp = actual_true_peak_dbtp + gain_db
```

**Example** (iter2):
- Actual: -16.32 LUFS, -1.08 dBTP
- If gain to -14 LUFS: +2.32 dB → projected true peak = **+1.24 dBTP** ❌
- If gain to -9 LUFS: +7.32 dB → projected true peak = **+6.24 dBTP** ❌
- **Conclusion**: Safe at delivery; would clip if normalized without limiting

**Deliverable**: Table in QC report:
| Target LUFS | Gain (dB) | Projected True Peak dBTP | Safe? |
|-------------|------------|--------------------------|-------|
| -14 | +2.32 | +1.24 | ❌ |
| -9 | +7.32 | +6.24 | ❌ |

---

### 4. Explicit Deliverable Types

**Stop mixing narratives.** Decide one of:

| Type | Description | Target |
|------|--------------|--------|
| **Streaming-normalized** | Safe for platform normalization | ~-14 LUFS, ≤ -1 dBTP |
| **Loud master** | Competitive commercial | ~-9 LUFS, ≤ -1 dBTP |

**Action**: Document which type each mode produces; validate that optimizer actually hits it.

---

### 5. Target-vs-Actual Verification

**Add to every QC run**:
- Intended mode + target LUFS
- Actual LUFS
- Delta (actual - target)
- **Pass/fail**: Did we hit target within ±0.5 LU?

**For iter2**:
- Mode: streaming_safe
- Target: -14 LUFS
- Actual: -16.32 LUFS
- Delta: -2.32 LU (too quiet)
- **FAIL**: Optimizer did not reach target

---

## Implementation: qc_compare.py

**Purpose**: Single-file QC that validates numbers align with intended target.

**Features**:
1. Integrated LUFS, True Peak (existing)
2. Short-term LUFS (3s) — min/max/mean
3. Momentary LUFS (400ms) — min/max
4. LRA
5. Crest factor
6. Gain-match simulation (-14, -9 LUFS)
7. Target-vs-actual (if JSONL/mode metadata available)

**Usage**:
```bash
python scripts/qc_compare.py output/stand_tall_premium_iter2.wav
```

**Output**: Structured report with all metrics + pass/fail for target alignment.

---

## Summary of Corrections

| Original Claim | Corrected |
|----------------|-----------|
| "Apple Music perfect match" | "Within Apple playback range; not a delivery requirement" |
| "Too quiet for Spotify" | "Quieter than typical; platforms normalize" |
| "Safe after normalization" | "Safe at delivery; would clip if gain-matched to -14 without limiting" |
| "iter2 from loud_preview" | "iter2 from streaming_safe; target -14, achieved -16.32 (miss)" |
| No gain-match check | Add: "Projected true peak if gain-matched to -14/-9" |
| Integrated only | Add: Short-term, momentary, LRA, crest factor |

---

## Next Steps

1. Implement `qc_compare.py` with all metrics
2. Run on iter2 and verify numbers
3. Update `validate_streaming.py` to include gain-match simulation
4. Fix optimizer to actually reach -14 LUFS in streaming_safe mode (separate task)
5. Document deliverable types in README/CHEATSHEET
