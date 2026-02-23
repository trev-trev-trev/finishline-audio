# 🎯 STAND TALL - EXECUTE NOW (EXACT STEPS)

**Analysis Complete!** Here's what we found:
- True Peak: +0.46 dBTP (⚠️ CLIPPING!)
- RMS Std Dev: 30.30 dB (⚠️ EXTREME inconsistency)
- Peak: -1.5 dBFS (too hot)

**Conclusion:** Clip gain (Layer A) is CRITICAL. Expect 10-20 adjustments.

---

## ⚡ PHASE 0: CRITICAL FIX (Do This FIRST - 1 minute)

### **In Ableton:**

1. Click **VOCALS group/track** (return bus)
2. Add **Ableton Utility** as FIRST device
3. Set **Gain: -3 dB**
   - Why: Pulls peaks back from clipping edge
   - Result: Peak ~-4.5 dBFS, True Peak ~-2.5 dBTP (safe)

**✓ DONE? Move to Phase 1.**

---

## 🎵 PHASE 1: LAYER A - CLIP GAIN PASS (5-10 minutes)

### **Goal:** Fix "all over the place" inconsistency at source

### **Method:**

1. **Open Arrangement View** (Tab key)
2. **Play track from start**
3. **Listen for phrases that jump out** (obviously louder/quieter)
4. **For each problem phrase:**
   - Click the clip
   - Find **Clip Gain** slider (bottom of clip editor, or Info View)
   - Adjust:
     - Too loud? **-2 to -4 dB**
     - Too quiet? **+2 to +4 dB**
5. **Mark as you go** (take notes or add locators)

### **"DONE" Criteria (measurable):**
- ✅ No phrase is obviously off WITHOUT Vocal Rider enabled
- ✅ When you enable Vocal Rider later, it rarely hits ±4 dB limits

### **Expected:**
- 10-20 adjustments (based on 30 dB std dev)
- Takes 5-10 minutes

### **Quick Reference - Problem Areas:**
Based on analysis, check these timestamps:
- 00:00-00:02 (very quiet intro - ignore or trim)
- Then: Listen through entire track, mark loud/quiet spots

**✓ DONE? Export to verify improvements.**

---

## 📤 VERIFY PHASE 1 (2 minutes)

### **Export after Utility PRE + Clip Gain:**

1. Solo VOCALS group
2. **Make sure Utility PRE (-3 dB) is ON**
3. **Bypass all other processing** (if any exists)
4. File → Export Audio/Video
   - Rendered Track: Master (soloed = VOCALS only)
   - Normalize: OFF
   - File: `stand_tall_vocal_layer_a.wav`
   - Location: `output/`
5. Export
6. Unsolo VOCALS

