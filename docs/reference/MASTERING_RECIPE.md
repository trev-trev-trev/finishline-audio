# Mastering Recipe: Compression + Limiting Strategy

**Date**: 2026-02-22  
**Source**: 16 export experiments  
**Status**: Validated, operational

---

## Critical Invariants (Non-Negotiable)

1. **Master fader = 0.0 dB** - Fader is post-device chain, defeats limiter if boosted
2. **Limiter must be last** - Final device in chain (after Utility, EQ, Compressor)
3. **Normalize = OFF** - In Export dialog (prevents peak manipulation)
4. **Rendered Track = Master** - In Export dialog (not "Selected Tracks Only")
5. **Loop/selection set** - Export only the desired loop section

**Ableton signal flow**:
```
[Utility] → [EQ Eight] → [Glue Compressor] → [Limiter] → Master Fader → Output
```

---

## The Problem: Limiter Alone is Insufficient

**Physics**: Peak-capped limiter restricts loudness gain

**Why**: 
- Limiter reduces peaks to stay under ceiling
- Lowering peaks reduces RMS contribution from transients
- More limiter gain → more peak reduction → diminishing LUFS returns

**Evidence** (from experiments):
- Limiter gain +15 dB: LUFS -14.33, Peak -6.00
- Limiter gain +19 dB: LUFS -13.83, Peak -6.00
- **Gain delta +4 dB → LUFS delta only 0.5 LU**

**Conclusion**: Need compression BEFORE limiter to increase RMS

---

## The Solution: Compression + Limiter Strategy

**Device chain**: `[Glue Compressor] → [Limiter]`

**Roles**:

1. **Glue Compressor** - Increase RMS/loudness
   - Reduce dynamic range (GR 10-18 dB on loud sections)
   - Increase average level (RMS)
   - Apply makeup gain (output boost)
   - Result: Louder, more consistent input to limiter

2. **Limiter** - Safety ceiling + final boost
   - Prevent clipping (hard ceiling)
   - Apply final gain boost (within ceiling constraint)
   - Result: Peak-safe output at target loudness

**Why this works**: Compression raises average level WITHOUT exceeding peaks, giving limiter more headroom for gain

---

## Compression Strategy (Glue Compressor)

### Target Gain Reduction (GR)

**Range**: 10-18 dB on loud sections

**How to set**:
- Play loop
- Lower Threshold until GR meter shows target (12-15 dB typical)
- Listen: Should sound natural, not "squashed"

**Parameter**: Threshold (dB)
- Lower threshold → more compression → higher GR
- Typical range: -25 to -40 dB (depends on input level)

### Makeup Gain

**Range**: 10-20 dB

**Purpose**: Compensate for GR + boost RMS

**Rule**: Makeup ≈ GR target (e.g., GR 15 dB → Makeup 15 dB)

**Parameter**: Makeup (dB)
- Direct output boost
- Increases RMS feeding into limiter

### Other Settings

**Ratio**: 3:1 to 10:1
- Lower (3:1): Gentler, more natural
- Higher (10:1): More aggressive, limiting-like
- Typical: 4:1 to 6:1

**Attack**: 5-10 ms
- Fast attack (< 5ms): More transparent, less punch
- Slow attack (> 10ms): Preserves transients, more punch
- Typical: 10 ms

**Release**: Auto or 50-200 ms
- Auto: Adapts to material (recommended)
- Manual: 100-200 ms for glue effect

**Dry/Wet**: 100% (wet)
- Full processing (no parallel compression needed here)

---

## Limiting Strategy (Limiter)

### Ceiling

**Range**: -6.0 to -6.5 dBFS

**Purpose**: Safety margin for peak control

**Rule**: Set 0.3-0.5 dB below actual target (-6.0) to prevent tiny overs

**Parameter**: Ceiling (dB)
- Hard limit, no signal exceeds this
- Typical: -6.3 dB (target -6.0, margin 0.3)

### Gain

**Range**: 24-34 dB

**Purpose**: Final loudness boost (constrained by ceiling)

**Rule**: As high as possible without causing excessive limiting

**Parameter**: Gain (dB)
- Applied before ceiling
- If too high: Over-limiting, distortion, pumping
- Typical: 28-32 dB

**Interaction with compression**:
- More compression → higher RMS → limiter can apply more gain
- Less compression → lower RMS → limiter must work harder (diminishing returns)

### Other Settings

