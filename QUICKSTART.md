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

**Generate 3 master candidates** (zero clicks):
```bash
flaas master-candidates
```

**What happens**:
1. Iterative threshold search per candidate (up to 6 iterations each)
2. Auto-sets params (Glue, Limiter) via OSC
3. Auto-exports via macOS UI automation (no clicks)
4. Auto-verifies LUFS/peak
5. Logs to `output/master_candidates.jsonl`
6. Stops each candidate when targets hit

**Outputs**: 3 WAV files (consensus, variant_a, variant_b)

**Goal**: Generate 3 Spotify-ready masters from current 8-bar loop

**Alternative - Custom sweep**:
```bash
flaas experiment-run data/experiments/master_sweep.json
```

**macOS Permissions Required** (one-time):
- System Settings → Privacy & Security → Accessibility → Terminal ON
- System Settings → Privacy & Security → Automation → Terminal → System Events ON

**Pre-requisites**:
- Ableton Live running with project open
- Export defaults set: Rendered Track = Master, Normalize = OFF
- Loop/selection set to desired range (4-8 bars)

**See usage guide**: `docs/reference/EXPERIMENT_RUNNER_USAGE.md`
