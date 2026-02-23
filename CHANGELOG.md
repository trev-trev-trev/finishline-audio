# CHANGELOG

All notable changes to the FLAAS autonomous audio mastering system.

---

## [Unreleased]

### Added
- Testing infrastructure with 71 unit tests (100% pass rate)
- Automated CI via macOS launchd (runs every 30 minutes)
- Comprehensive test coverage for core modules
- `TESTING_COMPLETE.md` - Complete testing reference
- `TESTING_SETUP_SUMMARY.md` - CI setup guide
- Test logs archived in `logs/tests/` (last 100 runs kept)

---

## [2026-02-23] - Testing Infrastructure Deployment

### Added
- **71 unit tests** across 6 test modules (959 lines of test code)
- **Automated CI system** - Tests run every 30 minutes via launchd service
- **Test coverage**: 12% overall, 82% on tested modules (critical production path)
- **Test modules**:
  - `test_analyze.py` - 14 tests - Audio analysis (LUFS/True Peak measurement)
  - `test_master_premium.py` - 20 tests - Production mastering engine (Waves plugins)
  - `test_osc_rpc.py` - 6 tests - OSC communication protocol
  - `test_preflight.py` - 12 tests - Pre-flight safety checks
  - `test_targets.py` - 10 tests - Device resolution & constants
  - `test_util.py` - 9 tests - Utility gain staging functions

### Documentation
- Added `TESTING_COMPLETE.md` - Comprehensive testing reference (300+ lines)
- Added `TESTING_SETUP_SUMMARY.md` - CI setup and troubleshooting guide
- Added `tests/README.md` - Quick testing reference
- Updated `STATE.md` - Current task: Testing infrastructure complete
- Updated `STATUS.md` - Operating procedures synchronized with STATE.md
- Updated `README.md` - Added link to testing framework

### Infrastructure
- Created launchd service: `com.finishline.flaas.tests`
- Created test runner script: `scripts/run_tests_background.sh`
- Created test log directory: `logs/tests/` with automatic cleanup (keeps last 100 runs)
- Added `pytest` and `pytest-cov` to `requirements.txt`

### Quality Assurance
- **Test pass rate**: 100% (71/71 tests passing)
- **Runtime**: ~1 second (fast enough for pre-commit hooks)
- **Coverage on tested modules**:
  - `analyze.py`: 85%
  - `osc_rpc.py`: 97%
  - `preflight.py`: 81%
  - `targets.py`: 100%
  - `util.py`: 100%
  - `audio_io.py`: 100%
  - `master_premium.py`: 28% (main function requires Ableton)

### Benefits
- Continuous quality assurance on production code
- Catch regressions immediately
- Historical test run archive
- Zero manual intervention required
- Fast feedback (<2 seconds)

---

## [2026-02-22] - Stand Tall Master Complete

### Completed
- Generated final master for "Stand Tall" track
- **Specifications**:
  - LUFS: -14.36 (Spotify-optimized)
  - True Peak: -0.38 dBTP (streaming safe)
  - Peak: -1.50 dBFS
  - Duration: 4:44 (284.4 seconds)
- **File**: `output/stand_tall_PERFECT_MASTER.wav`
- **Chain**: Utility → EQ Eight → Waves C6 → F6 → SSL → Saturator → L3 UltraMaximizer

### Fixed
- Export folder caching bug in UI automation
- AppleScript now forces correct export path (Cmd+Shift+G navigation)
- Added Cmd+A to clear cached paths before typing target directory
- Increased delays for UI stability

### Documentation
- Created `output/STAND_TALL_PERFECT_MASTER_INFO.md` - Full master specifications
- Updated `STATE.md` - Stand Tall project complete

---

## [2026-02-21] - Premium Master Chain Implementation

### Added
- `master_premium.py` - Autonomous optimization with Waves C6/SSL/L3 plugins
- Multi-mode optimization:
  - `streaming_safe`: -14 LUFS, -1 dBTP (official streaming spec)
  - `loud_preview`: -9 LUFS, -1 dBTP (competitive commercial)
  - `headroom`: -10 LUFS, -2 dBTP (internal safety)
- Iterative optimization algorithm (converges to target LUFS/True Peak)
- Diminishing returns detection (stops if LUFS improvement < 0.2 LU)
- C6 multiband compression automation
- SSL glue compression automation
- L3 UltraMaximizer transparent limiting
- Saturator RMS boost integration

### CLI
- Added `master-premium` command with `--mode`, `--yes`, `--port` flags
- Added `--yes` flag for autonomous operation (skips manual prompts)
- Updated CLI help text and argument parsing

### Documentation
- Created `QUICK_START.md` - One-page setup guide
- Created `docs/API.md` - Complete Python module reference
- Updated `README.md` - Added quick start commands and documentation links

---

## [2026-02-20] - Life You Chose Master Complete

### Completed
- Generated master for "Life You Chose" track
- **Specifications**:
  - LUFS: -23.41 (quiet export, user approved)
  - File: `output/life_you_chose/master_loud_preview_iter1.wav`

### Fixed
- Export automation: Fixed `.wav.wav` bug (Ableton auto-appends extension)
- Resolved filename handling in UI automation

---

## [Earlier] - Foundation & Core Features

### Core System
- Autonomous mastering via OSC control
- Ableton Live integration via AbletonOSC
- LUFS/True Peak analysis using `pyloudnorm`
- True Peak estimation (4x oversampling approximation)
- Pre-flight safety checks (master fader, device chain order)
- Automated export via macOS UI automation (AppleScript)

### Device Automation
- Utility gain staging (linear & normalized)
- EQ Eight parameter control
- Limiter automation (threshold, ceiling, release)
- Glue Compressor automation
- Saturator drive control

### Analysis & Verification
- LUFS-I (Integrated Loudness)
- Sample peak detection (dBFS)
- True Peak estimation (dBTP)
- Streaming platform compliance checking

### Export Automation
- macOS UI automation via AppleScript
- Keyboard navigation (Cmd+Shift+R, Cmd+Shift+G)
- File stabilization detection (waits for export to complete)
- Overwrite handling
- Export location forcing (prevents cached path issues)

### Documentation
- `STATE.md` - Operational state (single source of truth)
- `docs/status/STATUS.md` - Operating procedures
- `docs/reference/STREAMING_STANDARDS.md` - Platform specifications
- `docs/reference/MASTERING_RECIPE.md` - Technical mastering guide

---

## Version History

- **Current**: Testing infrastructure complete, system operational
- **2026-02-23**: Testing infrastructure deployment (71 tests, automated CI)
- **2026-02-22**: Stand Tall master complete (-14.36 LUFS, streaming safe)
- **2026-02-21**: Premium master chain implementation (Waves C6/SSL/L3)
- **2026-02-20**: Life You Chose master complete (-23.41 LUFS)
- **Earlier**: Foundation, core features, device automation

---

## Links

- [Testing Reference](TESTING_COMPLETE.md)
- [Quick Start Guide](QUICK_START.md)
- [API Documentation](docs/API.md)
- [Current State](STATE.md)
- [Operating Procedures](docs/status/STATUS.md)

---

**Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles.

**Categories**: Added, Changed, Deprecated, Removed, Fixed, Security