**Release**: Default or Auto
- Affects limiter release time
- Shorter: More transparent, less pumping
- Longer: More pumping, more aggressive

**Lookahead**: Default (usually 1-5ms)
- Allows limiter to anticipate peaks
- Improves transparency

---

## Workflow: Iterative Convergence

### Manual Iteration (Validated)

1. **Set Glue Compressor**: Target GR (via Threshold), Makeup
2. **Set Limiter**: Ceiling -6.3, Gain 28-32
3. **Export**: Master → Loop → WAV
4. **Verify**: `flaas verify-audio <wav>`
5. **Adjust**:
   - Peak > -6.0: Reduce limiter gain OR lower ceiling
   - LUFS < -10.5: Lower threshold (more GR) OR increase makeup OR increase limiter gain
6. **Repeat** until targets hit

### Automated Iteration (Implemented)

**Command**: `flaas experiment-run <config.json>`

**Per experiment**:
1. Auto-set params via OSC
2. Auto-export via UI automation (macOS)
3. Auto-verify LUFS/peak
4. Log to `output/experiments.jsonl`
5. Early exit on success

**Config**: Parameter sweep array (threshold, makeup, ceiling, gain)

---

## Target Metrics

**LUFS-I**: -10.50 ± 0.5 LU (integrated loudness)
- Spotify normalization target: -14 LUFS (we're targeting louder for impact)
- Our target: -10.50 (competitive streaming loudness)

**Peak**: ≤ -6.00 dBFS (true peak safety margin)
- Prevents clipping during format conversion (MP3, streaming codecs)
- Safety margin: 6 dB below 0 dBFS

---

## Curated Presets (Starting Points)

### CONSENSUS (Balanced, Safest)
- **Glue**: Threshold ~-30 dB (GR 12-15 dB), Makeup 18 dB, Ratio 4:1
- **Limiter**: Ceiling -6.3 dB, Gain 30 dB
- **Character**: Clean, natural, transparent

### VARIANT A (Controlled, Clean)
- **Glue**: Threshold ~-25 dB (GR 8-12 dB), Makeup 15 dB, Ratio 3:1
- **Limiter**: Ceiling -6.3 dB, Gain 32 dB
- **Character**: More dynamic, less compressed, cleaner

### VARIANT B (Loud, Forward)
- **Glue**: Threshold ~-35 dB (GR 15-18 dB), Makeup 20 dB, Ratio 6:1
- **Limiter**: Ceiling -6.5 dB, Gain 34 dB
- **Character**: More compressed, louder, more aggressive

**Note**: Exact thresholds vary by input level; use iterative search to hit LUFS target

---

## Key Learnings (From 16 Experiments)

1. **Master fader defeats limiter** - Must be 0.0 dB
2. **Compression is required** - Limiter alone hits diminishing returns
3. **Peak cap limits loudness** - Trade-off between LUFS and peak safety
4. **GR 12-18 dB is sweet spot** - Natural compression, effective RMS boost
5. **Makeup ≈ GR target** - Good starting point for output level
6. **Ceiling margin critical** - 0.3-0.5 dB below target prevents overs
7. **Iterative approach works** - Adjust → export → verify → repeat

---

## Psychoacoustic Goals

**Smoothness**: Even spectral balance, no harsh transients
- Achieved via: Gentle compression (Attack 10ms), moderate ratio (4:1)

**Fullness**: Rich low-end, present mids, clear highs
- Achieved via: EQ Eight (pre-compression), compression (sustain), makeup gain

**Loudness**: Competitive streaming level without distortion
- Achieved via: Compression (RMS boost) + limiter (peak control)

**Clarity**: Separation, definition, no mud
- Achieved via: Controlled compression (not over-squashed), EQ balance

---

## Export Automation (macOS)

**UI automation**: AppleScript keystroke sequence
- Cmd+Shift+R → Return → Cmd+Shift+G → folder → filename → Save
- Requires macOS Accessibility permissions (Terminal)

**File stabilization**: Wait for size/mtime stable (2 consecutive checks)

**Verification**: LUFS-I (BS.1770) + Peak dBFS

**Logging**: JSONL receipts with SHA256 audit trail

**See**: `src/flaas/ui_export_macos.py` for implementation

---

**Status**: Recipe validated. Ready for automated candidate generation.

**Next**: Run `flaas master-candidates` to generate 3 Spotify-ready masters.
