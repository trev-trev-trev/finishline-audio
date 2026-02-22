# Streaming Loudness Targets (Reference)

**Source**: Official streaming service normalization standards  
**Date**: 2026-02-22

---

## Streaming Service Targets

| Service | Target LUFS | Normalization | Notes |
|---------|------------|---------------|-------|
| **Spotify** | -14 LUFS | Yes (default) | Turns down louder tracks, turns up quieter |
| **Apple Music** | -16 LUFS | Yes (Sound Check) | More conservative target |
| **YouTube Music** | -13 to -15 LUFS | Yes | Variable depending on content |
| **Amazon Music** | -14 LUFS | Yes | Similar to Spotify |
| **Tidal** | -14 LUFS | Yes | HiFi platform, same target |

---

## Our Strategy: **Louder Than Normalization**

**Why go louder than -14 LUFS?**
1. **Impact/Presence**: Louder = more engaging, more emotional impact
2. **Competitive**: Most commercial releases are -8 to -10 LUFS
3. **Normalization headroom**: Services turn down loud tracks, preserving dynamics
4. **User perception**: "Loud" = "professional" in streaming context

**Our target**: **-8.0 LUFS** (maximum competitive loudness)

---

## Loudness Spectrum

```
-20 LUFS ────── Very quiet (acoustic, ambient)
-16 LUFS ────── Apple Music target
-14 LUFS ────── Spotify/YouTube target
-12 LUFS ────── Moderately loud (indie rock, folk)
-10 LUFS ────── Loud (pop, EDM)
 -9 LUFS ────── Very loud (competitive pop)
 -8 LUFS ────── MAXIMUM (commercial ceiling) ← OUR TARGET
 -7 LUFS ────── Hyper-compressed (EDM, hip-hop)
 -6 LUFS ────── Over-limited (distortion risk)
```

**Sweet spot**: -8 to -9 LUFS (loud, competitive, still clean)

---

## Why -8 LUFS is the Ceiling

**Physics**: Peak cap limits loudness
- Peak must stay ≤ -6.0 dBFS (true peak safety for format conversion)
- More compression + limiting = more loudness
- But: Over-compression = pumping, distortion, loss of dynamics

**Commercial releases**:
- Pop/EDM: -7 to -9 LUFS (very loud)
- Rock/Indie: -9 to -11 LUFS (loud but dynamic)
- Classical/Jazz: -16 to -20 LUFS (preserve dynamics)

**Our genre** (electronic, smooth, polished):
- Target: **-8.0 LUFS** (maximum loudness, competitive ceiling)
- Acceptable range: -7.5 to -8.5 LUFS

---

## Implementation Strategy

### Compression (Glue Compressor)

**Goal**: Increase RMS without destroying dynamics

**Settings for -8 LUFS**:
- Threshold: -35 to -45 dB (GR 18-22 dB on loud sections)
- Makeup: 22-28 dB (compensate for GR + boost output)
- Ratio: 5:1 to 8:1 (strong but not brick-wall)
- Attack: 5-10 ms (fast for control, not transparent)
- Release: Auto or 100-200 ms

**Result**: High RMS input to limiter

### Limiting (Limiter)

**Goal**: Final loudness boost + peak safety

**Settings for -8 LUFS**:
- Ceiling: -6.0 to -6.2 dBFS (tight peak control)
- Gain: 35-42 dB (maximum within device range)
- Release: Default or Auto

**Result**: Peak-safe output at maximum loudness

---

## Current Implementation

**Command**: `flaas master-consensus`

**Target**: -8.0 LUFS (MAXIMUM competitive loudness)

**Strategy**:
- Start very aggressive: Threshold -40, Makeup 25, Limiter gain 40
- Iterate up to 15 times
- Push loudness as hard as possible
- Converge when LUFS within 0.5 LU of target, peak safe

**Output**: `output/master_consensus.wav` (LOUD, not quiet)

---

**Reference**: This is what streaming services expect and what commercial releases hit.

**Our approach**: Hit the ceiling (-8 LUFS) for maximum impact.
