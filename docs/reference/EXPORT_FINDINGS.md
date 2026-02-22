# Export Findings: Master Chain Rendering

**Date**: 2026-02-22  
**Source**: Export triage chat log (16 experiments)  
**Status**: Export loop working, critical findings documented

---

## Critical Discoveries

### 1. Master Fader is Post-Device Chain

**Finding**: Master fader processes AFTER all devices (Utility, EQ, Limiter, etc.)

**Impact**: Master fader > 0.0 dB defeats Limiter ceiling

**Proof**:
- Experiment #9: Limiter ceiling -6.0, peak -3.77 (fader was boosted)
- Experiment #10: Master fader 0.0, peak -9.77 (ceiling restored)

**Rule**: **Master fader must be at 0.0 dB for predictable peak control**

---

### 2. Limiter Alone Cannot Reach LUFS Target

**Finding**: Peak-capped limiter restricts loudness gain

**Results**:
- Limiter gain +15: LUFS -14.33, peak -6.00
- Limiter gain +19: LUFS -13.83, peak -6.00
- **Diminishing returns**: More gain → more limiting → minimal LUFS rise

**Conclusion**: Need compression/saturation BEFORE limiter to increase RMS/loudness

---

### 3. Compression + Limiter Strategy

**Finding**: Glue Compressor before Limiter enables LUFS target

**Device chain**: `[Utility] → [EQ Eight] → [Glue Compressor] → [Limiter]`

**Glue Compressor role**:
- Reduce dynamic range (GR 10-18 dB)
- Increase RMS/average level
- Apply makeup gain

**Limiter role**:
- Safety ceiling (prevent clipping)
- Final gain boost (within ceiling constraint)

**Results**:
- Experiment #14: Glue + Limiter gain 24 → LUFS -13.59, peak -6.00 ✅
- Experiment #16: Makeup 15 + Limiter gain 28 → LUFS -14.17, peak -6.50 ✅

**Best result so far**: LUFS -13.59 (target -10.50, 3.09 LU gap remaining)

---

### 4. Master Export Rendering Validated

**Finding**: Export path is correct when properly configured

**Proof**: Experiment #4 (master fader mute):
- LUFS: -inf
- Peak: -138.47
- **Confirms**: Master device chain IS rendering

**Export settings validated**:
- Rendered Track = Master ✅
- Normalize = OFF ✅
- Selection/Loop only = works ✅

---

## Experiment Log (16 exports)

| # | File | LUFS | Peak | LUFS Pass | Peak Pass | Notes |
|--:|------|-----:|-----:|:---------:|:---------:|-------|
| 1 | master_iter1.wav | -19.16 | -3.77 | ❌ | ❌ | Baseline |
| 2 | master_iter2.wav | -19.16 | -3.77 | ❌ | ❌ | Limiter not applied |
| 3 | sanity_ceiling_-20.wav | -19.16 | -3.77 | ❌ | ❌ | Wrong chain edited |
| 4 | sanity_master_fader_mute.wav | -inf | -138.47 | ❌ | ✅ | **Confirms render path** |
| 5 | master_iter3.wav | -10.98 | -0.00 | ✅ | ❌ | Post-limiter gain issue |
| 6 | master_iter4.wav | -10.98 | -0.00 | ✅ | ❌ | Same |
| 7 | master_iter5.wav | -10.98 | -0.00 | ✅ | ❌ | Same |
| 8 | sanity_limiter_only.wav | -22.57 | -14.00 | ❌ | ✅ | Limiter active when isolated |
| 9 | sanity_limiter_ceiling_-6.wav | -19.16 | -3.77 | ❌ | ❌ | Master fader defeated ceiling |
| 10 | sanity_master_fader0_-6.wav | -25.16 | -9.77 | ❌ | ✅ | **Fader 0.0 = predictable** |
| 11 | sanity_gain15.wav | -14.33 | -6.00 | ❌ | ✅ | Limiter gain limited by ceiling |
| 12 | sanity_gain19.wav | -13.83 | -6.00 | ❌ | ✅ | Diminishing returns |
| 13 | sanity_glue.wav | -16.34 | -6.00 | ❌ | ✅ | Glue + Limiter |
| 14 | sanity_glue_gain24.wav | -13.59 | -6.00 | ❌ | ✅ | **Best LUFS so far** |
| 15 | sanity_glue_gr12_makeup10.wav | -15.00 | -6.00 | ❌ | ❌ | Borderline peak |
| 16 | sanity_glue_makeup15_gain28.wav | -14.17 | -6.50 | ❌ | ✅ | Lower ceiling for safety |

---

## Validated Configuration

**Master chain** (left to right):
```
[Utility] → [EQ Eight] → [Glue Compressor] → [Limiter]
```

**Master fader**: 0.0 dB (critical for peak control)

