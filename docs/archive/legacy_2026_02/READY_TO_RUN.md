# READY TO RUN: Final Master Generation

**Status**: All code implemented, export determinism hardened ✅

---

## Step 1: Export Probe (30 seconds)

**Validates export goes to correct location**:

```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
./scripts/test_export_probe.sh
```

**What it does**:
- Triggers one export to `output/_probe.wav`
- Verifies file appears at expected absolute path
- Measures LUFS/peak (sanity check)
- Cleans up

**Expected**: "✅ PROBE TEST PASSED"

**If fails**: 
- Check debug output (enable with `export FLAAS_UI_EXPORT_DEBUG=1`)
- mdfind will show where file actually went
- Common issue: Ableton saved to ~/Documents instead of repo/output

---

## Step 2: Add Saturator (30 seconds)

**In Ableton**:
1. Open Master track
2. Add **Saturator** device
3. Position: AFTER Glue Compressor, BEFORE Limiter
4. **Chain order**: `Utility → EQ → Glue → Saturator → Limiter`
5. Verify Master fader = 0.0 dB

**Why Saturator**: Most efficient RMS boost (soft clip), raises loudness without harsh limiting

---

## Step 3: Final Master Run (5-15 minutes)

**Maximum loudness, fully automated**:

```bash
flaas master-consensus --mode loud_preview && echo "----" && ls -lh output/master_loud_preview.wav && echo "----" && tail -n 20 output/master_loud_preview.jsonl
```

**Target**: -9 LUFS, -2 dBTP (commercial competitive loudness)

**What happens**:
- Pre-flight checks (master fader, device order)
- Up to 15 iterations:
  - Set params via OSC
  - Auto-export via UI automation (zero clicks)
  - Verify LUFS/true peak
  - Adapt based on results
- Stops on: hit_target / max_iterations / diminishing_returns

**Output**: `output/master_loud_preview.wav` ← Your shippable master

---

## Step 4: Review Results

**Check terminal output**:
- Final LUFS-I value
- True Peak (dBTP)
- STOP_REASON (why it stopped)
- Iteration count

**Listen**: `output/master_loud_preview.wav`

**Expected**: LOUD, full, smooth (competitive with commercial releases)

---

## Decision Tree

**If sounds LOUD + GOOD**:
- ✅ Ship it
- ✅ Move to next track
- ✅ This is your first complete master via flaas

**If STOP_REASON = diminishing_returns**:
- Algorithm stopped to prevent artifacts (correct behavior)
- Check achieved LUFS (may be -10 to -11 if loop is sparse)
- If sounds good → ship it anyway (streaming normalizes)

**If still too quiet + STOP_REASON = hit_target**:
- Reached -9 LUFS but perception is quiet
- Check playback volume (system, headphones)
- Compare to commercial reference track

**If sounds harsh/distorted**:
- Try `--mode streaming_safe` (-14 LUFS, more conservative)
- Or manually reduce compression in Ableton

---

## Debug Checklist (If Export Probe Fails)

**Enable debug mode**:
```bash
export FLAAS_UI_EXPORT_DEBUG=1
./scripts/test_export_probe.sh
```

**Check**:
- [ ] Ableton Live running?
- [ ] macOS permissions granted (Accessibility, Automation)?
- [ ] Plugin windows closed (script tries to close them)?
- [ ] Export defaults set (Rendered Track=Master, Normalize=OFF)?
- [ ] mdfind output shows where file went (if not in output/)

**Common fixes**:
- Ableton export folder wrong → Set in File → Export → folder path
- Permissions missing → System Settings → Privacy & Security
- Plugin windows blocking → Close manually before running

---

## Summary

**Two commands**:
1. `./scripts/test_export_probe.sh` (validates export, 30s)
2. `flaas master-consensus --mode loud_preview` (final master, 5-15 min)

**After completion**: Listen, check STOP_REASON, ship if good.

**This is your final swing at maximum loudness without overdoing it.**

---

**Ready when you are.**
