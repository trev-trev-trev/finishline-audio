# Streaming Standards (Official Specifications)

**Source**: Official platform documentation  
**Date**: 2026-02-22

---

## Spotify Loudness Normalization

**Official guidance**: [Spotify for Artists - Loudness Normalization](https://artists.spotify.com/help/article/loudness-normalization)

**Target**:
- **LUFS-I**: -14 LUFS (integrated)
- **True Peak**: ≤ -1 dBTP (recommended)

**Loudness penalty note**: 
- Tracks louder than -14 LUFS are turned down
- Tracks quieter than -14 LUFS are turned up (if user enables "Loud" mode)

**True peak note**:
- For tracks louder than -14 LUFS, Spotify recommends managing true peak to avoid codec distortion
- Suggested: ≤ -2 dBTP for louder masters

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

### Mode 1: Streaming Safe (Official Spec)

**Target**: LUFS -14, True Peak -1 dBTP

**Use case**: Maximum compatibility, official Spotify/streaming standard

**Trade-off**: Quieter initial playback (normalized up by service)

### Mode 2: Loud Preview (Competitive Commercial)

**Target**: LUFS -9 to -8, True Peak -2 dBTP

**Use case**: Competitive loudness, matches commercial releases

**Trade-off**: Normalized down by services, but perceived as "louder" initially

**Note**: This is what most commercial pop/EDM releases actually target

### Mode 3: Headroom Safe (Internal Safety)

**Target**: LUFS flexible, Peak -6 dBFS (sample peak)

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
- Claimed: "Spotify ceiling"

**Corrected**:
- Mode 1: -14 LUFS, -1 dBTP (streaming safe, official)
- Mode 2: -9 LUFS, -2 dBTP (loud preview, competitive)
- Mode 3: -6 dBFS sample peak (headroom safe, internal)

**Implementation**: Add modes to `flaas master-consensus --mode <name>`

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
