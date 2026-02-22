# THE MASTER IMPLEMENTATION GUIDE
## Finish Line Audio Automation System

**Your Engineering Notebook: From Zero to Finished Album**

---

## How to Use This Guide

This is your complete playbook. Every step is numbered. Every step has validation. Follow it in order. Don't skip. Don't improvise. Just execute.

**What you'll see:**
* **Headers** (1-3 words) - Quick tags for each section
* **What** - Brief explanation of what you're doing
* **Why** - Brief explanation of why it matters  
* **Steps** - Exact actions to take (click this, type this, see this)
* **Validation** - How to confirm it worked
* **Model** - Which AI model to use (when relevant)
* **Mode** - Which Cursor mode to use (Agent/Ask/Plan)

**Time estimate:** 16-24 hours if you follow every step without deviation.

**Philosophy:** This is like washing dishes. You're not changing the music. You're making it technically clean so it doesn't break speakers and meets streaming standards. The taste, vibe, style - that's already locked. This just makes it bigger and cleaner.

---

## TABLE OF CONTENTS (Index)

### PART 1: FOUNDATION (Steps 1-150)
Setup everything needed before any code is written.

**Section 1A: Workspace Preparation** (Steps 1-30)
- 001: Repository Check
- 002: Directory Creation
- 003: Dependencies Install
- 004: Config Verification
- 005: AbletonOSC Download
- 006: AbletonOSC Install
- 007: Ableton Preferences
- 008: OSC Test
- 009: Test Song Selection
- 010: Track Standardization

**Section 1B: Stem Export** (Steps 31-60)
- 011: Export Settings Lock
- 012: Vocal Lead Export
- 013: Vocal BG Export
- 014: Kick Export
- 015: Drums Export
- 016: Bass Export
- 017: Music Export
- 018: FX Export
- 019: Reverb Return Export
- 020: Master Export

**Section 1C: Validation Checkpoint** (Steps 61-75)
- 021: File Presence Check
- 022: Sample Rate Verify
- 023: Bit Depth Verify
- 024: Length Consistency
- 025: Waveform Visual Check

### PART 2: PHASE 0 - OSC BRIDGE (Steps 76-200)
Build and test the control bridge to Ableton.

**Section 2A: OSC RPC Implementation** (Steps 76-120)
- 026: RPC File Creation
- 027: Config Dataclass
- 028: OSC Server Setup
- 029: Client Setup
- 030: Message Queue
- 031: Call Method
- 032: Retry Logic
- 033: Error Handling

**Section 2B: OSC Testing** (Steps 121-150)
- 034: Ping Test
- 035: Track Names Test
- 036: Device List Test
- 037: Param Read Test
- 038: Param Write Test
- 039: Param Verify Test

**Section 2C: API Wrapper** (Steps 151-200)
- 040: API File Creation
- 041: Track Names Function
- 042: Device Names Function
- 043: Param Bulk Read
- 044: Param Single Set
- 045: Integration Test

### PART 3: PHASE 1 - FIRST CLOSED LOOP (Steps 201-400)
One action, end-to-end: Utility gain trim.

**Section 3A: Scanner Implementation** (Steps 201-250)
- 046: Cache Dataclasses
- 047: Scanner Algorithm
- 048: Fingerprint Hash
- 049: JSON Serialization
- 050: Scan Command

**Section 3B: Audio Analysis Core** (Steps 251-320)
- 051: WAV IO
- 052: Peak Detection
- 053: RMS Calculation
- 054: Activity Masking
- 055: Crest Factor
- 056: LUFS Calculation

**Section 3C: Headroom Detector** (Steps 321-360)
- 057: Detector Schema
- 058: Headroom Logic
- 059: Confidence Scoring
- 060: Persistence Key
- 061: Evidence Dict

**Section 3D: Utility Adapter** (Steps 361-400)
- 062: Adapter File
- 063: Find Gain Param
- 064: dB to Raw Converter
- 065: Set Gain Method
- 066: Clamp Logic

**Section 3E: Action Generation** (Steps 401-440)
- 067: Action Schema
- 068: Rule Engine
- 069: Role Gating
- 070: Confidence Gating
- 071: Actions JSON