**Glue Compressor settings** (for experiment #14):
- Threshold: Adjust for 10-18 dB GR
- Makeup: Varies (0-15 dB)
- Attack/Release: Default

**Limiter settings** (for experiment #14):
- Ceiling: -6.0 dB
- Gain: +24 dB
- Release: Default

**Result**: LUFS -13.59, Peak -6.00 (peak safe, LUFS 3.09 LU from target)

---

## Required for Target (-10.50 LUFS, -6.00 peak)

**Current gap**: 3.09 LU (-13.59 → -10.50)

**Options**:
1. **More compression**: Increase GR (15-18 dB) + Makeup gain
2. **Saturation**: Add subtle saturation before compressor (increases RMS)
3. **Multi-band**: Use multi-band compression for independent control
4. **Higher limiter gain**: Increase from +24 to +28-30 dB (if peak allows)

**Constraint**: Peak must stay ≤ -6.00 dBFS

---

## Workflow Recipe (Repeatable)

### Manual Iteration Loop

1. **Configure Master chain**:
   ```
   [Glue Compressor] → [Limiter]
   Master fader: 0.0 dB
   ```

2. **Glue settings**:
   - Threshold: -20 to -30 dB (GR target: 12-18 dB)
   - Makeup: 10-15 dB
   - Ratio: 3:1 to 10:1

3. **Limiter settings**:
   - Ceiling: -6.0 to -6.5 dB (safety margin)
   - Gain: 24-30 dB

4. **Export**:
   - Rendered Track = Master
   - Normalize = OFF
   - File: `output/master_iter<N>.wav`

5. **Verify**:
   ```bash
   flaas verify-audio output/master_iter<N>.wav
   ```

6. **Adjust** based on results:
   - Peak > -6.0: Reduce limiter gain OR lower ceiling
   - LUFS < -10.5: Increase compression OR increase limiter gain
   - Repeat

---

## Automation Feasibility (Verified)

**Export trigger**: ❌ NOT available via OSC

**Probe result**: `/live/song/export/structure` returns `(1,)` (status flag, not actionable)

**Prior probe**: `/live/song/export/audio` timed out (endpoint doesn't exist)

**Conclusion**: Export remains manual (File → Export Audio/Video click required)

---

## Semi-Automated Workflow (Feasible)

### What CAN be automated:
1. **Parameter control** (Glue Compressor, Limiter, Master fader)
2. **Verification** (`verify-audio` post-export)
3. **Logging** (settings + results → `experiments.jsonl`)

### What CANNOT be automated:
- **Export trigger** (manual click required per experiment)

### Batch Experiment Runner (Proposed)

**Command**: `flaas batch-experiment experiments.json`

**Flow**:
```python
for exp in experiments:
    # Automated
    set_glue_params(exp.threshold, exp.makeup, exp.ratio)
    set_limiter_params(exp.ceiling, exp.gain)
    set_master_fader(0.0)
    
    # Manual (PAUSE)
    print(f"Export to output/exp_{exp.id}.wav")
    input("Press Enter after export completes...")
    
    # Automated
    result = verify_audio(f"output/exp_{exp.id}.wav")
    log_experiment(exp.id, exp.settings, result)
```

**ROI**: 10-100x faster than fully manual (only export click is manual)

**Required OSC endpoints** (all available):
- `/live/track/get/volume` (master fader)
- `/live/track/set/volume` (master fader)
- `/live/device/set/parameter/value` (Glue + Limiter params)

**See**: `docs/reference/EXPORT_AUTOMATION_FEASIBILITY.md` for probe details

---

## Key Learnings

1. **Master fader is post-device chain** - Must be at 0.0 dB
2. **Limiter alone is insufficient** - Need compression for loudness
3. **Peak cap limits loudness gain** - Trade-off between LUFS and peak safety
4. **Compression + limiter strategy works** - Achieved -13.59 LUFS @ -6.00 peak
5. **Export settings matter** - Rendered Track = Master, Normalize = OFF
6. **Iterative approach required** - 3.09 LU gap remains, needs more compression

---

## Recommended Next Steps

### Immediate (Manual)

1. **Increase compression**:
   - Glue Threshold: Lower (more GR)
   - Glue Makeup: +15-18 dB
   - Limiter Gain: +28-30 dB
   - Limiter Ceiling: -6.5 dB (safety)

2. **Export + verify** → Iterate until LUFS -10.5, peak -6.0

### Short-term (Automation)

1. **Add master fader control** to FLAAS
2. **Add Glue Compressor control** (threshold, makeup, ratio)
3. **Update Limiter control** (already have limiter-set command)
4. **Add auto-adjustment logic** based on verify-audio results

### Long-term (Full Automation)

1. **Scripted export** via OSC (research `/live/song/export/*` endpoints)
2. **Full closed-loop**: plan → apply → export → verify → adjust → repeat
3. **Convergence algorithm**: Auto-tune compression/limiting to hit targets

---

**Status**: Export loop functional. Manual iteration working. Gap to target: 3.09 LU.
