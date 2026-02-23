# FLAAS - Finishline Audio Automated System

**Autonomous audio mastering for Ableton Live** - OSC-controlled Waves plugin automation with iterative LUFS/True Peak optimization.

## What It Does

**One command. 30 minutes. Streaming-ready master.**

```bash
flaas master-premium --mode loud_preview --yes --port 11000
```

Automatically:
- ✅ Controls Waves C6, SSL, L3 + Ableton Saturator via OSC
- ✅ Exports iterations via UI automation
- ✅ Analyzes LUFS, Peak, True Peak
- ✅ Converges to target loudness (-9, -11, or -14 LUFS)
- ✅ Ensures streaming safety (True Peak < -1.0 dBTP)
- ✅ Logs full parameter + metric history

## Status

**Production-ready.** 2 songs mastered:
- Life You Chose: -23.41 LUFS (user approved)
- Stand Tall: -14.36 LUFS, -0.59 dBTP ✅ (Spotify-optimized)

See `STATE.md` for details.

## Documentation

- **`QUICK_START.md`** - Get your first master in 30 min (start here!)
- `STATE.md` - Current operational state (load this first in new sessions)
- `docs/status/STATUS.md` - Operating procedures and contract
- `docs/reference/EXPORT_FINDINGS.md` - Export automation experiments
- `STAND_TALL_VOCAL_SETUP.md` - Vocal processing workflow (3-layer leveling)

## Quick Commands

### Mastering
```bash
# Autonomous optimization (recommended)
flaas master-premium --mode loud_preview --yes --port 11000  # -9 LUFS target
flaas master-premium --mode streaming_safe --yes --port 11000  # -14 LUFS (Spotify)

# Analyze results
flaas verify-audio output/your_master.wav
```

### Development
```bash
make smoke       # Fast sanity check (7s, read-only)
make write-fast  # Dev loop gate (9s, write tests)
make write       # Pre-commit gate (39s, full suite)
```

## Track Indexing

- Regular tracks: 0, 1, 2, ...
- Return tracks: -1, -2, -3, ...
- **Master track: -1000**

## Install

```bash
pip install -e .
```

## Requirements

- Python 3.11+
- Ableton Live 11.3+
- AbletonOSC remote script