**Section 3F: Apply Pipeline** (Steps 441-480)
- 072: Load Cache
- 073: Validate Fingerprint
- 074: Resolve IDs
- 075: Apply with Throttle
- 076: Verify After Set

**Section 3G: Report Generation** (Steps 481-520)
- 077: Report Schema
- 078: Before Metrics
- 079: Violations List
- 080: After Metrics
- 081: Pass/Fail Status

### PART 4: PHASE 2 - LIMITER (Steps 521-620)
Add master limiter ceiling control.

**Section 4A: Limiter Adapter** (Steps 521-560)
- 082: Limiter File
- 083: Find Ceiling Param
- 084: Set Ceiling Method
- 085: Master Track Find
- 086: Integration Test

**Section 4B: Limiter Rule** (Steps 561-600)
- 087: Master Rules Section
- 088: Limiter Action Type
- 089: Rule Priority
- 090: Apply Test

**Section 4C: Verification** (Steps 601-620)
- 091: Limiter Verify Read
- 092: Value Tolerance Check
- 093: Report Update

### PART 5: PHASE 3 - EQ EIGHT (Steps 621-900)
Complex device: parameter conversion, band control, mud detection.

**Section 5A: STFT Analysis** (Steps 621-700)
- 094: STFT Implementation
- 095: Window Function
- 096: Hop Size
- 097: Band Definitions
- 098: Band Energy Extraction
- 099: dB Conversion
- 100: Median Calculation

**Section 5B: Mud Detector** (Steps 701-760)
- 101: Mud Ratio Calculation
- 102: Activity Mask Integration
- 103: Confidence Logic
- 104: Frequency Bin Find
- 105: Persistence Key

**Section 5C: EQ Eight Adapter** (Steps 761-850)
- 106: EQ Adapter File
- 107: Band Param Regex
- 108: Find Band Params
- 109: Frequency Converter
- 110: Gain Converter
- 111: Q Converter
- 112: Set Band Cut Method
- 113: Enable Band Method

**Section 5D: EQ Action Apply** (Steps 851-900)
- 114: EQ Action Type
- 115: Band Slot Assignment
- 116: Apply Sequence
- 117: Verify Band Settings
- 118: Integration Test

### PART 6: PHASE 4 - FULL SUITE (Steps 901-1200)
Add all remaining detectors and iteration loop.

**Section 6A: Remaining Detectors** (Steps 901-1020)
- 119: Harsh Detector
- 120: Sibilance Detector
- 121: Rumble Detector
- 122: Stereo Detector
- 123: Reverb Tail Detector

**Section 6B: Rule Engine Complete** (Steps 1021-1100)
- 124: Rule Priority Order
- 125: Track Role Gating
- 126: Confidence Thresholds
- 127: Severity Buckets
- 128: Action Budget
- 129: Mild Report-Only

**Section 6C: Iteration Loop** (Steps 1101-1180)
- 130: Iteration Counter
- 131: Violation History
- 132: Unfixable Detection
- 133: Stop Conditions
- 134: Loop Logic

**Section 6D: Verification Criteria** (Steps 1181-1200)
- 135: LUFS Tolerance
- 136: Peak Tolerance
- 137: Stem Peaks Check
- 138: Severe Violations Check
- 139: Pass/Fail Logic

### PART 7: PHASE 5 - ALBUM BATCH (Steps 1201-1350)
Process multiple songs, error handling, validation.

**Section 7A: Album Job** (Steps 1201-1260)
- 140: Album Batch Script
- 141: Song Directory Loop
- 142: Per-Song Polish
- 143: Error Handling
- 144: Continue on Failure

**Section 7B: Validation Command** (Steps 1261-1310)
- 145: Track Names Check
- 146: Device Chain Check
- 147: Export Policy Check
- 148: File Presence Check
- 149: Validation Report

**Section 7C: Timeline Placeholder** (Steps 1311-1340)
- 150: Timeline JSON Schema
- 151: BPM Extract
- 152: Length Calculate
- 153: Markers Extract (optional)
- 154: Timeline Save

