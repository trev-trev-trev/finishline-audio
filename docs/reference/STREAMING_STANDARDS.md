# Streaming Standards (Official Specifications)

**Source**: Official platform documentation  
**Date**: 2026-02-22

---

## Spotify Loudness Normalization

**Official guidance**: [Spotify for Artists - Loudness Normalization](https://artists.spotify.com/help/article/loudness-normalization)

**Target behavior** (not hard delivery spec):
- **LUFS-I**: -14 LUFS (integrated) ← Spotify's normalization target
- **True Peak**: ≤ -1 dBTP (recommended for codec safety)

**Important**: This is Spotify's **recommendation**, not a hard delivery requirement. They normalize all tracks to -14 LUFS:
- Tracks **louder** than -14 LUFS: Turned down
- Tracks **quieter** than -14 LUFS: Turned up (if user enables "Loud" mode)

**True peak note**:
- For tracks louder than -14 LUFS, Spotify recommends managing true peak to avoid codec distortion
- Suggested: ≤ -2 dBTP for louder masters
- Prevents inter-sample peaks during MP3/AAC encoding

---

## Apple Music / iTunes

**Target**:
- **LUFS-I**: -16 LUFS (integrated)
- **True Peak**: ≤ -1 dBTP

**Note**: More conservative than Spotify

---

## YouTube

**Target**:
- **LUFS-I**: -13 to -15 LUFS
- **True Peak**: ≤ -1 dBTP

**Variable**: Depends on content type (music vs speech)

---

## Amazon Music / Tidal

**Target**:
- **LUFS-I**: -14 LUFS
- **True Peak**: ≤ -1 dBTP

**Similar to Spotify**

---

## Mode Definitions (Corrected)

### Mode 1: Streaming Safe (Conservative, Default)

**Target**: LUFS -14, True Peak -1 dBTP

**Use case**: Maximum compatibility, follows Spotify's recommendation

**Trade-off**: Quieter initial playback (normalized up by service)

**Note**: This is the safest default - avoids overcooking

### Mode 2: Loud Preview (Competitive Commercial)

**Target**: LUFS -9, True Peak -2 dBTP

**Use case**: Competitive loudness, **addresses "super quiet" perception**

**Trade-off**: Normalized down by services, but perceived as "louder" initially

**Note**: Commercial releases vary by genre (-8 to -12 LUFS typical for pop/EDM, -10 to -14 for indie/acoustic). Use your ears and watch for artifacts.

### Mode 3: Headroom Safe (Internal Safety)

**Target**: LUFS -10, Peak -6 dBFS (sample peak)

**Use case**: Internal safety margin for format conversion

**Trade-off**: Extra headroom, may sound quieter

---

## True Peak vs Sample Peak

**Sample Peak (dBFS)**:
- Measures highest sample value in digital file
- Our current measurement

**True Peak (dBTP)**:
- Measures peak of reconstructed analog waveform (4x oversampling)
- Accounts for inter-sample peaks
- Required for streaming specs
- Typically 0.5-1.5 dB higher than sample peak

**Example**:
- Sample peak: -6.0 dBFS
- True peak: -4.5 dBTP (1.5 dB difference)

**Why it matters**: Codec conversion (MP3, AAC) can cause true peak to exceed 0 dBFS even if sample peak is safe

---

## Our Correction

**Previous (incorrect)**:
- Target: -8.0 LUFS, -6 dBFS sample peak
- Claimed: "Spotify ceiling" (wrong - Spotify target is -14, not -8)

**Corrected**:
- Mode 1: **streaming_safe** = -14 LUFS, -1 dBTP (default, conservative)
- Mode 2: **loud_preview** = -9 LUFS, -2 dBTP (competitive, genre-dependent)
- Mode 3: **headroom** = -10 LUFS, -6 dBFS (internal safety)

**Implementation**: `flaas master-consensus --mode <name>`

**Default**: `streaming_safe` (conservative, avoids overcooking)

---

## What "Super Quiet" Actually Means

**User perception**: "Can barely hear it"

**Likely causes**:
1. LUFS target too conservative (-10.5 or -14 is quiet for modern music)
2. Peak cap limiting loudness gain (we hit this in experiments)
3. Insufficient compression before limiter (limiter alone has diminishing returns)

**Solution**:
1. Target **-9 LUFS** (loud preview mode, competitive)
2. Add **Saturator** before Limiter (raises RMS more efficiently than extreme compression)
3. Use **true peak -2 dBTP** (safer than -1 for loud masters)
4. Stop pushing limiter gain when returns < 0.2 LU per +1 dB

---

**Status**: Correcting implementation to match official streaming standards.
