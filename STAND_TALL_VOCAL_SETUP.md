# 🎤 STAND TALL - VOCAL PROCESSING SETUP (FINAL)

**Do this BEFORE running master optimization** - master chain will exaggerate vocal inconsistencies.

**Version 2.0** - Incorporates all ChatGPT feedback (3-layer model, F6 split, group-level sends, lock vocal step)

---

## ⚡ THE 3-LAYER LEVELING MODEL (CRITICAL)

**For "all over the place" vocals, this is the real fix:**

### **Layer A: Clip Gain / Utility Automation (COARSE - DO THIS FIRST!)**
- **Fix worst phrases:** ±1-4 dB adjustments
- **Time:** 5-10 minutes, listen through track once
- **Method:** 
  - In Arrangement View, use Clip Gain slider on individual clips
  - OR automate Utility PRE gain on VOCALS group for dynamic fixes
- **"DONE" criteria (measurable gate):**
  - ✅ **No phrase is obviously off WITHOUT Vocal Rider enabled**
  - ✅ **When you enable Vocal Rider, it rarely hits range limits (±2-4 dB)**
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

## 🎯 VOCALS GROUP (Lead Vocals)

**CRITICAL:** All processing happens on VOCALS **GROUP** (return bus), not individual vocal tracks.

**Goal:** Consistent level, softer top, less mud, smooth dynamics

### Device Chain (top → bottom):

#### 1. **Ableton Utility** (PRE gain staging)
- **Gain:** Adjust so vocal peaks sit **-10 to -6 dBFS** on VOCALS group meter (pre-chain)
- **Target:** After this Utility, before any processing
- This is your "trim in" - sets proper gain staging for the chain

#### 2. **MANUAL PASS: Clip Gain / Utility Automation (Layer A)**
- **CRITICAL:** Do this BEFORE enabling other plugins!
- Listen through track, fix worst phrases (±1-4 dB)
- Use Clip Gain slider on individual clips OR automate this Utility's gain
- **"DONE" criteria:**
  - No phrase obviously off WITHOUT Vocal Rider
  - Vocal Rider rarely hits range limits when enabled
- **Time:** 5-10 minutes
- **This is the primary fix** - everything else is polish

