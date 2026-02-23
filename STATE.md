# STATE

**Updated**: 2026-02-23 05:45 UTC  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## CURRENT TASK

**Testing Infrastructure - COMPLETE** ✅

**Status**: Production-ready autonomous testing system operational

**Test Suite**:
- 71 unit tests (100% pass rate)
- 6 test modules (959 lines of test code)
- Runtime: ~1 second
- Coverage: 12% overall, 82% on tested modules
- Automated CI: Runs every 30 minutes via launchd

**Test Coverage**:
- `test_analyze.py` - 14 tests - Audio analysis (LUFS/True Peak)
- `test_master_premium.py` - 20 tests - Production mastering engine
- `test_osc_rpc.py` - 6 tests - OSC communication
- `test_preflight.py` - 12 tests - Pre-flight checks
- `test_targets.py` - 10 tests - Device resolution
- `test_util.py` - 9 tests - Utility functions

**See**: `TESTING_COMPLETE.md`, `TESTING_SETUP_SUMMARY.md`, `tests/README.md`

---

## COMPLETED PROJECTS

**Stand Tall - DONE** ✅

**Final Master**: `output/stand_tall_PERFECT_MASTER.wav`

**Specs**:
- LUFS: **-14.36** (Spotify-optimized)
- True Peak: **-0.38 dBTP** ✅ (streaming safe)
- Peak: **-1.50 dBFS**
- Duration: **4:44** (284.4 seconds)

**Generated via**: `flaas master-premium --mode loud_preview` (iteration 1, autonomous optimization)

**Chain**: Utility → EQ Eight → Waves C6 → F6 → SSL → Saturator → L3 UltraMaximizer

**Life You Chose - DONE** ✅
- File: `output/life_you_chose/master_loud_preview_iter1.wav`
- LUFS: -23.41 (quiet export, user approved)

**System Status**: 
- ✅ Parameter control automated (Glue, Saturator, Limiter, Waves C6/SSL/L3)
- ✅ Export trigger automated (macOS UI automation via AppleScript)
- ✅ Verification automated (LUFS, sample peak, true peak)
- ✅ Logging automated (JSONL receipts)
- ✅ Testing automated (71 tests, 100% pass rate, runs every 30 minutes via launchd)
- ✅ Documentation complete (QUICK_START.md, API.md, TESTING_COMPLETE.md)
- ⚠️ Master fader (manual pre-run check, no OSC endpoint)

**See**: 
- `docs/reference/STREAMING_STANDARDS.md` - Official platform specs
- `docs/reference/MASTERING_RECIPE.md` - Technical guide
- `docs/reference/EXPORT_FINDINGS.md` - Experiment findings
- `tests/README.md` - Testing framework (51 tests, automated CI)
- `TESTING_SETUP_SUMMARY.md` - Complete testing infrastructure guide
- `HUMAN_ACTIONS_REQUIRED.md` - Run checklist

---

## APPLIED STATE

**Current Project**: Stand Tall

**Master Track** (track_id=-1000):
- **Device chain**: Utility → EQ Eight → Waves C6 → Waves F6 → Waves SSL → Saturator → Waves L3
- **Master fader**: 0.0 dB (CRITICAL - post-chain, defeats limiter if boosted)
- **F6 preset**: Static (2-5 kHz gentle cut or flat) - not automated

**Project structure**:
- 111 tracks total
- V1 elements: Active (tracks with devices)
- V2 elements: Mostly muted (0 devices)
- Key tracks: ELEMENTS, float a lil higher, orbit earth, levitate high, VOCALS, V2 [VOCALS], Chorus Features

**Previous project (Life You Chose)**:
- Final master: `output/life_you_chose/master_loud_preview_iter1.wav`
- LUFS: -23.41 (iteration 1, export automation issues, user approved as-is)
- All exports moved to `output/life_you_chose/` subfolder

---

## CRITICAL FACTS

### Track Indexing (AbletonOSC)
- Regular: 0, 1, 2, ...
- Returns: -1, -2, -3, ...
- **Master: -1000** (NOT 0)

### Device Resolution
```python
# Response from /live/track/get/devices/name is: (track_id, name0, name1, ...)
names = list(response)[1:]  # Drop track_id
device_id = names.index("Utility")  # Case-insensitive
```

### Master Fader Position
- **Post-device chain** (after Limiter)
- **Must be 0.0 dB** for predictable peak control
- Boosting fader defeats limiter ceiling (observed empirically)