**Section 7D: Final Testing** (Steps 1341-1350)
- 155: Three Song Test
- 156: Error Case Test
- 157: Report Review
- 158: Pass/Fail Confirm

### PART 8: HARDENING & POLISH (Steps 1351-1450)
Error messages, edge cases, user documentation.

**Section 8A: Error Messages** (Steps 1351-1390)
- 159: OSC Timeout Errors
- 160: Cache Mismatch Errors
- 161: Missing Device Errors
- 162: Param Not Found Errors
- 163: Export Policy Warnings

**Section 8B: Edge Cases** (Steps 1391-1430)
- 164: Silent Stems Handling
- 165: Missing Tracks Handling
- 166: Crest Factor Edge Cases
- 167: Confidence Edge Cases

**Section 8C: Documentation** (Steps 1431-1450)
- 168: Update README
- 169: Export Checklist
- 170: Workflow Doc
- 171: Troubleshooting Guide

### PART 9: MVP COMPLETE (Steps 1451-1500)
Final validation, album export, completion checklist.

**Section 9A: Full Album Run** (Steps 1451-1480)
- 172: Export All Stems
- 173: Run Album Batch
- 174: Review Reports
- 175: Verify Pass Status

**Section 9B: Final Masters** (Steps 1481-1495)
- 176: Re-Export Masters
- 177: LUFS Verify
- 178: Peak Verify
- 179: Listening Test

**Section 9C: Completion** (Steps 1496-1500)
- 180: Archive Reports
- 181: Backup Live Sets
- 182: Export Masters
- 183: Streaming Prep
- 184: MVP Complete

---

# PART 1: FOUNDATION

## Section 1A: Workspace Preparation

---

### 001: Repository Check

**What:** Verify you're in the correct repo.  
**Why:** Everything depends on being in the right directory.

**Steps:**
1. Open Terminal (Mac: Cmd+Space, type "Terminal", press Enter)
2. Type: `cd ~/Repos/finishline_audio_repo`
3. Press Enter
4. Type: `pwd`
5. Press Enter

**Validation:**
* Output should show: `/Users/trev/Repos/finishline_audio_repo`
* If not, navigate to correct directory first

**Checkpoint:** ✓ You are in the correct repo directory

---

### 002: Directory Creation

**What:** Create all required folders for data storage.  
**Why:** System needs these to store caches, reports, actions, etc.

**Steps:**
1. In Terminal, type: `mkdir -p data/caches data/reports data/actions data/timelines data/profiles`
2. Press Enter
3. Type: `mkdir -p input output tests/unit tests/integration`
4. Press Enter
5. Type: `ls -la`
6. Press Enter

**Validation:**
* You should see folders: `data`, `input`, `output`, `tests`, `src`
* Type: `ls data`
* Press Enter
* Output should show: `caches reports actions timelines profiles`

**Checkpoint:** ✓ All directories created

---

### 003: Dependencies Install

**What:** Install Python packages needed for the system.  
**Why:** Code won't run without these libraries.

**Steps:**
1. Type: `python3 -m venv .venv`
2. Press Enter (wait for completion, ~30 seconds)
3. Type: `source .venv/bin/activate`
4. Press Enter
5. You should see `(.venv)` appear at start of terminal prompt
6. Type: `pip install python-osc pyyaml numpy scipy soundfile pyloudnorm librosa`
7. Press Enter (wait for installation, ~2-3 minutes)

**Validation:**
* Type: `pip list | grep "python-osc"`
* Press Enter
* Output should show: `python-osc` with version number
* Type: `pip list | grep "pyloudnorm"`
* Press Enter
* Output should show: `pyloudnorm` with version number

**Checkpoint:** ✓ All dependencies installed

---

### 004: Config Verification

**What:** Check that config.yaml has all required settings.  
**Why:** System reads settings from this file.

**Steps:**
1. Open Cursor (the IDE)
2. In Cursor, press Cmd+P (Mac) or Ctrl+P (Windows)
3. Type: `config.yaml`
4. Press Enter
5. File should open in editor
6. Scroll through and verify you see these sections:
   * `ableton:`
   * `project:`
   * `tracks:`
   * `devices:`
   * `targets:`
   * `rules:`
   * `activity:`
   * `dynamics:`
   * `thresholds:`
   * `verification:`
   * `export_policy:`
   * `debug:`
   * `analysis:`
   * `confidence_thresholds:`
   * `severity_thresholds:`

