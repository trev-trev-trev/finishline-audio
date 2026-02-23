# STATE

**Updated**: 2026-02-22 23:30 UTC  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## CURRENT TASK

**Stand Tall - Premium Master Generation** 🚧

**Project**: Stand Tall (111 tracks, V1/V2 element layers, vocals)

**Command**: `flaas master-premium --mode loud_preview`

**Chain**: Utility → EQ Eight → Waves C6 → F6 → SSL → Saturator → L3 UltraMaximizer

**Targets**:
- loud_preview: **-9 LUFS, -1 dBTP** (competitive commercial, default)
- streaming_safe: **-14 LUFS, -1 dBTP** (official Spotify spec)
- headroom: **-10 LUFS, -2 dBTP** (internal safety)

**Premium chain features**:
- ✅ Waves C6 multiband compression (55 params) - per-band threshold/gain/attack/range
- ✅ Waves SSL G-Master compression (13 params) - glue with analog character
- ✅ Waves L3 UltraMaximizer (8 params) - transparent limiting
- ✅ Stock Saturator (17 params) - harmonic RMS boost
- ⚠️ Waves F6 (1 param - Device On only) - static preset required

**Algorithm improvements**:
- ✅ True peak (dBTP) measurement (4x oversampling approximation)
- ✅ Diminishing returns detection (stops if LUFS improvement < 0.2 LU)
- ✅ Mode-based parameter presets (aggressive for loud_preview, gentle for streaming_safe)
- ✅ Adaptive convergence (15 iterations max, early stopping on target hit)
- ✅ Per-iteration JSONL logging (full parameter + metric history)

**Completed projects**:
- ✅ Life You Chose - `output/life_you_chose/master_loud_preview_iter1.wav` (-23.41 LUFS, user approved)

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

## NEXT ACTION

**Run Stand Tall premium master optimization**:

```bash
cd /Users/trev/Repos/finishline_audio_repo
./RUN_STAND_TALL_NOW.sh
```

**Or directly**:
```bash
flaas master-premium --mode loud_preview
```

**Pre-flight checklist (CRITICAL ORDER)**:

**Step 1: Vocal Processing (DO THIS FIRST)**
- [ ] VOCALS bus: Utility → Vocal Rider → Sibilance → F6 → R-Vox → Utility
- [ ] Chorus Features bus: Utility → F6 → DeEsser → S1 → R-Vox
- [ ] Reverb/Delay returns: EQ + sidechain ducking from VOCALS
- [ ] Test full track, fix extreme cases with clip gain
- **Why:** Master chain exaggerates vocal inconsistencies - fix at source first
- **See:** `STAND_TALL_VOCAL_SETUP.md` for complete guide

**Step 2: Master Chain Setup**
- [ ] Ableton: Stand Tall project open (111 tracks)
- [ ] Loop brace: 8-16 bars (include loud/quiet vocal sections)
- [ ] Master chain: Utility → EQ → C6 → F6 → SSL → Saturator → L3 (in order)
- [ ] F6 preset: Set manually (gentle 2-5 kHz cut or flat)
- [ ] Master fader: 0.0 dB (verify visually)
- [ ] All plugin windows closed
- [ ] Export defaults: Rendered Track = Master, Normalize = OFF
- [ ] Export folder: `/Users/trev/Repos/finishline_audio_repo/output`

**Expected runtime**: 30-60 minutes (5-15 iterations)

**Goal**: Generate premium Stand Tall master at -9.0 LUFS, -1.0 dBTP

**See**: `STAND_TALL_READY.md` for complete workflow guide

---

**Single source of truth for operational state. No redundant documentation.**
