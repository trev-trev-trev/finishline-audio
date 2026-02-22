# QUICKSTART

**Repo**: `/Users/trev/Repos/finishline_audio_repo`

## Current Status

**Export loop WORKING** ✅ Manual iteration functional

**Latest**: LUFS -13.59, Peak -6.00 (gap to target: 3.09 LU)

**Loop**: `configure → export → verify-audio → adjust → repeat`

**Next**: Close LUFS gap via compression tuning

## Key Files (Priority Order)

1. `STATE.md` - Current operational state
2. `PRIORITY.md` - Execution order correction
3. `docs/ENDPOINT_REGISTRY.json` - OSC endpoint specifications
4. `DISCOVERY.md` / `NEXT_CHAPTER.md` - Blocked until export works
5. `docs/status/STATUS.md` - Operating procedures

## Commands

```bash
# Smoke tests
make smoke       # 7s, read-only
make write-fast  # 9s, dev gate
make write       # 39s, commit gate

# Audio verification
flaas verify-audio <wav>  # Check LUFS/peak vs targets
```

## Next Action (Manual)

**In Ableton** (Master chain tuning):
1. Glue Compressor: Lower Threshold → GR 15-18 dB
2. Glue Compressor: Makeup +15-18 dB
3. Limiter: Gain +28-30 dB, Ceiling -6.5 dB
4. Export Master (loop) → `output/master_iter<N>.wav`

**After export**:
```bash
flaas verify-audio output/master_iter<N>.wav
```

**See detailed workflow**: `docs/reference/EXPORT_FINDINGS.md`
