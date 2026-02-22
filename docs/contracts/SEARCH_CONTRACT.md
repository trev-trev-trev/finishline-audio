# Search Contract

**Status**: PERMANENT (canon)  
**Scope**: Optimization algorithm structure and stop conditions

---

## Contract

**Closed-loop optimization**:
```
set params → export → measure → decide → adjust → repeat
```

**Decision signal**: Distance from target LUFS-I (in LU)

**Safety constraint**: True peak ≤ limit (mode-dependent)

**Stop conditions**:
1. **Convergence**: abs(LUFS-I - target) ≤ 0.5 LU AND true peak safe
2. **Max iterations**: 15 (prevents infinite loop)
3. **Diminishing returns**: LUFS improvement < 0.2 LU per iteration AND strategy exhausted

---

## Control Knobs (Master Chain)

**Phase 1: Compression** (Glue Compressor)
- Threshold (dB): Controls gain reduction depth
- Makeup (dB): Output level boost
- Ratio: Compression curve steepness
- Attack (ms): Speed of compression onset

**Phase 2: Saturation** (Saturator, optional but recommended)
- Drive (dB): Soft clip amount (raises RMS efficiently)
- Dry/Wet: Mix (typically 100%)

**Phase 3: Limiting** (Limiter)
- Gain (dB): Input boost before limiting
- Ceiling (dB): Hard peak ceiling (fixed or optimized)

---

## Phase-Based Optimization (Sequential)

**Phase 1: Tune Compression**
- Adjust Glue Threshold to hit target GR band
- Example: For -9 LUFS target, aim for GR 12-15 dB
- Adjust Makeup to compensate output loss
- Keep Limiter gain moderate

**Phase 2: Add Saturation** (if available)
- Increase Saturator Drive to raise RMS
- Monitor true peak (soft clip can increase peak)
- More efficient than extreme compression

**Phase 3: Fine-Tune Limiter**
- Adjust Limiter Gain in small steps (1-2 dB)
- Stop if LUFS improvement < 0.2 LU per iteration
- Prevents distortion from over-limiting

**Why sequential**: Moving all knobs simultaneously creates instability and oscillation

---

## Diminishing Returns Detection

**Rule**: If LUFS improvement < 0.2 LU per iteration, current strategy is exhausted

**Response**:
- **If in limiting phase**: Switch to compression or saturation
- **If in compression phase**: Switch to saturation or accept convergence
- **If all phases exhausted**: Stop and use best result

**Example**:
```
Iteration 5: LUFS -11.2 → Iteration 6: LUFS -11.15 (improvement 0.05 LU)
→ Diminishing returns detected
→ Stop increasing limiter gain
→ Switch to Saturator drive or compression
```

---

## Adaptive Adjustments

**Gap-based step sizes**:
- **Large gap (>3 LU)**: Aggressive adjustment (threshold -5 dB, makeup +2.5 dB, limiter +3 dB)
- **Medium gap (1-3 LU)**: Moderate adjustment (threshold -3 dB, makeup +1.5 dB, limiter +2 dB)
- **Small gap (<1 LU)**: Fine adjustment (threshold -2 dB, makeup +1 dB, limiter +1 dB)

**Peak safety override**:
- If true peak > limit: Immediately reduce limiter gain by 2 dB (takes precedence over LUFS)

**Overshoot correction**:
- If LUFS > target: Raise threshold +2 dB, reduce makeup -1 dB

---

## Stop Conditions

**1. Convergence (ideal)**:
- abs(LUFS-I - target) ≤ 0.5 LU
- true_peak_dbtp ≤ limit
- Status: "converged"

**2. Max iterations (fallback)**:
- Reached 15 iterations
- Use best result (closest to target with safe peak)
- Status: "max_iterations"

**3. Diminishing returns (strategy exhausted)**:
- LUFS improvement < 0.2 LU for 2+ consecutive iterations
- All phases tried (compression, saturation, limiting)
- Status: "diminishing_returns"

---

## Logging (Every Iteration)

**Required fields**:
```json
{
  "iteration": 3,
  "threshold_db": -35.0,
  "makeup_db": 20.0,
  "ratio": 5.0,
  "saturator_drive_db": 5.0,
  "limiter_gain_db": 32.0,
  "lufs_i": -9.2,
  "peak_dbfs": -3.1,
  "true_peak_dbtp": -2.3,
  "lufs_distance": 0.2,
  "true_peak_safe": true
}
```

**On failure**: Log with `"status": "failed"`, include error message

---

## Parameter Clamping

**Always clamp to device min/max** (from OSC):
```python
# Get min/max from OSC
param_info = params["Threshold"]
min_val = param_info["min"]  # e.g., -60.0
max_val = param_info["max"]  # e.g., 0.0

# Clamp before setting
threshold = max(min_val, min(max_val, threshold))
```

**Why**: Prevents invalid parameter writes, OSC rejects out-of-range values

---

## Mode-Specific Search

**streaming_safe** (-14 LUFS, -1 dBTP):
- Start conservative (GR 8-12 dB)
- Small steps (compression priority)
- Minimize limiting (quality over loudness)

**loud_preview** (-9 LUFS, -2 dBTP):
- Start aggressive (GR 12-15 dB)
- Medium steps (balance quality + loudness)
- Use Saturator + compression + moderate limiting

**headroom** (-10 LUFS, -6 dBFS):
- Start moderate (GR 10-12 dB)
- Small steps (safety priority)
- Conservative limiting

---

## Best Practices

**Do**:
- ✅ Optimize in phases (compression → saturation → limiting)
- ✅ Detect diminishing returns (stop when ineffective)
- ✅ Log every iteration (even failures)
- ✅ Use best result if convergence not achieved
- ✅ Clamp parameters to device min/max

**Don't**:
- ❌ Move all knobs simultaneously (creates oscillation)
- ❌ Push limiter to max (diminishing returns, distortion)
- ❌ Ignore peak safety (always enforce true peak limit)
- ❌ Skip logging (receipts are critical for debugging)

---

## What's NOT Canon (Track-Dependent)

**Not permanent**:
- Exact LUFS target (-9 vs -14 vs -10)
- Starting parameter values
- Step sizes (aggressive vs conservative)
- Max iterations (15 is tuneable)
- Convergence tolerance (0.5 LU is tuneable)

**These vary by**: Genre, track dynamics, user preference, artifact tolerance

---

**This search contract is permanent. Optimization structure is stable, parameters are tuneable.**
