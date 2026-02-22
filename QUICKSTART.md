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

# Semi-automated experiments (NEW)
flaas experiment-run <config.json>  # Batch parameter sweep
```

## Next Action (Fully Automated)

**Run batch experiment** (3 runs, no manual clicks):
```bash
flaas experiment-run data/experiments/master_sweep.json
```

**What happens**:
1. Auto-sets params (Glue, Limiter) via OSC
2. Auto-exports via macOS UI automation (no clicks)
3. Auto-verifies LUFS/peak
4. Logs to `output/experiments.jsonl`
5. Early exit on success

**Config**: GR 12-18 dB, Makeup 15-20 dB, Limiter 28-32 dB

**Goal**: Close 3.09 LU gap (-13.59 → -10.50)

**macOS Permissions Required** (one-time):
- System Settings → Privacy & Security → Accessibility → Terminal ON
- System Settings → Privacy & Security → Automation → Terminal → System Events ON

**Pre-requisites**:
- Ableton Live running with project open
- Export defaults set: Rendered Track = Master, Normalize = OFF
- Loop/selection set to desired range (4-8 bars)

**See usage guide**: `docs/reference/EXPERIMENT_RUNNER_USAGE.md`
