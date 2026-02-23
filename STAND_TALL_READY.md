# 🎚️ STAND TALL - READY TO RUN

## ⚡ QUICK START (3 Steps)

### 1. **Vocal Processing Setup** (15-30 min) - DO THIS FIRST!

**CRITICAL:** Fix vocal levels at source before mastering.

Follow complete guide: `STAND_TALL_VOCAL_SETUP.md`

**Quick checklist:**
- [ ] VOCALS bus: Utility → Vocal Rider → Sibilance → F6 → R-Vox → Utility
- [ ] Chorus Features bus: Utility → F6 → DeEsser → S1 → R-Vox
- [ ] Reverb/Delay returns: EQ + sidechain ducking from VOCALS
- [ ] Test full track, fix extreme cases with clip gain

**Why:** Master chain (C6/SSL/L3) will exaggerate vocal inconsistencies. Level vocals first = cleaner master.

---

### 2. **Final Ableton Prep** (2 min)

In Ableton Live:
- ✅ Stand Tall project open
- ✅ Vocal processing complete (see step 1)
- ✅ Loop brace set over section to master (8-16 bars with loud/quiet vocal variation)
- ✅ Master chain devices in order:
  1. Utility
  2. EQ Eight
  3. Waves C6 Stereo
  4. Waves F6 Stereo (set a preset: gentle 2-5 kHz cut, or leave flat)
  5. Waves SSLComp Stereo
  6. Saturator
  7. Waves L3 UltraMaximizer Stereo
- ✅ Master fader = **0.0 dB**
- ✅ All plugin windows closed
- ✅ Export defaults confirmed (File → Export Audio/Video → Cancel):
  - Rendered Track = **Master**
  - Normalize = **OFF**
  - File Type = **WAV**
  - Export folder = `/Users/trev/Repos/finishline_audio_repo/output`

---

### 3. **Run Optimization** (30-60 min)

Open **Terminal.app** (not Cursor terminal), then:

```bash
cd /Users/trev/Repos/finishline_audio_repo
./RUN_STAND_TALL_NOW.sh
```

**What it does:**
- Iteratively optimizes Waves C6/SSL/L3 + Saturator parameters
- Targets **-9.0 LUFS** (perceived loudness), **-1.0 dBTP** (streaming safe)
- Auto-exports each iteration via macOS UI automation
- Up to 15 iterations (converges early if target hit)

**Expected behavior:**
- You'll see iteration progress in terminal
- Ableton will auto-export (File menu opens, types filename, clicks Save)
- Hands-off after you press Enter at the start

---

### 4. **Review Final Master** (5 min)

When complete, the script shows:
```
Final master: output/stand_tall_premium_loud_preview_iterN.wav
  LUFS-I: -9.XX (target -9.0)
  True Peak: -X.XX dBTP (limit -1.0)
```

**Listen to it:**
```bash
open output/stand_tall_premium_loud_preview_iter*.wav
```

**Compare to Life You Chose:**
```bash
open output/life_you_chose/master_loud_preview_iter1.wav
```

---

## 🔍 WHAT'S DIFFERENT FROM LIFE YOU CHOSE?

**Premium Plugins:**
- **Waves C6** - Multiband compression for vocal leveling + frequency control
- **Waves SSL** - Glue compression (analog character)
- **Waves L3** - Transparent limiting (better than stock Limiter)
- **Waves F6** - Static preset for harsh frequency smoothing (not automated)

**Algorithm:**
- Adaptive per-band threshold adjustments (C6 low/mid/high)
- SSL threshold/makeup/ratio optimization
- Saturator drive for harmonic RMS boost
- L3 threshold for final limiting
- Diminishing returns detection (stops if LUFS improvement < 0.2 LU)

---

## 📊 TROUBLESHOOTING

### Export fails with "File did not appear"
- Check Ableton's Export defaults (File → Export Audio/Video)
- Ensure no plugin windows are open (they can block UI automation)
- Run export probe test:
  ```bash
  ./scripts/test_export_probe.sh
  ```

### "Device not found" error
- Check master chain order matches expected (Utility → EQ → C6 → F6 → SSL → Saturator → L3)
- Device names must contain: "C6", "F6", "SSL", "Saturator", "L3"

### Master sounds distorted/clipped
- Check Master fader is at 0.0 dB
- Check True Peak in final analysis (should be ≤ -1.0 dBTP)

### Too quiet / Too loud
- **Too quiet:** Re-run with `--mode loud_preview` (default) or check if F6 is cutting too much
- **Too loud:** Re-run with `--mode streaming_safe` (targets -14 LUFS)

---

## 📁 OUTPUT FILES

After optimization:
- `output/stand_tall_premium_loud_preview_iterN.wav` - Final master (N = converged iteration)
- `output/stand_tall_premium_loud_preview.jsonl` - Parameter log (all iterations)

---

## 🚀 NEXT STEPS

1. **A/B Test:** Compare Stand Tall master to Life You Chose master
2. **Refine:** If needed, adjust F6 preset or re-run with different mode
3. **Ship:** Export final master for distribution

---

## 💡 PRO TIPS

- **F6 Preset:** Set a gentle high-frequency cut (2-5 kHz, -2 to -3 dB, wide Q) to smooth harshness
- **Monitoring:** Watch Terminal output - each iteration shows LUFS/Peak progress
- **Patience:** Convergence typically takes 5-10 iterations (~20-40 min)
- **Logs:** Check `output/stand_tall_premium_loud_preview.jsonl` for detailed parameter history

---

**Ready?** Open Terminal and run:
```bash
./RUN_STAND_TALL_NOW.sh
```
