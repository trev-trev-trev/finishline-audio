# 🎤 STAND TALL - VOCAL PROCESSING SETUP

**Do this BEFORE running master optimization** - master chain will exaggerate vocal inconsistencies.

---

## ⚡ THE 3-LAYER LEVELING MODEL (CRITICAL)

**For "all over the place" vocals, this is the real fix:**

### **Layer A: Clip Gain / Utility Automation (COARSE - DO THIS FIRST!)**
- **Fix worst phrases:** ±1-4 dB adjustments
- **Time:** 5-10 minutes, listen through track once
- **Goal:** No phrase is "obviously way too loud/quiet"
- **Method:** 
  - In Arrangement View, use Clip Gain slider
  - OR automate Utility PRE gain for dynamic fixes
- **This is primary fix** - if you skip this, Vocal Rider will slam range limits

### **Layer B: Compression (MEDIUM - Steady Containment)**
- **R-Vox:** 3-6 dB gain reduction
- **Goal:** Consistent RMS, smooth dynamics
- **This is containment** - holds vocal in consistent range

### **Layer C: Vocal Rider (FINE - Micro-Balancing)**
- **Range:** ±2-4 dB (NOT ±6+ dB!)
- **Goal:** Polish and phrase-to-phrase balance
- **This is finishing touch** - if it's slamming range limits, go back to Layer A

**Without Layer A, you'll keep getting "random loud/quiet" and the master chain will keep pumping.**

---

## 🎯 VOCALS BUS (Lead Vocals)

**Goal:** Consistent level, softer top, less mud, smooth dynamics

### Device Chain (top → bottom):

#### 1. **Ableton Utility** (PRE gain staging)
- **Gain:** Adjust so vocal peaks sit **-10 to -6 dBFS** on VOCALS meter (pre-chain)
- **Target:** After this Utility, before any processing
- This is your "trim in" - sets proper gain staging for the chain

#### 2. **MANUAL PASS: Clip Gain / Utility Automation (Layer A)**
- **CRITICAL:** Do this BEFORE enabling other plugins!
- Listen through track, fix worst offenders (±1-4 dB)
- Use Clip Gain slider in Arrangement View OR automate this Utility's gain
- **Goal:** No phrase is "obviously way too loud/quiet"
- **Time:** 5-10 minutes
- **This is the primary fix** - everything else is polish