**Validation:**
* All 14 sections present
* `port_in: 11000` under `ableton:`
* `port_out: 11001` under `ableton:`

**Checkpoint:** ✓ Config file is complete

---

### 005: AbletonOSC Download

**What:** Download the control script that lets Python talk to Ableton.  
**Why:** Without this, there's no bridge between your code and Live.

**Steps:**
1. Open web browser (Safari, Chrome, etc.)
2. Go to: `https://github.com/ideoforms/AbletonOSC`
3. Click green "Code" button (top right)
4. Click "Download ZIP"
5. Wait for download to complete
6. Open Finder
7. Go to Downloads folder
8. Find `AbletonOSC-main.zip`
9. Double-click to unzip
10. You should see folder named `AbletonOSC-main`

**Validation:**
* Folder `AbletonOSC-main` exists in Downloads
* Inside it, you should see files like `AbletonOSC.py`, `README.md`, etc.

**Checkpoint:** ✓ AbletonOSC downloaded and unzipped

---

### 006: AbletonOSC Install

**What:** Copy AbletonOSC into Ableton's Remote Scripts folder.  
**Why:** Ableton only loads scripts from this specific location.

**Steps:**
1. Open Finder
2. Go to: `/Users/trev/Music/Ableton/User Library`
   * (If you can't find it, press Cmd+Shift+G and paste the path)
3. Look for folder named `Remote Scripts`
4. If it doesn't exist:
   * Right-click in the folder
   * Select "New Folder"
   * Name it exactly: `Remote Scripts`
5. Open the `Remote Scripts` folder
6. Go back to Downloads folder
7. Find `AbletonOSC-main` folder
8. Rename it to just: `AbletonOSC` (remove the `-main` part)
9. Drag the `AbletonOSC` folder into `Remote Scripts` folder
10. Release

**Validation:**
* Path should now exist: `/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC`
* Inside `AbletonOSC` folder, you should see `AbletonOSC.py` file

**Checkpoint:** ✓ AbletonOSC installed in Remote Scripts

---

### 007: Ableton Preferences

**What:** Enable AbletonOSC as a control surface in Ableton Live.  
**Why:** Ableton needs to activate the script before it starts listening.

**Steps:**
1. Open Ableton Live
2. Wait for it to fully load (splash screen disappears)
3. Click "Live" menu (top left, next to Apple menu)
4. Click "Preferences..." (or press Cmd+,)
5. Preferences window opens
6. Click "Link Tempo MIDI" tab (left sidebar)
7. Look for "Control Surface" dropdowns (upper section)
8. Find the first empty dropdown (should say "None")
9. Click it
10. Scroll down the list
11. Find and click "AbletonOSC"
12. Leave "Input" and "Output" dropdowns as "None"
13. Look at bottom right of Ableton's main window

**Validation:**
* Status bar at bottom right should show yellow text: "Listening for OSC on port 11000"
* If you don't see it, close and restart Ableton
* After restart, yellow text should appear

**Checkpoint:** ✓ AbletonOSC enabled and listening

---

### 008: OSC Test

**What:** Send a test message to confirm OSC is working.  
**Why:** If this fails, nothing else will work.

**Cursor Mode:** Agent  
**Model:** Claude Sonnet 4.5

**Steps:**
1. Go back to Cursor
2. Press Cmd+L to open Cursor chat
3. Click "Agent" mode (top of chat)
4. Copy this prompt EXACTLY:

```
Create a test script at tests/test_osc_ping.py that:
1. Imports python-osc
2. Creates UDP client to 127.0.0.1:11000
3. Sends /live/test message
4. Prints success
Run it and confirm we get no errors.
```

5. Paste into chat
6. Press Enter
7. Wait for Cursor to create the file and run it
8. Look at output

**Validation:**
* You should see output like: `OSC test message sent to port 11000`
* No errors about "connection refused" or "module not found"
* Check Ableton status bar - it might briefly flash "OSC message received"

**Checkpoint:** ✓ OSC communication working

---

### 009: Test Song Selection

**What:** Choose one song to use for testing throughout development.  
**Why:** Need consistent test data to validate each phase.

**Steps:**
1. Think about your album
2. Pick the simplest song (fewest tracks, most straightforward mix)
3. Open that song in Ableton Live
4. Save it with a clear name like: `TestSong_FinishLine.als`
5. Note the song name (you'll use this in config)

**Validation:**
* Song is open in Ableton
* It's saved with a clear name
* You remember which song this is

**Checkpoint:** ✓ Test song selected and open

---

### 010: Track Standardization

**What:** Rename and organize tracks to match the required stem names.  
**Why:** System expects exact track names to know what to control.

**Steps:**
1. In Ableton, look at your tracks list (left side or bottom of Clip View)
2. Find your lead vocal track/group
3. Right-click on track name
4. Select "Rename"
5. Type exactly: `VOCAL_LEAD`
6. Press Enter
7. Repeat for background vocals → name: `VOCAL_BG`
8. Repeat for kick → name: `KICK`
9. Repeat for drums (excluding kick) → name: `DRUMS`
10. Repeat for bass → name: `BASS`
11. Repeat for music/instruments → name: `MUSIC`
12. Repeat for FX/fills → name: `FX`
13. If you have a reverb return, name it: `REVERB_RETURN`
14. Find or create your master track
15. If it's a group acting as pre-master, name it: `ALBUM_MASTER`

**Validation:**
* You should now see exactly these track names:
  * VOCAL_LEAD
  * VOCAL_BG
  * KICK
  * DRUMS
  * BASS
  * MUSIC
  * FX
  * REVERB_RETURN (optional)
  * ALBUM_MASTER (or Master)
* If a role doesn't exist in your song, that's okay - note it down

**Checkpoint:** ✓ All tracks renamed to standard names

---

## Section 1B: Stem Export

**CRITICAL:** Follow these export settings EXACTLY every time. Any deviation invalidates all analysis.

---

### 011: Export Settings Lock

**What:** Configure Ableton's export settings to the required specifications.  
**Why:** Wrong export settings = wrong measurements = wrong corrections.

**Steps:**
1. In Ableton, click "File" menu
2. Click "Export Audio/Video..."
3. Export dialog opens
4. **Sample Rate:** Click dropdown, select "48000"
5. **File Type:** Click dropdown, select "WAV"
6. **Bit Depth:** Click dropdown, select "24"
7. **Dither Options:** Click dropdown, select "None"
8. **Normalize:** Make sure this checkbox is UN-checked (very important!)
9. **Create Analysis Files:** UN-check this
10. **Rendered Track:** We'll change this for each stem (see next steps)
11. Leave dialog open

**Validation:**
* Sample Rate: 48000
* File Type: WAV
* Bit Depth: 24
* Dither: None
* Normalize: UNCHECKED (this is critical)

**DO NOT CLICK EXPORT YET**

**Checkpoint:** ✓ Export settings configured correctly

---

### 012: Vocal Lead Export

**What:** Export the VOCAL_LEAD stem.  
**Why:** First required stem for analysis.

**Steps:**
1. Export dialog should still be open from previous step
2. **Rendered Track:** Click dropdown
3. Find and select "VOCAL_LEAD"
4. **File Name:** Type: `VOCAL_LEAD`
5. **Export Location:** Click "Browse" or "Choose"
6. Navigate to: `~/Repos/finishline_audio_repo/input`
7. Create new folder named: `TestSong` (or your song name)
8. Inside `TestSong`, create folder named: `stems`
9. Select the `stems` folder
10. Click "Choose" or "Select Folder"
11. **Start Time:** Should say "1.1.1" (bar 1, beat 1, tick 1)
12. **End Time:** Should show the end of your song
13. Click "Export"
14. Wait for export to complete (progress bar)
15. Dialog closes when done

**Validation:**
* Navigate in Finder to: `~/Repos/finishline_audio_repo/input/TestSong/stems`
* You should see file: `VOCAL_LEAD.wav`
* File size should be several MB (not tiny)
* Double-click to open in QuickTime/Spotify to confirm it plays audio

**Checkpoint:** ✓ VOCAL_LEAD.wav exported

---

### 013: Vocal BG Export

**What:** Export the VOCAL_BG stem.  
**Why:** Second required stem.

**Steps:**
1. Repeat steps from 012, but:
2. **Rendered Track:** Select "VOCAL_BG"
3. **File Name:** Type: `VOCAL_BG`
4. Use same export location: `~/Repos/finishline_audio_repo/input/TestSong/stems`
5. Click "Export"

**Validation:**
* File `VOCAL_BG.wav` exists in `stems` folder
* File plays audio when opened

**Checkpoint:** ✓ VOCAL_BG.wav exported

---

### 014: Kick Export

**What:** Export KICK stem.

**Steps:**
1. **Rendered Track:** Select "KICK"
2. **File Name:** Type: `KICK`
3. Click "Export"

**Validation:**
* File `KICK.wav` exists

**Checkpoint:** ✓ KICK.wav exported

---

### 015: Drums Export

**What:** Export DRUMS stem (excludes kick).

**Steps:**
1. **Rendered Track:** Select "DRUMS"
2. **File Name:** Type: `DRUMS`
3. Click "Export"

**Validation:**
* File `DRUMS.wav` exists

**Checkpoint:** ✓ DRUMS.wav exported

---

### 016: Bass Export

**What:** Export BASS stem.

**Steps:**
1. **Rendered Track:** Select "BASS"
2. **File Name:** Type: `BASS`
3. Click "Export"

**Validation:**
* File `BASS.wav` exists

**Checkpoint:** ✓ BASS.wav exported

---

### 017: Music Export

**What:** Export MUSIC stem.

**Steps:**
1. **Rendered Track:** Select "MUSIC"
2. **File Name:** Type: `MUSIC`
3. Click "Export"

**Validation:**
* File `MUSIC.wav` exists

**Checkpoint:** ✓ MUSIC.wav exported

---

### 018: FX Export

**What:** Export FX stem.

**Steps:**
1. **Rendered Track:** Select "FX"
2. **File Name:** Type: `FX`
3. Click "Export"

**Validation:**
* File `FX.wav` exists

**Checkpoint:** ✓ FX.wav exported

---

### 019: Reverb Return Export

**What:** Export REVERB_RETURN stem (optional but recommended).  
**Why:** Needed for reverb tail detection.

**Steps:**
1. If you have a reverb return track:
2. **Rendered Track:** Select "REVERB_RETURN"
3. **File Name:** Type: `REVERB_RETURN`
4. Click "Export"
5. If you don't have a reverb return, skip this step

**Validation:**
* File `REVERB_RETURN.wav` exists (if you exported it)

**Checkpoint:** ✓ REVERB_RETURN.wav exported (or skipped if N/A)

---

### 020: Master Export

**What:** Export Master/premaster stem for reference.

**Steps:**
1. **Rendered Track:** Select "ALBUM_MASTER" or "Master"
2. **File Name:** Type: `Master`
3. Click "Export"

**Validation:**
* File `Master.wav` exists

**Checkpoint:** ✓ Master.wav exported

---

## Section 1C: Validation Checkpoint

---

### 021: File Presence Check

**What:** Confirm all 9 required files exist.  
**Why:** Missing files will cause errors later.

**Steps:**
1. Open Finder
2. Navigate to: `~/Repos/finishline_audio_repo/input/TestSong/stems`
3. Look at the files
4. Count them

**Validation:**
You should see exactly these files:
1. VOCAL_LEAD.wav
2. VOCAL_BG.wav
3. KICK.wav
4. DRUMS.wav
5. BASS.wav
6. MUSIC.wav
7. FX.wav
8. REVERB_RETURN.wav
9. Master.wav

Total: 9 files (8 stems + 1 master)

**If any are missing:** Go back and export them now.

**Checkpoint:** ✓ All 9 files present

---

### 022: Sample Rate Verify

**What:** Check that all files are 48kHz.  
**Why:** Mismatched sample rates break analysis.

**Steps:**
1. In Finder, right-click on `VOCAL_LEAD.wav`
2. Select "Get Info"
3. Look for "Sample Rate" or expand "More Info"
4. Should say: "48000 Hz" or "48 kHz"
5. Close info window
6. Repeat for one or two other files to spot-check

**Validation:**
* All checked files show 48000 Hz

**Checkpoint:** ✓ Sample rate is correct

---

### 023: Bit Depth Verify

**What:** Check that files are 24-bit.

**Steps:**
1. In Finder, right-click on `VOCAL_LEAD.wav`
2. Select "Get Info"
3. Look for "Bit Depth" or "Bits per Sample"
4. Should say: "24-bit" or "24"

**Validation:**
* File is 24-bit

**Checkpoint:** ✓ Bit depth is correct

---

### 024: Length Consistency

**What:** Confirm all stems are the same length.  
**Why:** Different lengths cause sync issues.

**Steps:**
1. In Finder, select all 9 WAV files
2. Right-click
3. Select "Get Info"
4. Multiple info windows open
5. Look at "Duration" or "Length" in each
6. They should all show the same time (e.g., "3:45" or "4:12")

**Validation:**
* All files have identical duration

**Checkpoint:** ✓ All stems are same length

---

### 025: Waveform Visual Check

**What:** Open one stem and look at the waveform.  
**Why:** Catch obvious export errors (silence, clipping, normalization).

**Steps:**
1. Double-click `VOCAL_LEAD.wav` to open in QuickTime or system player
2. Play it - confirm you hear audio
3. Close player
4. Drag `VOCAL_LEAD.wav` onto Ableton icon in dock (or open in any DAW)
5. Look at waveform
6. Check that:
   * It's not silent (flat line)
   * It's not clipping (hitting 0 dBFS = top and bottom of waveform)
   * It's not normalized (peaks don't all hit -0.1 dBFS exactly)
7. Close without saving

**Validation:**
* Waveform looks normal
* Audio plays correctly
* Not clipped, not normalized

**Checkpoint:** ✓ Stems exported correctly

---

**END OF PART 1**

You now have:
* ✓ Workspace set up
* ✓ AbletonOSC installed and working
* ✓ Test song standardized
* ✓ All stems exported with correct settings
* ✓ Files validated

**Next:** Part 2 - Build the OSC bridge

**Estimated time so far:** 2-3 hours

**Remaining time:** 14-21 hours

---

*[This guide continues for 1500+ total steps through Phase 5. The full document would be approximately 30,000-40,000 words. Would you like me to continue generating the remaining parts, or should we test this format first?]*

---

## APPENDIX A: Quick Reference

### Export Settings Checklist
Every export must use:
- [ ] Sample Rate: 48000
- [ ] File Type: WAV
- [ ] Bit Depth: 24
- [ ] Dither: None
- [ ] Normalize: UNCHECKED
- [ ] Start: 1.1.1
- [ ] Length: Full song

### Required Stem Names
1. VOCAL_LEAD.wav
2. VOCAL_BG.wav
3. KICK.wav
4. DRUMS.wav
5. BASS.wav
6. MUSIC.wav
7. FX.wav
8. REVERB_RETURN.wav
9. Master.wav

### Cursor Modes
* **Agent Mode:** When implementing code (use for building features)
* **Ask Mode:** When you have questions (use for clarification)
* **Plan Mode:** When designing approach (use for architecture decisions)

### When to Use ChatGPT
1. After Cursor generates a complex implementation → copy to ChatGPT for review
2. When you need alternative perspectives → paste Cursor's plan + ask for feedback
3. For domain-specific questions → paste technical output + ask for explanation

### Model Recommendations
* **Claude Sonnet 4.5:** General implementation, complex logic, architecture
* **Fast Model:** Simple file operations, boilerplate code, testing
* **ChatGPT-4:** Review, alternative perspectives, explanation

### Common Errors & Fixes
**OSC timeout:** Restart Ableton, check port 11000 not in use
**Module not found:** Reactivate venv: `source .venv/bin/activate`
**File not found:** Check you're in correct directory: `pwd`

---

