# Quick Start - Autonomous Mastering

**Get a streaming-ready master in ~30 minutes with one command.**

---

## Prerequisites (One-Time Setup)

### 1. Ableton Project Setup
- [ ] Open your song in Ableton Live
- [ ] Set loop brace over 8-16 bars (include dynamic sections)
- [ ] **Master fader = 0.0 dB** (critical!)
- [ ] Close all plugin windows

### 2. Master Chain (in this exact order)
Add these devices to your Master track:

1. **Utility** (pre-gain staging)
2. **EQ Eight** (corrective EQ)
3. **Waves C6 Stereo** (multiband compression)
4. **Waves F6 Stereo** (dynamic EQ - set static preset manually)
5. **Waves SSLComp Stereo** (glue compression)
6. **Saturator** (harmonic richness)
7. **Waves L3 UltraMaximizer Stereo** (final limiting)

### 3. Export Settings
- File → Export Audio/Video (configure once, Ableton remembers):
  - **Rendered Track** = Master
  - **Normalize** = OFF
  - **File Type** = WAV
  - **Export folder** = `/Users/trev/Repos/finishline_audio_repo/output`
- Click Cancel (just setting defaults)

---

## Run Optimization

```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
flaas master-premium --mode loud_preview --yes --port 11000
```

**Wait ~30 minutes** while it:
- Runs pre-flight checks
- Sets C6, SSL, Saturator, L3 parameters via OSC
- Exports iteration 1
- Analyzes LUFS & True Peak
- Adjusts parameters and re-exports (up to 15 iterations)
- Stops when target reached or diminishing returns detected

---

## Modes

```bash
# LOUD (competitive commercial) - default
flaas master-premium --mode loud_preview --yes --port 11000
# Target: -9 LUFS, -1 dBTP

# Spotify-optimized (conservative)
flaas master-premium --mode streaming_safe --yes --port 11000
# Target: -14 LUFS, -1 dBTP

# Internal preview (extra headroom)
flaas master-premium --mode headroom --yes --port 11000
# Target: -10 LUFS, -2 dBTP
```

---

## Output Files

After completion, check `output/`:
- `<songname>_premium_iter1.wav` through `iterN.wav` - all iterations
- `<songname>_premium_<mode>.jsonl` - full optimization log (params + metrics)

**Pick the best iteration** (usually the one closest to target without overs).

---

## Troubleshooting

### "Pre-flight checks failed"
- **Master fader not 0.0 dB**: Set to 0.0 in Ableton, re-run
- **Device order wrong**: Verify chain matches order above
- **OSC timeout**: Restart Ableton Live, re-run

### "Export file did not appear"
- **Wrong export folder**: Check Ableton's last export location (File → Export)
  - If wrong, manually set to `output/` folder, click Cancel, re-run
- **Ableton hung**: Check Activity Monitor, kill if "Not Responding"
- **Plugin authorization**: Check for popup dialogs in Ableton

### "True Peak OVER limit"
- Normal! Optimization backs off limiter and re-tries
- If persistent after 5+ iterations, vocals might be clipping (check pre-master processing)

### Optimization is too quiet
- Check vocal levels (use `flaas verify-audio output/<file>.wav`)
- If vocals have extreme dynamics (30+ dB range), apply vocal processing first:
  - See `STAND_TALL_VOCAL_SETUP.md` for 3-layer leveling model

---

## Advanced

### Manual parameter control
If you want specific settings without iteration:

```bash
# Disable auto-export, set parameters manually
flaas master-premium --mode loud_preview --no-auto-export --yes --port 11000
```

Then manually export from Ableton and verify:
```bash
flaas verify-audio output/your_export.wav
```

### Debug mode
```bash
FLAAS_UI_EXPORT_DEBUG=1 flaas master-premium --mode loud_preview --yes --port 11000
```

Shows detailed AppleScript execution logs.

---

## What's Happening Under the Hood

1. **Pre-flight**: Verifies master fader (0.0 dB) and device chain order
2. **Device resolution**: Finds Utility, C6, SSL, Saturator, L3 by name via OSC
3. **Parameter mapping**: Reads min/max ranges for each device parameter
4. **Iteration loop** (up to 15):
   - Set parameters (C6 thresholds, SSL makeup, Saturator drive, L3 threshold)
   - Trigger export via macOS UI automation (Cmd+Shift+R → Save)
   - Wait for WAV to appear and stabilize
   - Analyze LUFS, Peak, True Peak
   - Compare to target (mode-dependent)
   - If True Peak over: reduce L3 intensity
   - If LUFS under target: increase SSL/Saturator/C6
   - If LUFS over target: reduce SSL/Saturator
   - Stop if: target hit, diminishing returns, or max iterations
5. **Logging**: Write full parameter + metric history to JSONL

---

## Examples

### Completed Projects
- **Life You Chose**: `-23.41 LUFS` (user approved, quiet export)
- **Stand Tall**: `-14.36 LUFS, -0.59 dBTP` (Spotify-optimized, streaming safe)

### Typical Results
- **Iteration 1**: Usually -14 to -16 LUFS (starting conservative)
- **Iteration 5-8**: Converging to target (-9 to -11 LUFS)
- **Final**: Within 0.5 LU of target, True Peak < -1.0 dBTP

---

**That's it!** One command, 30 minutes, streaming-ready master. 🎉
