# FLAAS - Finishline Audio Automated System

Control Ableton Live via OSC for automated audio processing workflows.

## Status

**Current**: Troubleshooting export crash. See `STATE.md`.

## Documentation

- `STATE.md` - Current operational state
- `QUICKSTART.md` - Quick reference
- `docs/status/STATUS.md` - Operating procedures

## Quick Commands

```bash
make smoke       # Fast sanity check
make write-fast  # Dev loop gate
make write       # Pre-commit gate
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
