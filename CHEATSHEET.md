# FLAAS Quick Reference

**Single-page command reference for autonomous audio mastering**

---

## System Health

```bash
./scripts/health_check.sh              # Verify all systems operational
```

---

## Mastering Workflows

### Quick Master (30 minutes, fully autonomous)

```bash
# 1. Open project in Ableton, start AbletonOSC
# 2. Run mastering
flaas master-premium --mode streaming_safe --yes --port 11000

# 3. Verify result
flaas verify-audio output/track_master.wav
```

### Mastering Modes

| Mode | Target LUFS | Use Case | Command |
|------|-------------|----------|---------|
| `streaming_safe` | -14 | Spotify/Apple Music | `--mode streaming_safe` |
| `loud_preview` | -9 | Loud preview/club | `--mode loud_preview` |
| `headroom` | -16 | Conservative/classical | `--mode headroom` |

### Common Flags

```bash
--yes              # Skip all confirmations (fully autonomous)
--port 11000       # OSC port (default: 11000)
--no-export        # Skip auto-export after mastering
```

---

## Audio Verification

```bash
# Analyze any WAV file
flaas verify-audio path/to/file.wav

# Expected output:
# - LUFS (integrated loudness)
# - True Peak (dBTP, must be < -1.0 for streaming)
# - Duration, sample rate, channels
```

---

## Testing

```bash
# Quick run (all 71 tests, ~1s)
python -m pytest tests/ -q

# Verbose output with coverage
python -m pytest tests/ -v --cov=src/flaas --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_master_premium.py -v

# View latest automated test results
cat logs/tests/latest.log
```

### Automated Testing

Tests run **every 30 minutes** in background via launchd:

```bash
# Check service status
launchctl list | grep com.finishline.flaas.tests

# Manually trigger test run
./scripts/run_tests_background.sh

# View recent logs
ls -lt logs/tests/
```

---

## Development Workflow

### Pre-Commit Checks

```bash
make smoke         # Quick sanity (7s) - format, type hints, smoke test
make write-fast    # Dev gate (9s) - above + import order
make write         # Full gate (39s) - all checks + full test suite
```

### Git Workflow

```bash
git status                              # Check changes
git add -A                              # Stage all
git commit -m "Description"             # Commit
git push origin main                    # Push to remote
```

---

## File Locations

### Input/Output

| Path | Contents |
|------|----------|
| `output/` | Exported masters (WAV files) |
| `output/stand_tall_PERFECT_MASTER.wav` | Completed "Stand Tall" master |
| `output/life_you_chose/` | "Life You Chose" project files |

### Logs

| Path | Contents |
|------|----------|
| `logs/tests/` | Automated test run logs |
| `logs/tests/latest.log` | Most recent test results |
| `data/reports/` | Smoke test results |

### Documentation

| File | Purpose |
|------|---------|
| `QUICK_START.md` | 30-minute setup guide |
| `STATE.md` | Operational state & system status |
| `CHEATSHEET.md` | This file (quick reference) |
| `tests/README.md` | Testing framework guide |
| `docs/API.md` | Python API reference |

---

## Troubleshooting

### OSC Connection Issues

```bash
# 1. Verify AbletonOSC is running in Ableton
# 2. Check port (default 11000):
flaas master-premium --port 11000

# 3. Test OSC connectivity:
# Open Python REPL:
python
>>> from flaas.osc_rpc import request_once
>>> request_once("/live/test", port=11000)
# Should return response tuple
```

### Master Fader Not at 0dB

```bash
# Error: "Master fader must be at 0dB"
# Fix: In Ableton, reset master fader to 0dB (unity gain)
```

### True Peak Clipping (> -1.0 dBTP)

```bash
# If master exceeds -1.0 dBTP:
# 1. Re-run with more conservative mode:
flaas master-premium --mode headroom --yes

# 2. Or manually adjust L3 "Out Ceiling" to -1.5 dB in Ableton
```

### Tests Failing

```bash
# 1. Check which tests failed:
python -m pytest tests/ -v

# 2. Check linter errors:
make smoke

# 3. View detailed error output:
python -m pytest tests/test_module.py -vv
```

---

## Plugin Chain (Master Track)

**Required order for `master-premium`:**

1. **Waves C6** - Multiband compressor
2. **Waves SSL G-Master Buss Compressor** - Glue compression
3. **Ableton Saturator** - Harmonic saturation
4. **Waves L3 Multimaximizer** - Limiter/maximizer

*Autonomous mastering configures all parameters automatically*

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Test Coverage | 71 tests across 6 modules |
| Automated CI | Every 30 minutes |
| Completed Masters | 2 (Stand Tall, Life You Chose) |
| Documentation Files | 8 markdown files |
| Average Master Time | 30 minutes |

---

## One-Liners

```bash
# Full health check + master + verify
./scripts/health_check.sh && flaas master-premium --mode streaming_safe --yes && flaas verify-audio output/*.wav | tail -20

# Run tests + commit if passing
python -m pytest tests/ -q && git add -A && git commit -m "Update" && git push

# Find latest master
ls -lt output/*.wav | head -1

# Check automated test schedule
launchctl list | grep flaas && cat logs/tests/latest.log | grep "passed"
```

---

## Emergency Commands

```bash
# Kill stuck Ableton export
pkill -f "osascript.*Ableton"

# Restart launchd test service
launchctl unload ~/Library/LaunchAgents/com.finishline.flaas.tests.plist
launchctl load ~/Library/LaunchAgents/com.finishline.flaas.tests.plist

# Clean all logs
rm logs/tests/*.log

# Reset virtual environment
rm -rf .venv && python -m venv .venv && source .venv/bin/activate && pip install -e .
```

---

**For detailed guides, see [`QUICK_START.md`](QUICK_START.md) or [`docs/status/STATUS.md`](docs/status/STATUS.md)**
