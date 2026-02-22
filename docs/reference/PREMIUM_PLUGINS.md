# Premium Plugin Integration

**Date**: 2026-02-22  
**Status**: FUTURE ENHANCEMENT (not blocking current master)

---

## Available Premium Plugins

**Waves Bundle**:
- Renaissance Compressor (RCompressor) - Character compression
- Renaissance Vox (RVox) - Vocal compression with body
- L1 Limiter, L2 Limiter, L3 Multimaximizer - Professional limiters
- API 2500 - Bus compressor with analog character
- SSL G-Master Buss Compressor - Classic glue
- Kramer Master Tape - Analog saturation

**Output Bundle**:
- Output Arcade - Creative sampler/effects
- Output Rhythm - Rhythm engine
- Output Bass - Bass synthesis
- (Other Output plugins user has)

---

## Swap Strategy (When Chain is Working)

**Current status**: Chain works perfectly with Ableton stock plugins
- Glue Compressor → Saturator → Limiter
- User feedback: "Sounds incredible, just needs to be louder"

**Loudness issue root cause**: LUFS target too conservative (NOT plugin quality)

**Solution order**:
1. **Fix loudness FIRST**: Run `--mode loud_preview` (-9 LUFS)
2. **If still needs character**: Swap plugins as enhancement

---

## When to Swap (Not Now, But Later)

**Indicators that plugin swap would help**:
- ✅ LUFS target already hit (-9 LUFS achieved)
- ✅ Peak safe (true peak ≤ -2 dBTP)
- ❌ BUT: Sound is "thin", "harsh", "digital", "sterile"

**If current master sounds "incredible" but just "too quiet"**:
- **Don't swap plugins** (quality is fine)
- **Just run loud_preview mode** (louder target)

---

## Recommended Swaps (If Enhancing Character)

### Swap 1: Glue Compressor → Renaissance Compressor

**Why**: 
- Renaissance adds analog character (warmth, body)
- More "musical" than stock Glue
- Better for pop/EDM (adds density)

**Trade-off**: 
- More CPU
- Less transparent (adds color, may not fit all genres)

**When**: If stock Glue sounds "digital" or "sterile"

---

### Swap 2: Saturator → Kramer Master Tape

**Why**:
- Analog tape saturation (harmonic distortion, warmth)
- More "vintage" character than stock Saturator
- Adds subtle compression + saturation in one

**Trade-off**:
- More CPU
- Less predictable (tape modeling is complex)

**When**: If stock Saturator sounds "harsh" or lacks warmth

---

### Swap 3: Limiter → Waves L2 or L3

**Why**:
- L2/L3 are industry-standard mastering limiters
- More transparent than stock Limiter at high gain
- Better artifact handling (dithering, lookahead)

**Trade-off**:
- More CPU
- More parameters (complexity)

**When**: If stock Limiter causes distortion or pumping at high gain

---

## Integration Strategy (Future)

**Phase 1**: Get OSC control working for Waves plugins
- Resolve device by name (e.g., "Renaissance Compressor")
- Map parameters (Threshold, Ratio, Attack, Release, Makeup)
- Same pattern as stock plugins

**Phase 2**: Create preset configs
- `master_chain_waves.json` - Waves-based chain
- `master_chain_stock.json` - Ableton stock chain
- Allow swapping via config

**Phase 3**: A/B testing
- Export with stock chain → `output/master_stock.wav`
- Export with Waves chain → `output/master_waves.wav`
- Listen and compare (blind test if possible)

---

## Current Recommendation

**For THIS master (right now)**:
1. **Keep stock plugins** (Glue, Saturator, Limiter)
2. **Run loud_preview mode** (-9 LUFS, -2 dBTP)
3. **Get the loudness right FIRST**
4. **Listen to result**
5. **If quality is good** → Ship it
6. **If needs character** → Consider Waves swap as enhancement

**Why this order**: Loudness target is the bottleneck (NOT plugin quality)

---

## Plugin Quality Assessment

**Stock Ableton plugins are professional-grade**:
- Glue Compressor: Based on SSL bus compressor (industry standard)
- Saturator: Clean soft clip, minimal artifacts
- Limiter: Lookahead brick-wall limiter (sufficient for most use cases)

**Waves adds**:
- Analog modeling (harmonic distortion, warmth)
- Character/color (may or may not fit genre)
- Brand recognition (psychological, not necessarily better)

**Bottom line**: Stock plugins can achieve commercial loudness. Waves adds character, not capability.

---

## Output Plugins (Creative, Not Mastering)

**Output Arcade, Rhythm, Bass**: 
- These are **creative tools** (sound design, synthesis)
- NOT mastering/mixing tools
- Use during production, not mastering chain

**Example**: Output Bass on a bass track (pre-master), not on Master bus

---

## Next Steps

**Now**: Run `flaas master-consensus --mode loud_preview` with stock plugins

**After listening**:
- **If sounds great**: Ship it, move to next track
- **If needs more character**: Create Waves swap config
- **If needs creative enhancement**: Apply Output plugins to individual tracks

---

**Recommendation: Get loudness right with stock plugins first. Waves swap is enhancement, not fix.**
