# STATE

**Updated**: 2026-02-22 19:30 UTC  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## CURRENT TASK

**Master consensus generator CORRECTED** ✅

**Command**: `flaas master-consensus --mode loud_preview`

**Corrected targets** (per official Spotify docs):
- loud_preview: **-9 LUFS, -2 dBTP** (competitive commercial, default)
- streaming_safe: **-14 LUFS, -1 dBTP** (official Spotify spec)
- headroom: **-10 LUFS, -6 dBFS** (internal safety)

**Key fixes**:
- ✅ True peak (dBTP) measurement added (4x oversampling)
- ✅ Saturator support (optional, recommended for RMS boost)
- ✅ Diminishing returns detection (stops pushing limiter when < 0.2 LU improvement)
- ✅ Mode-based parameter presets (streaming_safe vs loud_preview vs headroom)
- ✅ 3-stage processing: Glue → Saturator → Limiter

**Previous errors corrected**:
- ❌ -8 LUFS is NOT "Spotify ceiling" (it's -14)
- ❌ -6 dBFS is internal safety, NOT streaming spec
- ❌ Master fader boost is WRONG (post-chain, defeats limiter)
- ❌ Limiter gain to max has diminishing returns

**Automation status**: 
- ✅ Parameter control (Glue, Saturator, Limiter) automated
- ✅ Export trigger automated (macOS UI automation via AppleScript)
- ✅ Verification automated (LUFS, sample peak, true peak)
- ✅ Logging automated (JSONL receipts)
- ⚠️ Master fader (manual pre-run check, no OSC endpoint)

**See**: 
- `docs/reference/STREAMING_STANDARDS.md` - Official platform specs
- `docs/reference/MASTERING_RECIPE.md` - Technical guide
- `docs/reference/EXPORT_FINDINGS.md` - Experiment findings
- `HUMAN_ACTIONS_REQUIRED.md` - Run checklist

---

## APPLIED STATE

**Master Track** (track_id=-1000):
- **Device chain**: Utility → EQ → Glue Compressor → **Saturator (recommended)** → Limiter
- **Master fader**: 0.0 dB (CRITICAL - post-chain, defeats limiter if boosted)

**Latest result** (from manual experiments):
- LUFS: -13.59 (too quiet for commercial)
- Peak: -6.00 dBFS
- Gap to target: 3.09 LU (if targeting -10.5)

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

### Smoke Tests
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

### Master Consensus (Corrected)
```bash
flaas master-consensus --mode loud_preview     # -9 LUFS, -2 dBTP (default, LOUD)
flaas master-consensus --mode streaming_safe   # -14 LUFS, -1 dBTP (official Spotify)
flaas master-consensus --mode headroom         # -10 LUFS, -6 dBFS (internal)
```

**Output**: `output/master_{mode}.wav`, `output/master_{mode}.jsonl`

---

## NEXT ACTION

**Run consensus master with corrected targets**:

```bash
flaas master-consensus --mode loud_preview
```

**Pre-flight**:
- [ ] Ableton Live running with project open
- [ ] Master fader = 0.0 dB (verify visually)
- [ ] Device chain: Utility → EQ → Glue → **Saturator** → Limiter
- [ ] Saturator added (if missing, command will warn but continue)
- [ ] Loop/selection = 8 bars
- [ ] Export folder = `/Users/trev/Repos/finishline_audio_repo/output`
- [ ] Export defaults: Rendered Track = Master, Normalize = OFF

**Goal**: Generate ONE LOUD master (competitive commercial loudness)

---

**Single source of truth for operational state. No redundant documentation.**
