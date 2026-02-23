# FLAAS - Finishline Audio Automated System

**Autonomous audio mastering for Ableton Live.** OSC-controlled premium plugin automation with iterative LUFS/True Peak optimization.

## Quick Start

**One command → streaming-ready master in 30 minutes:**

```bash
flaas master-premium --mode loud_preview --yes --port 11000
```

Automatically optimizes Waves C6/SSL/L3 + Saturator to hit target loudness while ensuring True Peak < -1.0 dBTP for streaming safety.

**See [`QUICK_START.md`](QUICK_START.md) for setup guide.**

## Status

**Production-ready.** Masters generated:
- `Stand Tall`: -14.36 LUFS, -0.59 dBTP (Spotify-optimized) ✅
- `Life You Chose`: -23.41 LUFS (quiet export, user approved)

## Documentation

| File | Purpose |
|------|---------|
| **[`QUICK_START.md`](QUICK_START.md)** | 30-minute setup guide (start here) |
| **[`CHEATSHEET.md`](CHEATSHEET.md)** | **Quick reference** (all commands, one page) |
| [`SECURITY_AUDIT_REPORT.md`](SECURITY_AUDIT_REPORT.md) | Security compliance audit (24 findings) |
| [`tests/README.md`](tests/README.md) | Testing framework (71 tests, automated CI every 30 min) |
| [`STATE.md`](STATE.md) | Operational state & commands |
| [`docs/API.md`](docs/API.md) | Python API reference |
| [`docs/status/STATUS.md`](docs/status/STATUS.md) | Operating procedures |
| [`STAND_TALL_VOCAL_SETUP.md`](STAND_TALL_VOCAL_SETUP.md) | Vocal processing guide |

## Commands

```bash
# System Health
./scripts/health_check.sh                                        # Check all systems

# Mastering (autonomous)
flaas master-premium --mode loud_preview --yes --port 11000     # -9 LUFS (loud)
flaas master-premium --mode streaming_safe --yes --port 11000   # -14 LUFS (Spotify)

# Verification
flaas verify-audio output/your_master.wav                        # Basic analysis
python scripts/validate_streaming.py output/your_master.wav     # Single file validation
python scripts/batch_validate.py                                 # Batch validate all masters

# Development
make smoke       # Sanity check (7s)
make write-fast  # Dev gate (9s)
make write       # Commit gate (39s)
```

## Install

```bash
git clone <repo>
cd finishline_audio_repo
pip install -e .
```

**Requirements:**
- Python 3.11+
- Ableton Live 11.3+
- [AbletonOSC](https://github.com/ideoforms/AbletonOSC) remote script
- Waves plugins (C6, SSL, L3) for premium mastering

## Architecture

**Track Indexing (AbletonOSC):**
- Regular tracks: `0, 1, 2, ...`
- Return tracks: `-1, -2, -3, ...`
- Master track: `-1000`

**Core Modules:**
- `cli.py` - Command interface
- `master_premium.py` - Waves optimization engine
- `master_consensus.py` - Stock Ableton mastering
- `ui_export_macos.py` - UI automation for export
- `analyze.py` - LUFS/True Peak analysis
- `osc_rpc.py` - OSC request/response RPC

**See [`docs/architecture/`](docs/architecture/) for details.**