#### 3. **Waves Vocal Rider** (Layer C - Fine polish)
- **Range:** ±2-4 dB (NOT ±6+ dB! If it's slamming limits, go back to clip gain)
- **Speed:** Fast (if it lags, go faster; if it chatters, slower)
- **Sensitivity:** Medium-high (catch quiet lines)
- **Sidechain filter/detection:** Ignore lows (kick/bass won't drive it)
- **Output:** 0 dB (trim later with POST utility)
- *Purpose: Micro-balancing, phrase-to-phrase smoothing (NOT primary leveling)*

#### 4. **Waves R-Vox** (Layer B - Compression)
- **Threshold:** Set for 3–6 dB gain reduction on loud lines (typical), peaks 8 dB max
- **Gate:** OFF or very light
- **Output:** Match bypass loudness (no jumps)
- *Purpose: Consistent RMS, steady containment*
- **NOTE:** Compression can raise sibilance - de-ess AFTER this

#### 5. **Waves Sibilance** (or Waves DeEsser)
- **Target band:** 5–9 kHz
- **Reduction:** 2–5 dB on "S/T" moments (not constant)
- *Purpose: Tame sibilance AFTER compression (compression raises S's)*
- **Placement:** After R-Vox is critical for "soft/polished" goal

#### 6. **Waves F6** (Dynamic EQ)
- **HPF:** 80 Hz, 24 dB/oct (rumble removal)
  - **Flexibility:** Lower to 60-70 Hz if vocal sounds hollow/thin
  - For 111-track project, aggressive HPF helps avoid mud
- **Mud control:** 
  - Freq: 220–350 Hz
  - Q: 1.0–1.4 (wide)
  - **Dynamic mode**
  - Range: -2 to -4 dB
- **Harshness control:**
  - Freq: 2.5–4.5 kHz
  - Q: 2–4 (narrower)
  - **Dynamic mode**
  - Range: -2 to -5 dB
- **Backup sibilance** (if Sibilance plugin isn't enough):
  - Freq: 6–9 kHz
  - **Dynamic mode**
  - Range: -2 to -4 dB
- *Purpose: Surgical frequency control without static cuts*

#### 7. **Ableton Utility** (POST trim)
- **Gain:** Final trim to place VOCALS in the mix
- This is your "trim out" - balances vocal bus vs. other elements

### Optional (only if quiet lines still disappear):

#### **Waves MV2** (after Utility POST)
- **Low Level:** 10–20 (brings up quiet passages)
- **High Level:** 0–5 (gentle limiting)
- **Warning:** Can bring up room noise/reverb - remove if messy
- **Only use if Layer A (clip gain) + Layer B (compression) + Layer C (Vocal Rider) aren't enough**

---

## 🎸 INSTRUMENTS / MUSIC BUS (Critical Addition!)

**Goal:** Make space for vocals WITHOUT just boosting vocals

### NEW BUS: INSTRUMENTS (or MUSIC)

Route all non-vocal elements to this bus:
- All instrument tracks
- All drum tracks  
- All synth tracks
- **NOT vocals or vocal FX**

### Device Chain:

#### **Waves F6** (Dynamic EQ with sidechain)
- **Sidechain input:** VOCALS bus (lead vocals)
- **Purpose:** Duck instruments when vocals sing, creating space

**Dynamic EQ Bands (sidechained from VOCALS):**

1. **Presence band (vocal clarity):**
   - Freq: 2.5–4.5 kHz
   - Q: 1.5–2.5
   - **Dynamic mode, Sidechain ON**
   - Range: -1 to -3 dB
   - *Ducks instrument presence when vocals sing*

2. **Body band (vocal warmth):**
   - Freq: 200–350 Hz
   - Q: 1.0–1.5
   - **Dynamic mode, Sidechain ON**
   - Range: -1 to -2 dB
   - *Ducks instrument low-mids when vocals sing*

**Result:** Vocals sit naturally in mix without level wars. Instruments "breathe" around vocals.

---

## 🎵 CHORUS FEATURES BUS (Background Vocals)

**Goal:** Wider, flatter, supportive (not competing with lead)

### Device Chain (top → bottom):

#### 1. **Ableton Utility** (PRE gain staging)
- Start **-3 dB** vs lead vocals (backgrounds sit behind)

#### 2. **Waves F6** (Dynamic EQ)
- **HPF:** 120 Hz, 24 dB/oct (more aggressive than lead)
- **Mud control:** 250–400 Hz, MORE cut than lead (-3 to -6 dB)
- **Harshness control:** 3–5 kHz, MORE cut than lead (-3 to -6 dB)
- *Purpose: Cleaner spectrum, avoids masking lead*

#### 3. **Waves Sibilance/DeEsser**
- **Stronger than lead** (backgrounds can be duller)
- Target: 5–9 kHz, 3–6 dB reduction

#### 4. **Waves S1** (Stereo imaging)
- **Width:** 1.2–1.4 (spread backgrounds wide)
- **Keep low end mono:** Below ~150 Hz (prevents phase issues)
- *Purpose: Wide soundstage, keeps lead centered*

#### 5. **Waves R-Vox**
- **Threshold:** 6–10 dB GR (backgrounds can be flatter/more compressed)
- *Purpose: Consistent level, stays in background*

---

## 🌊 REVERB/DELAY RETURNS (Smooth, ducking)

Keep verbs/delays **on sends**, then **duck the return** so they breathe with vocals.

### ⚠️ CRITICAL: POST-Fader Send Routing

**MUST DO:** Set all vocal sends to **POST-fader**
1. Right-click each send knob on VOCALS bus
2. Select "Post-Fader" mode
3. Repeat for all sends (reverb, delay, etc.)

**Why this matters:**
- **POST-fader:** Vocal Rider/leveling changes affect FX send level = even reverb/delay
- **Pre-fader (WRONG):** Dry vocal smooths, but reverb/delay stays uneven = unstable sound

**Without POST-fader sends, your vocal processing won't work properly!**

### Return A (Reverb)

#### Before reverb plugin:
- **Ableton EQ Eight:**
  - **HPF:** 200 Hz (remove mud from reverb)
  - **LPF:** 8–10 kHz (remove harsh reflections)

#### Reverb plugin settings:
- Use your preferred reverb (Ableton Reverb, Valhalla, etc.)
- Decay: 1.5–3.0s (adjust to taste)
- Pre-delay: 15–40 ms (separates vocal from verb)

#### After reverb plugin:
- **Ableton Compressor** with **sidechain from VOCALS bus**
  - **Duck amount:** 3–6 dB GR on phrases
  - **Attack:** Fast (5–10 ms)
  - **Release:** 200–400 ms (slow return)
  - **Ratio:** 4:1 or higher
  - *Purpose: Reverb ducks when vocals sing, swells in gaps*

### Return B (Delay)

#### Before delay plugin:
- **Ableton EQ Eight:**
  - **HPF:** ~200 Hz
  - **LPF:** ~8 kHz (filtered delay sits better)

#### Delay plugin:
- Use filtered delay or standard delay
- Check if it has built-in ducking (some Waves delays do)

#### If no built-in ducking:
- **Ableton Compressor** after delay, same sidechain method as reverb
  - Duck amount: 2–4 dB GR
  - Release: 150–300 ms

---

## 🛠️ FIX REMAINING "RANDOM LOUD/QUIET" MOMENTS

After processing, if specific words/phrases still spike or dip:

### Option 1: Clip Gain (preferred for isolated issues)
1. In Arrangement View, double-click the clip
2. Use **Clip Gain** slider (±1–2 dB adjustments)
3. Fast, transparent, non-destructive

### Option 2: Automation (for dynamic fixes)
1. Automate **Utility PRE gain** (the first Utility in chain)
2. Draw automation envelope for problem words
3. Quick down/up (fast, clean)

**DO NOT** automate final master chain - fix issues at source.

---

## 📊 OBJECTIVE TARGETS (What "Good" Looks Like)

### **VOCALS Bus Meters:**

**Pre-chain (after Utility PRE):**
- Peaks: **-10 to -6 dBFS** (before any processing)
- This is your input level target

**Post-chain (after final Utility POST):**
- Peaks: **-8 to -4 dBFS** (after all processing)
- **NOT clipping** (red meter = bad)
- Consistent level across phrases

### **Plugin Behavior (what's working correctly):**

#### Vocal Rider:
- ✅ **Spends 80% of time within ±1.5 dB of center** (small movements)
- ✅ Occasionally hits range limits (±2-4 dB), but NOT constantly
- ❌ **Pinned at range limits** = go back to Layer A (clip gain)

#### R-Vox (Compression):
- ✅ **Typical GR: 3-6 dB** (steady containment)
- ✅ **Peak GR: 8 dB max** (on loudest phrases)
- ❌ **Constant 10+ dB GR** = reduce threshold OR go back to Layer A
- ❌ **Pumping/breathing** = attack/release too fast OR too much compression

#### F6 Dynamic Bands:
- ✅ **Move often** (responding to vocal dynamics)
- ✅ **Not pinned at max range** (dynamic control, not brick wall)
- ❌ **Constantly maxed out** = range too narrow OR source problem

#### Instruments Bus F6 (Sidechain):
- ✅ **Ducks 1-3 dB when vocals sing** (subtle space-making)
- ✅ **Returns to 0 dB in gaps** (breathing behavior)
- ❌ **Constant ducking** = sidechain sensitivity too high

### **Master Meter:**
- Total mix: **-18 to -12 dBFS** (leave headroom for mastering)
- **NOT hitting 0 dBFS** (master chain optimization will bring it up)

### Red flags:
- ❌ Vocal bus clipping (reduce Utility PRE gain)
- ❌ Vocal Rider pinned at limits (do Layer A: clip gain first!)
- ❌ R-Vox causing pumping (reduce threshold OR attack/release too fast)
- ❌ Reverb/Delay overwhelming mix (check sidechain ducking + POST-fader sends)
- ❌ Instruments not ducking (check F6 sidechain routing)

---

## ✅ WORKFLOW (Step-by-Step)

### **Phase 1: Coarse Leveling (Layer A - CRITICAL!)**

1. **Add Utility PRE to VOCALS bus**, set gain for -10 to -6 dBFS peaks
2. **MANUAL PASS: Clip gain / automation**
   - Listen through full track
   - Fix worst phrases (±1-4 dB)
   - Use Clip Gain slider OR automate Utility PRE
   - **Goal:** No phrase is "obviously way too loud/quiet"
   - **Time:** 5-10 minutes
3. **Verify:** Play through track, levels should be "mostly even"

### **Phase 2: VOCALS Bus Chain (Layers B & C)**

4. **Add compression chain:**
   - Vocal Rider (±2-4 dB range)
   - R-Vox (3-6 dB GR)
   - Sibilance (after R-Vox!)
   - F6 (dynamic EQ)
   - Utility POST (final trim)
5. **Dial in each plugin**, watch objective targets
6. **Verify:** Vocal Rider not pinned, R-Vox steady 3-6 dB GR

### **Phase 3: Instruments Bus Ducking (Space-Making)**

7. **Create INSTRUMENTS/MUSIC bus**
8. **Route all non-vocal tracks** to this bus
9. **Add F6 with sidechain from VOCALS**
10. **Set dynamic bands:** 2.5-4.5 kHz (-1 to -3 dB), 200-350 Hz (-1 to -2 dB)
11. **Verify:** Instruments duck when vocals sing

### **Phase 4: Background Vocals & FX**

12. **Setup Chorus Features chain** (backgrounds)
13. **Setup Reverb/Delay returns** (with EQ + sidechain ducking)
14. **CRITICAL: Set all vocal sends to POST-fader**
15. **Verify:** Reverb/delay levels stay even with vocal dynamics

### **Phase 5: Final Check & Export**

16. **Listen through full track**, check problem spots resolved
17. **Verify objective targets** (Vocal Rider usage, R-Vox GR, meters)
18. **Export quick reference** (no mastering) to check balance
19. **If everything sounds consistent, run master optimization:**
    ```bash
    ./RUN_STAND_TALL_NOW.sh
    ```

---

## 🎯 EXPECTED RESULTS

**Before:**
- Random loud/quiet sections
- Harsh sibilance cutting through
- Muddy low-mids masking clarity
- Reverb/delay fighting lead vocal

**After:**
- Consistent vocal level (verse/chorus smooth)
- Soft top end (no harsh S/T)
- Clear presence (no mud)
- Smooth dynamics (compressed but natural)
- Reverb/delay breathing with vocals

---

## 💡 PRO TIPS

1. **Clip gain FIRST, always:** Vocal Rider is polish (Layer C), not primary fix (Layer A)
2. **POST-fader sends are mandatory:** Pre-fader = uneven FX, sounds amateur
3. **Instruments bus ducking = secret weapon:** Create space without boosting vocals
4. **De-ess AFTER compression:** R-Vox can raise sibilance, fix it downstream
5. **Watch objective targets:** If Vocal Rider is pinned, go back to clip gain
6. **A/B constantly:** Bypass entire chain to hear improvement
7. **Solo VOCALS bus:** Dial in processing without distractions
8. **Check in context:** Mix decisions should be made in full mix
9. **Less is more:** If plugin isn't helping, remove it
10. **HPF aggressively:** 80 Hz on lead (60-70 Hz if thin), 120 Hz on backgrounds
11. **Sidechain ducking on returns:** Makes reverb/delay sound expensive

---

## 🚨 CRITICAL NOTES

### **1. Master Chain = Microscope**

**Your master chain (C6/SSL/L3) will EXAGGERATE vocal inconsistencies.**

If vocals aren't level BEFORE mastering:
- Master compressor (C6/SSL) will pump on vocal peaks
- Limiter (L3) will crush loud phrases, miss quiet ones
- Final LUFS will be inconsistent across song

**Fix vocal levels FIRST (3-layer model), then master.** This is the pro approach.

### **2. The 3-Layer Model is Non-Negotiable**

For "all over the place" vocals:
- **Layer A (clip gain)** = PRIMARY FIX (5-10 min manual pass)
- **Layer B (compression)** = containment (R-Vox 3-6 dB GR)
- **Layer C (Vocal Rider)** = polish (±2-4 dB range)

**Skipping Layer A = Vocal Rider slams limits = master chain pumps.**

### **3. POST-Fader Sends or Bust**

Pre-fader sends = uneven FX = amateur sound. Always POST-fader.

### **4. Instruments Bus Ducking = Game Changer**

Creating space by ducking instruments (2.5-4.5 kHz, 200-350 Hz) is smarter than boosting vocals. Master this technique.

---

**When vocal processing is complete, run:**
```bash
cd /Users/trev/Repos/finishline_audio_repo
./RUN_STAND_TALL_NOW.sh
```

Master chain will have clean, consistent vocals to work with.
