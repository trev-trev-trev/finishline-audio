# Human Actions Required: Consensus Master Generation

**Goal**: Generate ONE high-quality, LOUD master from your 8-bar loop

**Modes Available**:
- `loud_preview` (default): -9 LUFS, -2 dBTP (competitive commercial, addresses "super quiet")
- `streaming_safe`: -14 LUFS, -1 dBTP (official Spotify spec, quieter)
- `headroom`: -10 LUFS, -6 dBFS (internal safety)

**Status**: All code implemented ✅ Ready to run

---

## ONE-TIME SETUP (Do Once)

### 1. macOS Permissions (Required for Auto-Export)

**System Settings → Privacy & Security → Accessibility**:
- ✅ Enable **Terminal** (or iTerm2 if you use that)

**System Settings → Privacy & Security → Automation**:
- ✅ Enable **Terminal → System Events**

**How to verify**: Run `./scripts/test_ui_export.sh` - should auto-export without prompts

---

## BEFORE EACH RUN

### 2. Ableton Live Setup (Required)

**Start Ableton**:
- ✅ Open your project (the one with the 8-bar loop you like)
- ✅ Ableton Live must be running and in focus initially

**Export defaults** (set once, persists):
1. File → Export Audio/Video
2. **Rendered Track** = Master (dropdown, critical)
3. **Normalize** = OFF (checkbox unchecked)
4. **Export folder** = `/Users/trev/Repos/finishline_audio_repo/output`
5. Cancel (don't export yet, just save these defaults)

**Loop/Selection**:
- ✅ Set Loop brace over your 8-bar section
- ✅ Verify loop plays the section you want to master

**Master Track Device Chain** (verify in Ableton):
- ✅ Track name: "Master" (or whatever it shows)
- ✅ Device order (left to right): `[Utility] → [EQ Eight] → [Glue Compressor] → [Limiter]`
- ✅ All devices ON (activator buttons lit)

**Master Fader**:
- ✅ Set Master track fader to **0.0 dB** (vertical slider on Master track)
- ✅ Verify visually (should be at center position)

---

## RUN THE COMMAND

### 3. Execute Master Candidates Generation

**Open terminal** (in repo directory):
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
flaas master-candidates
```

**What you'll see**:
1. Device resolution (finds Glue Compressor, Limiter)
2. Parameter resolution (queries all param info)
3. **Prompt**: "Press Enter to start candidate generation..."
4. **For each of 3 candidates** (CONSENSUS, VARIANT A, VARIANT B):
   - Sets fixed params (Makeup, Ratio, Attack, Limiter)
   - **Iterative threshold search** (up to 6 exports per candidate):
     - Sets threshold
     - Auto-triggers export (Ableton dialogs will flash, no clicks needed)
     - Waits for file to stabilize
     - Verifies LUFS/peak
     - Adjusts threshold if needed
     - Stops when targets hit
   - Prints results per iteration

**Expected duration**: 3-18 exports total (1-6 per candidate), ~3-10 minutes

**Interaction required**: 
- **ONE prompt at start**: "Press Enter to start" (after confirming Master fader 0.0)
- **Zero clicks during run** (auto-export handles everything)

---

## AFTER COMPLETION

### 4. Review Results

**Check output files**:
```bash
ls -lh output/master_*.wav
```

**Expected files**:
- `output/master_consensus.wav` (balanced, safest)
- `output/master_variant_a.wav` (controlled, clean)
- `output/master_variant_b.wav` (loud, forward)

**Check results log**:
```bash
tail -n 10 output/master_candidates.jsonl
```

**Or pretty-print**:
```bash
cat output/master_candidates.jsonl | jq .
```

**Expected**: Each candidate logged with LUFS, peak, pass flags, SHA256

### 5. Listen to Candidates

**Play each WAV** in your DAW or audio player:
1. `output/master_consensus.wav` - Balanced approach
2. `output/master_variant_a.wav` - More dynamic, cleaner
3. `output/master_variant_b.wav` - Louder, more compressed

**Listen for**:
- Smoothness (no harsh transients)
- Fullness (rich low-end, present mids)
- Loudness (competitive level, not distorted)
- Clarity (separation, definition)

**Pick your favorite** or note what to adjust

---

## TROUBLESHOOTING

### "Ableton Live not running" Error

**Fix**: Start Ableton Live, ensure project is open, try again

### "Device 'Glue Compressor' not found" Error

**Fix**: Check device names in Ableton Master track, ensure:
- Device exists and is named "Glue Compressor" (exact name)
- Device is ON (activator button lit)

**Alternative**: Edit `src/flaas/master_candidates.py` and update device names at top

### Export Dialogs Not Appearing

**Fix**: 
1. Check macOS permissions (Accessibility + Automation)
2. Ensure Ableton is frontmost before running
3. Try `./scripts/test_ui_export.sh` first (simpler test)

### "File did not appear or stabilize"

**Fix**:
- Check Export folder in Ableton = `/Users/trev/Repos/finishline_audio_repo/output`
- Check Rendered Track = Master (not "Selected Tracks Only")
- Ensure loop is set (not exporting entire project)

### Peak Failures (Peak > -6.00)

**Not critical**: Candidates that don't hit targets are still logged
- Listen to them anyway (may sound good even if peak slightly over)
- Algorithm will attempt to adjust limiter gain down on next iteration

### LUFS Too Low After 6 Iterations

**Expected**: Some candidates may not hit exact target (-10.50)
- This is OK! You have 3 candidates to choose from
- Pick closest to target or the one that sounds best
- Can manually adjust in Ableton if needed

---

## SUMMARY CHECKLIST

**One-time setup**:
- [ ] macOS Accessibility permission (Terminal)
- [ ] macOS Automation permission (Terminal → System Events)
- [ ] Ableton export defaults (Rendered Track = Master, Normalize = OFF, folder = output/)

**Before each run**:
- [ ] Ableton Live running with project open
- [ ] Loop/selection set to 8-bar section
- [ ] Master fader = 0.0 dB (CRITICAL - post-chain, defeats limiter if boosted)
- [ ] Master device chain: Utility → EQ → Glue Compressor → **Saturator** → Limiter (all ON)
  - **Saturator optional but recommended** (add for maximum loudness)

**DEFAULT (conservative, recommended first run)**:
```bash
cd /Users/trev/Repos/finishline_audio_repo && source .venv/bin/activate && flaas master-consensus
```
- Default mode: `streaming_safe` (-14 LUFS, -1 dBTP)
- Official Spotify recommendation
- Good baseline, avoids overcooking

**IF "super quiet" (use loud_preview mode)**:
```bash
flaas master-consensus --mode loud_preview
```
- Target: **LUFS -9.0, True Peak -2 dBTP** (competitive commercial)
- **Genre note**: Commercial releases vary (-8 to -12 LUFS depending on style)
- Pop/EDM: typically -8 to -9 LUFS
- Indie/acoustic: typically -10 to -14 LUFS
- **Use your ears** and watch for artifacts (distortion, pumping)

**What it does**:
- Generates ONE thoroughly optimized master
- Up to 15 iterations with adaptive adjustments
- **Pre-flight checks**: Verifies master fader (0.0 dB) and device order
- **3-stage processing**: Glue Compressor → Saturator (optional) → Limiter
- **Diminishing returns detection**: Stops pushing limiter when ineffective (< 0.2 LU improvement)
- **Adaptive strategy**: Prioritizes Saturator/compression over extreme limiter gain
- Stops when within 0.5 LU of target with safe true peak

**After completion**:
```bash
# If you ran default (streaming_safe):
ls -lh output/master_streaming_safe.wav
cat output/master_streaming_safe.jsonl | jq .

# If you ran loud_preview:
ls -lh output/master_loud_preview.wav
cat output/master_loud_preview.jsonl | jq .
```

**Other modes**:
```bash
flaas master-consensus --mode headroom  # -10 LUFS (moderate, internal safety)
```

---

---

## IF STILL TOO QUIET (Add Saturator First)

**Best solution**: Add Saturator to device chain (most efficient RMS boost)

### Add Saturator (Recommended)

**In Ableton**:
1. **Add Saturator** device to Master track
2. **Position**: AFTER Glue Compressor, BEFORE Limiter
3. **Chain order**: `[Utility] → [EQ] → [Glue Compressor] → [Saturator] → [Limiter]`
4. **Settings**:
   - Soft Clip = ON
   - Drive = 3-8 dB (start at 5 dB)
   - Dry/Wet = 100%
5. Run `flaas master-consensus --mode loud_preview` again

**Why Saturator**: Raises average level (RMS) more efficiently than extreme compression, smoother sound

### If STILL too quiet after Saturator

**Option 1: Use streaming_safe mode for reference**:
```bash
flaas master-consensus --mode streaming_safe  # -14 LUFS (quieter but official)
```
If this is also too quiet, issue is likely playback volume, not master

**Option 2: Check playback volume**:
- System volume control
- Headphone/speaker amp gain
- Compare to commercial reference track at same volume

**DO NOT**:
- ❌ Boost Master fader (it's post-chain, defeats limiter, breaks peak safety)
- ❌ Push limiter gain to max (diminishing returns, causes distortion)

---

**Next step**: Run `flaas master-consensus --mode loud_preview` and listen.