#### 3. **Waves Vocal Rider** (Layer C - Fine polish)
- **Range:** ±2-4 dB (if slamming limits, go back to clip gain!)
- **Speed:** Fast (if it lags, go faster; if it chatters, slower)
- **Sensitivity:** Medium-high (catch quiet lines)
- **Sidechain filter/detection:** Ignore lows (kick/bass won't drive it)
- **Output:** 0 dB (trim later with POST utility)
- *Purpose: Micro-balancing, phrase-to-phrase smoothing (NOT primary leveling)*

#### 4. **Waves F6 (Static Cleanup)** - BEFORE COMPRESSION
- **Purpose:** Subtractive EQ before compression (prevents comp reacting to mud/boxiness)
- **HPF:** 80 Hz, 24 dB/oct (rumble removal)
  - **Flexibility:** Lower to 60-70 Hz if vocal sounds hollow/thin
- **Mud removal (STATIC cut):**
  - Freq: 220–350 Hz
  - Q: 1.0–1.4 (wide)
  - **Static mode** (not dynamic)
  - Cut: -2 to -4 dB (permanent reduction)
- **Harshness removal (STATIC cut):**
  - Freq: 2.5–4.5 kHz
  - Q: 2–4 (narrower)
  - **Static mode** (not dynamic)
  - Cut: -1 to -3 dB (permanent reduction, gentle)
- *Purpose: Clean up problem areas BEFORE compression sees them*

#### 5. **Waves R-Vox** (Layer B - Compression)
- **Threshold:** Set for 3–6 dB gain reduction on loud lines (typical), peaks 8 dB max
- **Gate:** OFF or very light
- **Output:** Match bypass loudness (no jumps)
- *Purpose: Consistent RMS, steady containment*
- **NOTE:** Compression can raise sibilance - de-ess AFTER this

#### 6. **Waves Sibilance** (or Waves DeEsser)
- **Target band:** 5–9 kHz
- **Reduction:** 2–5 dB on "S/T" moments (not constant)
- *Purpose: Tame sibilance AFTER compression (compression raises S's)*
- **Placement:** After R-Vox is critical for "soft/polished" goal

#### 7. **Waves F6 (Dynamic Control)** - AFTER COMPRESSION
- **Purpose:** Dynamic frequency control (responsive to vocal dynamics)
- **Mud control (DYNAMIC):**
  - Freq: 220–350 Hz
  - Q: 1.0–1.4 (wide)
  - **Dynamic mode**
  - Range: -2 to -4 dB (responds to buildup)
- **Harshness control (DYNAMIC):**
  - Freq: 2.5–4.5 kHz
  - Q: 2–4 (narrower)
  - **Dynamic mode**
  - Range: -2 to -5 dB (responds to peaks)
- **Backup sibilance (DYNAMIC - if Sibilance plugin isn't enough):**
  - Freq: 6–9 kHz
  - **Dynamic mode**
  - Range: -2 to -4 dB
- *Purpose: Dynamic frequency control without static cuts*

#### 8. **Ableton Utility** (POST trim)
- **Gain:** Final trim to place VOCALS group in the mix
- This is your "trim out" - balances vocal group vs. other elements

### Optional (only if quiet lines still disappear):

#### **Waves MV2** (after Utility POST)
- **Low Level:** 10–20 (brings up quiet passages)
- **High Level:** 0–5 (gentle limiting)
- **Warning:** Can bring up room noise/reverb - remove if messy
- **Only use if Layer A (clip gain) + Layer B (compression) + Layer C (Vocal Rider) aren't enough**

---

## 📐 CALIBRATION PROCEDURE (Dial Settings Correctly)

**Don't just guess - use this workflow:**

### Step 1: Find Your Extremes
1. **Locate densest chorus** (loudest, most energetic section)
2. **Locate quietest verse** (softest, most intimate section)

### Step 2: Dial on Dense Chorus
1. Solo VOCALS group
2. Play densest chorus on loop
3. Dial in each plugin:
   - Vocal Rider: Should move ±1-2 dB (small movements)
   - F6 static: Cut mud/harshness to taste
   - R-Vox: 4-6 dB GR on loud lines
   - Sibilance: 3-5 dB reduction on "S/T"
   - F6 dynamic: Bands move but not pinned

### Step 3: Verify on Quiet Verse
1. Play quietest verse
2. Check if verse disappears or feels thin
3. **If verse disappears:**
   - ✅ Raise Vocal Rider sensitivity slightly
   - ✅ Use MV2 lightly (Low Level 10-20)
   - ❌ **DON'T crush R-Vox harder** (causes pumping)
4. **If verse sounds good:**
   - Settings are correct
   - Move to next phase

### Step 4: Full Track Test
1. Play full track (unsolo)
2. Listen for:
   - Consistent level across verses/choruses
   - No pumping/breathing
   - Smooth FX tails
2. If any phrase still jumps out, add clip gain adjustment (back to Layer A)

---

## 🎸 INSTRUMENTS / MUSIC BUS (Critical Addition!)

**Goal:** Make space for vocals WITHOUT just boosting vocals

### NEW GROUP: INSTRUMENTS (or MUSIC)

Route all non-vocal elements to this group:
- All instrument tracks
- All drum tracks  
- All synth tracks
- **NOT vocals or vocal FX returns**

### Device Chain:

#### **Waves F6** (Dynamic EQ with sidechain)
- **Sidechain input:** VOCALS group (lead vocals)
- **Purpose:** Duck instruments when vocals sing, creating space

**Dynamic EQ Bands (sidechained from VOCALS):**

1. **Presence band (vocal clarity):**
   - Freq: 2.5–4.5 kHz
   - Q: 1.5–2.5
   - **Dynamic mode, Sidechain ON**
   - Range: -1 to **-3 dB MAX** (guardrail)
   - Release: **150–350 ms** (avoid pumping)
   - *Ducks instrument presence when vocals sing*

2. **Body band (vocal warmth):**
   - Freq: 200–350 Hz
   - Q: 1.0–1.5
   - **Dynamic mode, Sidechain ON**
   - Range: -1 to **-2 dB MAX** (guardrail)
   - Release: **150–350 ms** (avoid pumping)
   - *Ducks instrument low-mids when vocals sing*

**Guardrails (prevent overuse):**
- **Presence duck:** Max -3 dB (more sounds hollow)
- **Body duck:** Max -2 dB (more loses weight)
- **Release:** 150-350 ms (faster pumps, slower drags)
- **If mix sounds hollow:** Reduce presence duck before touching vocal level

**Result:** Vocals sit naturally in mix without level wars. Instruments "breathe" around vocals.

---

## ⚠️ SIDECHAIN VERIFICATION CHECKLIST

**After routing tracks to INSTRUMENTS group, verify:**

1. **Check existing sidechains:**
   - Do any effects currently sidechain off individual elements?
   - (e.g., reverb ducking from kick, delay from snare)

2. **Verify sidechain sources still correct:**
   - If kick was on track 5, now it's in INSTRUMENTS group
   - Sidechain detectors may see different levels
   - Re-test each sidechained effect

3. **Fix broken sidechains:**
   - If sidechain doesn't work anymore, re-route to correct source
   - May need to use pre-fader send from individual track

**Don't skip this** - routing changes can break existing automation.

---

## 🌊 REVERB/DELAY RETURNS (Smooth, ducking)

Keep verbs/delays **on sends**, then **duck the return** so they breathe with vocals.

### ⚠️ CRITICAL: GROUP-LEVEL SEND ROUTING

**WHERE sends live (this is critical for stable FX):**

1. **Sends must be on VOCALS GROUP** (return bus), **NOT individual vocal tracks**
2. **Why:** Vocal Rider on group affects group fader, which affects send levels (if post-fader)
3. **If sends are on individual tracks:** Vocal Rider won't affect FX send levels = uneven reverb/delay

**How to set up:**
1. **Remove all sends from individual vocal tracks**
2. **Add sends on VOCALS GROUP only**
3. **Set sends to POST-fader** (right-click send knob → Post-Fader)

**Result:** When Vocal Rider/compression smooths dry vocal, FX levels smooth too = stable sound.

---

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
- **Ableton Compressor** with **sidechain from VOCALS group**
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

## 🎵 CHORUS FEATURES BUS (Background Vocals)

**Goal:** Wider, flatter, supportive (not competing with lead)

### Device Chain (top → bottom):

#### 1. **Ableton Utility** (PRE gain staging)
- Start **-3 dB** vs lead vocals (backgrounds sit behind)

#### 2. **Waves F6** (Static + Dynamic EQ)
- **HPF:** 120 Hz, 24 dB/oct (more aggressive than lead)
- **Mud control:** 250–400 Hz, MORE cut than lead (-3 to -6 dB, STATIC)
- **Harshness control:** 3–5 kHz, MORE cut than lead (-3 to -6 dB, STATIC)
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

## 📊 OBJECTIVE TARGETS (What "Good" Looks Like)

### **VOCALS Group Meters:**

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

#### F6 Static (before R-Vox):
- ✅ **Permanent cuts** (not moving)
- ✅ Mud/harshness reduced by 2-4 dB

#### R-Vox (Compression):
- ✅ **Typical GR: 3-6 dB** (steady containment)
- ✅ **Peak GR: 8 dB max** (on loudest phrases)
- ❌ **Constant 10+ dB GR** = reduce threshold OR go back to Layer A
- ❌ **Pumping/breathing** = attack/release too fast OR too much compression

#### F6 Dynamic (after Sibilance):
- ✅ **Move often** (responding to vocal dynamics)
- ✅ **Not pinned at max range** (dynamic control, not brick wall)
- ❌ **Constantly maxed out** = range too narrow OR source problem

#### Instruments Bus F6 (Sidechain):
- ✅ **Ducks 1-3 dB when vocals sing** (subtle space-making)
- ✅ **Returns to 0 dB in gaps** (breathing behavior)
- ✅ **Release 150-350 ms** (smooth, not pumpy)
- ❌ **Constant ducking** = sidechain sensitivity too high
- ❌ **Mix sounds hollow** = reduce presence duck (max -3 dB!)

### **Master Meter:**
- Total mix: **-18 to -12 dBFS** (leave headroom for mastering)
- **NOT hitting 0 dBFS** (master chain optimization will bring it up)

### Red flags:
- ❌ Vocal bus clipping (reduce Utility PRE gain)
- ❌ Vocal Rider pinned at limits (do Layer A: clip gain first!)
- ❌ R-Vox causing pumping (reduce threshold OR attack/release too fast)
- ❌ Reverb/Delay overwhelming mix (check sidechain ducking + group-level sends)
- ❌ Instruments not ducking (check F6 sidechain routing + verify after routing change)
- ❌ Mix sounds hollow (reduce presence duck on instruments bus)

---

## ✅ WORKFLOW (Step-by-Step)

### **Phase 1: Coarse Leveling (Layer A - CRITICAL!)**

1. **Add Utility PRE to VOCALS group**, set gain for -10 to -6 dBFS peaks
2. **MANUAL PASS: Clip gain / automation**
   - Listen through full track
   - Fix worst phrases (±1-4 dB)
   - Use Clip Gain slider on individual clips OR automate Utility PRE
   - **"DONE" criteria:** No phrase obviously off WITHOUT Vocal Rider enabled
   - **Time:** 5-10 minutes
3. **Verify:** Play through track, levels should be "mostly even"

### **Phase 2: VOCALS Group Chain (Layers B & C)**

4. **Add chain in order:**
   - Vocal Rider (±2-4 dB range)
   - F6 (static cleanup: HPF + mud/harshness cuts)
   - R-Vox (3-6 dB GR)
   - Sibilance (after R-Vox!)
   - F6 (dynamic bands: mud/harshness/sibilance)
   - Utility POST (final trim)

5. **Calibration procedure:**
   - Find densest chorus + quietest verse
   - Dial on chorus, verify on verse
   - Adjust Vocal Rider sensitivity if verse disappears
   - Use MV2 only if needed (last resort)

6. **Verify:** 
   - Vocal Rider not pinned at limits (80% time within ±1.5 dB center)
   - R-Vox steady 3-6 dB GR
   - F6 static cuts permanent, F6 dynamic bands moving

### **Phase 3: Instruments Bus Ducking (Space-Making)**

7. **Create INSTRUMENTS/MUSIC group**
8. **Route all non-vocal tracks** to this group
9. **CRITICAL: Verify existing sidechains** (checklist above)
10. **Add F6 with sidechain from VOCALS group**
11. **Set dynamic bands with guardrails:**
    - 2.5-4.5 kHz: -1 to -3 dB MAX, Release 150-350 ms
    - 200-350 Hz: -1 to -2 dB MAX, Release 150-350 ms
12. **Verify:** Instruments duck when vocals sing, release smoothly

### **Phase 4: Background Vocals & FX**

13. **Setup Chorus Features group chain** (backgrounds)
14. **Setup Reverb/Delay returns** (with EQ + sidechain ducking)
15. **CRITICAL: Remove sends from individual vocal tracks**
16. **Add sends on VOCALS GROUP only, set to POST-fader**
17. **Verify:** Reverb/delay levels stay even with vocal dynamics

### **Phase 5: Final Check & Lock Vocal**

18. **Listen through full track**, check problem spots resolved
19. **Verify objective targets** (Vocal Rider usage, R-Vox GR, meters, ducking)
20. **Export quick reference** (no mastering) to check balance

21. **LOCK VOCAL (CRITICAL - do before master optimization):**
    - Right-click VOCALS group → Freeze Track
    - OR Export VOCALS group as stem, import on new track, disable VOCALS group
    - **Why:** Master optimizer needs stable target, not moving vocal dynamics
    - **Result:** Master chain optimizes consistent vocal level

22. **Run master optimization:**
    ```bash
    ./RUN_STAND_TALL_NOW.sh
    ```

---

## 💡 PRO TIPS

1. **Clip gain FIRST, always** - Vocal Rider is polish (Layer C), not primary fix (Layer A)
2. **F6 split is critical** - Static cleanup BEFORE compression, dynamic AFTER
3. **Group-level sends only** - Individual track sends won't follow Vocal Rider
4. **Calibrate on extremes** - Dial on densest chorus, verify on quietest verse
5. **Lock vocal before mastering** - Freeze/flatten VOCALS group = stable target
6. **Instruments ducking = secret weapon** - Create space without boosting vocals
7. **Ducking guardrails prevent overuse** - Max -3 dB presence, -2 dB body
8. **De-ess AFTER compression** - R-Vox can raise sibilance, fix it downstream
9. **Watch objective targets** - If Vocal Rider pinned, go back to clip gain
10. **Verify sidechains after routing** - Routing changes can break existing automation
11. **A/B constantly** - Bypass entire chain to hear improvement
12. **Solo VOCALS group** - Dial in processing without distractions
13. **Check in context** - Mix decisions should be made in full mix
14. **Less is more** - If plugin isn't helping, remove it
15. **HPF aggressively** - 80 Hz on lead (60-70 Hz if thin), 120 Hz on backgrounds

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

### **3. F6 Split is Critical**

- **Static F6 (before R-Vox):** Subtractive EQ (prevents comp reacting to mud/boxiness)
- **Dynamic F6 (after Sibilance):** Responsive frequency control

**Don't skip the split** - it's the difference between smooth and harsh.

### **4. Group-Level Sends or Bust**

Sends on individual vocal tracks = Vocal Rider doesn't affect FX levels = uneven reverb/delay.

**Always use group-level sends.**

### **5. Lock Vocal Before Mastering**

Freeze/flatten VOCALS group = master optimizer has stable target.

**Don't skip this** - master chain chasing moving dynamics = poor convergence.

### **6. Instruments Bus Ducking = Game Changer**

Creating space by ducking instruments (2.5-4.5 kHz, 200-350 Hz) is smarter than boosting vocals. 

**But use guardrails** - max -3 dB presence, -2 dB body, or mix sounds hollow.

---

**When vocal processing is complete and locked, run:**
```bash
cd /Users/trev/Repos/finishline_audio_repo
./RUN_STAND_TALL_NOW.sh
```

Master chain will have clean, consistent vocals to work with.