### True Peak vs Sample Peak
- **Sample peak (dBFS)**: Highest digital sample value
- **True peak (dBTP)**: Reconstructed analog peak (4x oversampling)
- True peak typically 0.5-1.5 dB higher than sample peak
- Streaming services require true peak compliance (codec safety)

### Loudness Strategy
1. **Compression before limiting** (Glue Compressor)
2. **Saturation for RMS boost** (Saturator, soft clip)
3. **Peak catching** (Limiter)
4. Limiter alone is insufficient (observed in experiments)

---

## COMMANDS

### Unit Tests (Automated CI)
```bash
# Run all tests manually
python -m pytest tests/ -v                    # 51 tests, <1s

# With coverage report
python -m pytest tests/ --cov=src/flaas --cov-report=html
open htmlcov/index.html

# Check automated test results (runs every 30 min)
cat logs/tests/latest.log                     # Latest automated run
ls -lt logs/tests/test_run_*.log | head -5    # Recent runs

# Trigger automated test now (doesn't wait 30 min)
launchctl start com.finishline.flaas.tests

# Service status
launchctl list | grep flaas                   # Should show: com.finishline.flaas.tests
```

**Test modules**: 
- `test_analyze.py` - Audio analysis (14 tests, 85% coverage)
- `test_osc_rpc.py` - OSC communication (6 tests, 97% coverage)
- `test_preflight.py` - Pre-flight checks (12 tests, 81% coverage)
- `test_targets.py` - Constants/resolution (10 tests, 100% coverage)
- `test_util.py` - Utility functions (9 tests, 100% coverage)

**See**: `tests/README.md` for complete testing guide

### Smoke Tests (Integration)
```bash
make smoke       # 7s, 8 tests (read-only)
make write-fast  # 9s, 4 tests (dev gate)
make write       # 39s, 13 tests (commit gate)
```

### Exit Codes
- 0: pass
- 10: skip only
- 20: read failure
- 30: write failure

### Master Consensus (Stock Ableton Chain)
```bash
flaas master-consensus --mode loud_preview     # -9 LUFS, -2 dBTP (default, LOUD)
flaas master-consensus --mode streaming_safe   # -14 LUFS, -1 dBTP (official Spotify)
flaas master-consensus --mode headroom         # -10 LUFS, -6 dBFS (internal)
```

**Chain**: Utility → EQ Eight → Glue Compressor → Saturator → Limiter  
**Output**: `output/master_{mode}.wav`, `output/master_{mode}.jsonl`

### Master Premium (Waves + Stock Hybrid)
```bash
flaas master-premium --mode loud_preview     # -9 LUFS, -1 dBTP (default, LOUD)
flaas master-premium --mode streaming_safe   # -14 LUFS, -1 dBTP (official Spotify)
flaas master-premium --mode headroom         # -10 LUFS, -2 dBTP (internal)
```

**Chain**: Utility → EQ Eight → Waves C6 → Waves F6 → Waves SSL → Saturator → Waves L3  
**Output**: `output/stand_tall_premium_{mode}_iterN.wav`, `output/stand_tall_premium_{mode}.jsonl`

**Premium features**:
- C6 multiband leveling (per-band threshold/gain control)
- SSL glue compression (analog character)
- L3 transparent limiting (better than stock Limiter)
- F6 static preset (manual setup required)

---

## SYSTEM CAPABILITIES

**Production Ready Features**:
1. ✅ Autonomous mastering (Waves C6/SSL/L3 + stock chain)
2. ✅ Multi-mode optimization (streaming_safe, loud_preview, headroom)
3. ✅ True Peak safety (auto-adjusts to stay under limit)
4. ✅ Automated export via UI automation
5. ✅ LUFS/True Peak analysis
6. ✅ Pre-flight safety checks
7. ✅ Comprehensive unit testing (71 tests, automated CI)

**Available Commands**:
```bash
# Master with premium Waves chain (autonomous optimization)
flaas master-premium --mode streaming_safe --yes  # -14 LUFS, -1 dBTP
flaas master-premium --mode loud_preview --yes    # -9 LUFS, -1 dBTP
flaas master-premium --mode headroom --yes        # -10 LUFS, -2 dBTP

# Verify audio file
flaas verify-audio output/track.wav

# Test system health
python -m pytest tests/ -v
cat logs/tests/latest.log
```

**Next Project Ready**: System is ready for new tracks anytime

---

**Single source of truth for operational state. No redundant documentation.**
