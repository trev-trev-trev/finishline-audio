# QUICKSTART

**Repo**: `/Users/trev/Repos/finishline_audio_repo`

## Current Blocker

**Export crash** prevents closed-loop audio iteration loop.

**Loop**: `plan-gain → apply → export → verify-audio → repeat`

**Must fix before**: Endpoint expansion / command generation

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

# Master workflow (gain applied: -0.750)
flaas verify              # Check gain (returns 0.125000)
flaas plan-gain <wav>     # Calculate delta
flaas apply --actions <j> # Apply delta
```

## Next Action (Manual)

**In Ableton**:
1. Track 41: Disable ValhallaSpaceModulator (device 1)
2. Track 41: Disable StudioVerse (device 2)
3. Set loop brace to 4-8 bars
4. Export Master → Selection/Loop only → `output/master_iter1.wav`

**After export succeeds**:
```bash
flaas verify-audio output/master_iter1.wav
```
