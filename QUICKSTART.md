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

# Automated mastering (NEW)
flaas master-candidates           # Generate 3 curated masters (zero clicks)
flaas experiment-run <config.json>  # Custom parameter sweep
```

## Next Action (Fully Automated)

**Generate ONE consensus master** (zero clicks, properly loud):
```bash
flaas master-consensus
```

**What happens**:
1. Up to 10 iterations with adaptive optimization
2. Target: **LUFS -9.0** (competitive loudness, NOT quiet)
3. Auto-sets params (Glue, Limiter) via OSC
4. Auto-exports via macOS UI automation (no clicks)
5. Auto-verifies LUFS/peak
6. Stops when within 0.3 LU of target
7. Logs to `output/master_consensus.jsonl`

**Output**: ONE thoroughly optimized WAV (`output/master_consensus.wav`)

**Goal**: High-quality, properly loud master (NOT the quiet -10.5 target)

**Alternative - 3 variants**:
```bash
flaas master-candidates  # Generates 3 different presets
```

**macOS Permissions Required** (one-time):
- System Settings → Privacy & Security → Accessibility → Terminal ON
- System Settings → Privacy & Security → Automation → Terminal → System Events ON

**Pre-requisites**:
- Ableton Live running with project open
- Export defaults set: Rendered Track = Master, Normalize = OFF
- Loop/selection set to desired range (4-8 bars)

**See usage guide**: `docs/reference/EXPERIMENT_RUNNER_USAGE.md`