### **Verify:**
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
flaas verify-audio output/stand_tall_vocal_layer_a.wav
```

### **Expected results:**
- True Peak: **< 0 dBTP** (negative, no clipping!)
- Peak: **-4 to -6 dBFS** (good headroom)
- LUFS: **-12 to -14 dBFS** (lower is fine, we'll raise it later)

**If True Peak still positive:** Reduce Utility PRE more (-4 or -5 dB).

**✓ PASS? Move to Phase 2.**

---

## 🎚️ PHASE 2: ADD PROCESSING CHAIN (5 minutes)

### **On VOCALS group, add these devices IN ORDER:**

#### 1. **Utility PRE** (already added, keep at -3 dB)

#### 2. **Waves Vocal Rider**
- Range: **±4 dB** (wider than normal due to high inconsistency)
- Speed: **Fast**
- Sensitivity: **Medium-High**
- Sidechain: **Ignore lows** (so kick/bass don't drive it)

#### 3. **Waves F6** (Static Cleanup)
- **HPF:** 80 Hz, 24 dB/oct
- **Band 1 (Mud):**
  - Freq: **250-350 Hz**
  - Q: **1.2**
  - Mode: **STATIC** (not dynamic)
  - Cut: **-3 dB**
- **Band 2 (Harshness):**
  - Freq: **3-5 kHz**
  - Q: **2.5**
  - Mode: **STATIC** (not dynamic)
  - Cut: **-2 dB**

#### 4. **Waves R-Vox**
- Threshold: Set for **4-6 dB gain reduction** on loud lines
  - (Higher than normal due to wide dynamic range)
- Gate: **OFF**
- Output: **Match bypass loudness**

#### 5. **Waves Sibilance** (or DeEsser)
- Band: **5-9 kHz**
- Reduction: **3-5 dB** on "S/T" moments

#### 6. **Waves F6** (Dynamic Control)
- **Band 1 (Dynamic Mud):**
  - Freq: **220-350 Hz**
  - Q: **1.0**
  - Mode: **DYNAMIC**
  - Range: **-2 to -4 dB**
- **Band 2 (Dynamic Harshness):**
  - Freq: **2.5-4.5 kHz**
  - Q: **2.5**
  - Mode: **DYNAMIC**
  - Range: **-2 to -5 dB**

#### 7. **Utility POST** (Final Trim)
- Gain: **Adjust to taste** (balance VOCALS vs mix)
- Start at 0 dB, adjust later

**✓ DONE? Verify processing.**

---

## 📊 VERIFY PHASE 2 (Objective Targets)

### **Play track and watch:**

#### **Vocal Rider:**
- ✅ Spends 80% of time within **±2 dB** of center
- ✅ Occasionally hits ±4 dB limits, but NOT constantly
- ❌ **Pinned at limits?** → Go back to Layer A (more clip gain fixes)

#### **R-Vox:**
- ✅ Typical GR: **4-6 dB** (steady)
- ✅ Peak GR: **8-10 dB** (on loudest phrases)
- ❌ **Constant 12+ dB GR?** → Threshold too low OR go back to Layer A

#### **VOCALS Group Meter:**
- ✅ Post-chain peaks: **-8 to -4 dBFS** (not clipping)

**✓ PASS? Export final processed vocal.**

---

## 📤 EXPORT PHASE 2 (Final Processed Vocal)

### **Export with all processing:**

1. Solo VOCALS group
2. **All processing ON** (full chain)
3. File → Export Audio/Video
   - File: `stand_tall_vocal_processed.wav`
   - Location: `output/`
4. Export
5. Unsolo VOCALS

### **Verify:**
```bash
flaas verify-audio output/stand_tall_vocal_processed.wav
```

### **Expected results:**
- True Peak: **< -1 dBTP** (streaming safe)
- Peak: **-6 to -4 dBFS** (good level)
- LUFS: **-10 to -12 dBFS** (consistent, commercial loudness)

**✓ PASS? Move to Phase 3.**

---

## 🎸 PHASE 3: INSTRUMENTS BUS DUCKING (5 minutes)

### **Create INSTRUMENTS group:**

1. **Create new Group Track** → Name: `INSTRUMENTS` (or `MUSIC`)
2. **Route all non-vocal tracks** to this group:
   - All drums → INSTRUMENTS
   - All synths → INSTRUMENTS
   - All instruments → INSTRUMENTS
   - **NOT vocals!**

### **Add F6 to INSTRUMENTS group:**

1. Add **Waves F6**
2. Set **Sidechain Input: VOCALS group**

### **Configure dynamic bands:**

#### **Band 1 (Presence Duck):**
- Freq: **2.5-4.5 kHz**
- Q: **2.0**
- Mode: **DYNAMIC, Sidechain ON**
- Range: **-1 to -3 dB MAX**
- Release: **200 ms**

#### **Band 2 (Body Duck):**
- Freq: **200-350 Hz**
- Q: **1.5**
- Mode: **DYNAMIC, Sidechain ON**
- Range: **-1 to -2 dB MAX**
- Release: **200 ms**

### **Verify:**
- Play track
- Watch F6 bands duck when vocals sing
- Return to 0 dB in gaps
- **If mix sounds hollow:** Reduce presence duck (max -2 dB instead of -3)

**✓ DONE? Move to Phase 4.**

---

## 🌊 PHASE 4: REVERB/DELAY SETUP (5 minutes)

### **Critical: Group-Level Sends**

1. **Remove all sends from individual vocal tracks** (if any)
2. **Add sends on VOCALS GROUP only:**
   - Send A → Reverb return
   - Send B → Delay return
3. **Set sends to POST-fader:**
   - Right-click send knob → Post-Fader

### **Reverb Return (A):**

#### Before reverb plugin:
- Add **EQ Eight**
  - HPF: **200 Hz**
  - LPF: **8-10 kHz**

#### After reverb plugin:
- Add **Compressor**
  - **Sidechain from VOCALS group**
  - Threshold: Set for **3-6 dB GR** when vocals sing
  - Attack: **5-10 ms**
  - Release: **200-400 ms**
  - Ratio: **4:1**

### **Delay Return (B):**

#### Before delay plugin:
- Add **EQ Eight**
  - HPF: **200 Hz**
  - LPF: **8 kHz**

#### After delay (if no built-in ducking):
- Add **Compressor** (same sidechain as reverb)
  - GR: **2-4 dB**

**✓ DONE? Test full mix.**

---

## ✅ PHASE 5: LOCK VOCAL & MASTER (Final Steps)

### **1. Lock Vocal (CRITICAL before master optimization):**

**Option A: Freeze (faster):**
1. Right-click VOCALS group → **Freeze Track**
2. Wait for freeze to complete

**Option B: Bounce (more control):**
1. Solo VOCALS group
2. Export as `stand_tall_vocal_final.wav`
3. Create new audio track
4. Import stem
5. Disable VOCALS group (click Enable button)

**Why:** Master optimizer needs stable target (not moving vocal dynamics).

### **2. Run Master Optimization:**

```bash
cd /Users/trev/Repos/finishline_audio_repo
./RUN_STAND_TALL_NOW.sh
```

**This will:**
- Optimize Waves C6/SSL/L3 + Saturator chain
- Target: -9.0 LUFS, -1.0 dBTP (loud_preview mode)
- Up to 15 iterations (30-60 minutes)
- Auto-export each iteration

### **3. Review Final Master:**

When complete, check:
- Final LUFS: **-9.X** (close to -9.0)
- True Peak: **< -1.0 dBTP**
- Consistent level across full track

---

## 📋 QUICK REFERENCE CHECKLIST

- [ ] **Phase 0:** Add Utility PRE (-3 dB) to VOCALS group
- [ ] **Phase 1:** Clip gain pass (10-20 adjustments, 5-10 min)
- [ ] **Verify 1:** Export, check True Peak < 0 dBTP
- [ ] **Phase 2:** Add processing chain (Vocal Rider → F6 static → R-Vox → Sibilance → F6 dynamic → Utility POST)
- [ ] **Verify 2:** Check objective targets (Vocal Rider usage, R-Vox GR)
- [ ] **Phase 3:** Create INSTRUMENTS group, add F6 ducking
- [ ] **Phase 4:** Setup reverb/delay (group-level sends, sidechain ducking)
- [ ] **Phase 5:** Lock vocal (freeze/flatten), run master optimization

---

## ⏱️ TIME ESTIMATE

- Phase 0: **1 minute**
- Phase 1: **5-10 minutes** (clip gain pass)
- Verify 1: **2 minutes**
- Phase 2: **5 minutes** (add chain)
- Verify 2: **2 minutes**
- Phase 3: **5 minutes** (instruments ducking)
- Phase 4: **5 minutes** (reverb/delay)
- Phase 5: **30-60 minutes** (master optimization)

**Total: ~60-90 minutes**

---

## 🚀 START NOW!

**Open Ableton, go to Phase 0, execute each step sequentially.**

When you complete each phase, come back and report status.

**LET'S MAKE STAND TALL SHINE!**
