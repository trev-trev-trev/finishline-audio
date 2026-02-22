# FINAL MASTER RUN

**Date**: 2026-02-22  
**Goal**: Generate ONE shippable master at maximum competitive loudness

---

## User Feedback

> "It sounds incredible, it just needs to be LOUDER. Whatever the loudest you can get on Spotify is."

**Translation**: Chain works perfectly, LUFS target too conservative

**Solution**: `--mode loud_preview` (-9 LUFS, -2 dBTP)

---

## The Command

```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

# Ensure Saturator is in Master chain (if missing, add it):
# Chain: Utility → EQ → Glue Compressor → Saturator → Limiter

flaas master-consensus --mode loud_preview
```

**Output**: `output/master_loud_preview.wav`

---

## What This Does

**Target**: -9 LUFS (commercial competitive loudness)
- This is **as loud as you should go** without artifacts
- Matches pop/EDM commercial releases
- Spotify will normalize DOWN to -14, but initial perception is LOUD

**True peak**: -2 dBTP (codec safe)
- Prevents distortion during MP3/AAC encoding
- Conservative enough for loud masters

**Optimization**:
- Up to 15 iterations
- Adaptive adjustments (compression → saturation → limiting)
- Diminishing returns detection (stops when ineffective)
- Pre-flight checks (verifies fader, device order)

---

## Pre-Flight Checklist (Critical)

**In Ableton**:
- [ ] Ableton Live running with project open
- [ ] Master fader = **0.0 dB** (verify visually - post-chain, critical)
- [ ] Device chain: Utility → EQ → **Glue Compressor** → **Saturator** → **Limiter** (all ON)
- [ ] Saturator added (if missing - highly recommended for max loudness)
- [ ] Loop/selection = 8 bars (or full song if ready)
- [ ] Export defaults: Rendered Track = **Master**, Normalize = **OFF**
- [ ] Export folder = `/Users/trev/Repos/finishline_audio_repo/output`

**macOS permissions** (one-time):
- [ ] System Settings → Privacy & Security → Accessibility → Terminal ON
- [ ] System Settings → Privacy & Security → Automation → Terminal → System Events ON

---

## Expected Result

**LUFS**: ≈ -9.0 (±0.5 LU)

**True Peak**: ≤ -2.0 dBTP (codec safe)

**Perception**: LOUD, full, competitive

**Comparison**: Should match commercial pop/EDM releases in perceived loudness

---

## After Completion

**Verify**:
```bash
ls -lh output/master_loud_preview.wav
cat output/master_loud_preview.jsonl | jq .
```

**Listen**: `output/master_loud_preview.wav` in your DAW or audio player

**Compare**: Play alongside a commercial reference track (same genre) at same volume

---

## Decision Tree

**If result sounds LOUD and GOOD**:
- ✅ Ship it
- ✅ Move to next track
- ✅ Consider this master "done" (per flaas algorithm v1)

**If still too quiet** (unlikely):
- Check playback volume (system, headphones)
- Verify Saturator is in chain
- See "IF STILL TOO QUIET" section in `HUMAN_ACTIONS_REQUIRED.md`

**If sounds harsh/distorted**:
- You may have exceeded artifact threshold
- Try `--mode streaming_safe` (-14 LUFS, more conservative)
- Or manually adjust in Ableton (reduce compression)

**If needs more character** (warmth, analog feel):
- Current master is shippable
- Consider Waves plugin swap as enhancement (see `docs/reference/PREMIUM_PLUGINS.md`)

---

## Bottom Line

**This is your final swing at maximum loudness**:
- Loudest target: -9 LUFS (without overdoing it)
- Best RMS boost: Saturator + Glue + Limiter
- Maximum iterations: 15 (thorough convergence)
- Adaptive algorithm: Prioritizes density over limiting

**After this run**: You have a shippable master. Premium plugins are enhancement, not requirement.

---

**Run it. Listen. If it's LOUD and sounds incredible, you're done.**
