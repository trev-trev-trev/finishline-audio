# START HERE

**Last updated**: 2026-02-22 19:40 UTC  
**Project**: Finishline Audio (flaas) - OSC control for Ableton Live

---

## IMMEDIATE ACTION (RIGHT NOW)

**Status**: Export determinism hardened ✅ Final master run ready

**Action**: Generate ONE shippable master at maximum competitive loudness

**See**: `READY_TO_RUN.md` ← Complete 3-step workflow (probe + master + review)

**Quick version**:
1. Run export probe (validates export goes to correct location): `./scripts/test_export_probe.sh`
2. Add Saturator to Master chain (if missing): `Glue → Saturator → Limiter`
3. Run final master: `flaas master-consensus --mode loud_preview`
4. Listen to `output/master_loud_preview.wav`
5. If LOUD + sounds good → ship it, move to next track

**Target**: -9 LUFS, -2 dBTP (commercial competitive loudness)

---

## KEY DOCUMENTATION (Priority Order)

1. **READY_TO_RUN.md** ← **START HERE** (3-step workflow: probe + master + review)
2. **STATE.md** - Current operational state (targets, invariants, commands)
3. **HUMAN_ACTIONS_REQUIRED.md** - Detailed run checklist + troubleshooting
4. **FINAL_MASTER_RUN.md** - Context on loudness targets + stop reasons
5. **docs/contracts/** - 4 permanent system contracts (canon rules):
   - `MEASUREMENT_CONTRACT.md` - LUFS/peak measurement rules
   - `EXPORT_CONTRACT.md` - Export correctness + proof tests
   - `MASTER_CHAIN_CONTRACT.md` - Device order + fader invariants
   - `SEARCH_CONTRACT.md` - Optimization algorithm structure
6. **docs/reference/STREAMING_STANDARDS.md** - Official platform specs (Spotify, Apple Music)
7. **docs/reference/MASTERING_RECIPE.md** - Technical guide (compression + saturation + limiting)

---

## Project Overview

**What is flaas?**
- Python CLI for controlling Ableton Live via OSC (Open Sound Control)
- Automated audio mastering optimization
- Closed-loop: set params → export → measure → adjust → repeat

**Current capability**:
- Automated master track processing (Glue Compressor + Saturator + Limiter)
- macOS UI automation for export (zero clicks)
- LUFS/peak measurement + true peak (dBTP)
- Iterative optimization with artifact guards

**Goal**: Generate commercial-quality masters programmatically

---

## What Just Happened (Context)

**User feedback**: "Sounds incredible, just needs to be LOUDER"

**Root cause**: LUFS target too conservative (-10.5, then -14)

**Solution**: `--mode loud_preview` targets -9 LUFS (commercial competitive)

**Export bug**: Fixed determinism (files went to wrong location)
- Now: Absolute paths + UI hardening + mdfind search
- Export probe test validates this before full run

**Corrections applied** (per user/ChatGPT feedback):
- ✅ Spotify official spec is -14 LUFS (NOT -8)
- ✅ True peak (dBTP) required (NOT just sample peak)
- ✅ Master fader is post-chain (must be 0.0 dB)
- ✅ Limiter alone has diminishing returns
- ✅ Saturator + compression more efficient than extreme limiting
- ✅ Added pre-flight checks (fail fast on misconfiguration)

---

## Smoke Tests (Development)

```bash
make smoke       # 7s, read-only, fast sanity
make write-fast  # 9s, dev loop gate
make write       # 39s, pre-commit gate (includes plugin test)
```

**Exit codes**: 0 (pass), 10 (skip), 20 (read fail), 30 (write fail)

---

## Next Chapter (After This Master)

**Once first master shipped**:
- Systematic control discovery (300-500 OSC endpoints)
- Per-track plugin control
- Stem export automation
- Multi-track mastering

**Blocked on**: Completing first master (gating milestone)

**See**: `DISCOVERY.md`, `NEXT_CHAPTER.md` for research plan

---

## Quick Reference

**Commands**:
```bash
# Smoke tests
make smoke / make write-fast / make write

# Audio verification
flaas verify-audio <wav>  # LUFS-I, sample peak, true peak

# Master consensus (3 modes)
flaas master-consensus --mode loud_preview     # -9 LUFS (competitive, LOUD)
flaas master-consensus --mode streaming_safe   # -14 LUFS (official Spotify)
flaas master-consensus --mode headroom         # -10 LUFS (internal safety)
```

**Repo**: `/Users/trev/Repos/finishline_audio_repo`

**AbletonOSC version expected**: `0.3.14`

**Python**: 3.11+ required

---

**Ready to run. See READY_TO_RUN.md for 3-step workflow.**
