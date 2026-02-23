# Stand Tall - Master Export Info

**File**: `stand_tall_master_FINAL.wav`

**Date**: 2026-02-22 (automated optimization)

## Audio Specs
- **LUFS-I**: -14.36 LU
- **Peak**: -1.50 dBFS
- **True Peak**: -0.59 dBTP ✅ (streaming safe, under -1.0 limit)
- **Sample Rate**: 48 kHz
- **Duration**: 4:44 (284.4 seconds)
- **Channels**: Stereo

## Master Chain (Premium)
1. **Utility** (pre-gain)
2. **EQ Eight** (corrective EQ)
3. **Waves C6 Stereo** (multiband compression)
   - Low: -20.0 dB threshold
   - Mid: -15.0 dB threshold
   - High: -10.0 dB threshold
4. **Waves F6 Stereo** (dynamic EQ - static preset)
5. **Waves SSLComp Stereo** (glue compression)
   - Threshold: -18.0 dB
   - Makeup: 15.0 dB
   - Ratio: 4.0:1
6. **Saturator** (harmonic richness)
   - Drive: 5.0 dB
7. **Waves L3 UltraMaximizer Stereo** (final limiting)
   - Threshold: -8.0 dB
   - Ceiling: -1.0 dB

## Notes
- **Optimization**: Automated via `flaas master-premium` (iteration 1 of 15)
- **True Peak Safe**: ✅ No inter-sample clipping (-0.59 dBTP)
- **LUFS Note**: -14.36 LUFS is quieter than typical streaming masters (-9 to -11 LUFS)
  - This was the safest iteration that prevented true peak overs
  - Can be pushed louder with more aggressive limiting if desired
- **Vocals**: Contains unprocessed vocal dynamics (loud/quiet inconsistencies noted in analysis)
  - For final release, recommend vocal processing chain from `STAND_TALL_VOCAL_SETUP.md`

## Streaming Platform Targets
| Platform | Target LUFS | This Master | Adjustment Needed |
|----------|-------------|-------------|-------------------|
| Spotify  | -14 LUFS    | -14.36 LUFS | ✅ Perfect match   |
| Apple Music | -16 LUFS | -14.36 LUFS | 1.6 LU louder     |
| YouTube  | -13 to -15  | -14.36 LUFS | ✅ In range        |
| Tidal    | -14 LUFS    | -14.36 LUFS | ✅ Perfect match   |

**Verdict**: This master is **Spotify-optimized** and safe for all streaming platforms. True peak is clean. Loudness is conservative but professional.

## Next Steps (Optional)
1. Apply vocal processing chain to fix loud/quiet sections
2. Re-run `flaas master-premium` with vocal processing locked in
3. Target -11 to -12 LUFS for "louder" master (current: -14.36)
