# Plan Summary & Next Steps

This document summarizes the feedback evaluation and current state of planning.

---

## What Changed Based on Feedback

### ChatGPT Feedback Evaluation

**What we ACCEPTED and integrated:**

1. ✅ **Export settings fragility** - Added as Section 0 "Critical Prerequisites" with machine-verifiable tracking
2. ✅ **Stem definition** - Locked specification (post-fader, post-FX, pre-master-chain)
3. ✅ **Action whitelist** - Explicit table of allowed devices/params (enforces "no taste")
4. ✅ **Activity masking with hysteresis** - Enter/exit thresholds prevent flutter
5. ✅ **Crest factor protection** - Prevents over-optimization of compressed material
6. ✅ **Track role gating** - Enhanced rule engine to require role matching
7. ✅ **Parameter converters** - Device adapters expose musical units (dB, Hz), not raw values
8. ✅ **Cache fingerprinting** - Validation before applying actions
9. ✅ **UDP throttling** - 25ms delay between parameter sets
10. ✅ **Confidence scoring** - Detectors output confidence, rules gate on it
11. ✅ **Stop conditions** - Detect unfixable violations
12. ✅ **Verification criteria** - Clear pass/fail numbers with tolerances
13. ✅ **Timeline placeholder** - Minimal JSON for future visual features
14. ✅ **Standardized Detection schema** - violation_id, confidence, role_required
15. ✅ **True-peak labeling** - Always marked as "estimate" in reports

**What we REFINED (ChatGPT's corrections to our corrections):**

1. ✅ **Timeline.json** - Not "overengineering", but minimal passive artifact (BPM, length, markers array) - ACCEPTED
2. ✅ **Policy versioning** - Not separate doc, but added to spec header and action whitelist - ACCEPTED
3. ✅ **Verification criteria** - Added specific numbers and tolerances - ACCEPTED

**What we DEFERRED (post-MVP):**

1. ⏸️ **Album-level consistency** - Phase 2 feature, documented in FUTURE_ENHANCEMENTS.md
2. ⏸️ **Programmatic export** - Phase 2 feature, currently user responsibility
3. ⏸️ **Section/marker awareness** - Phase 2 feature (uses timeline.json)
4. ⏸️ **Reference profile system (full)** - Phase 2 feature, basic version in MVP
5. ⏸️ **Undo mechanism** - Phase 2 feature, user keeps Live set backups

**What we CLARIFIED (was already correct):**

* True-peak is explicitly an "estimate" in original spec, not claiming ITU compliance
* Reverb tail detection already mentioned requiring dedicated stem
* Band detection reliability already has severity buckets and clamps

---

## Documentation Structure (Final)

### Three Core Files

1. **`VISION.md`** (Philosophy - 95% unchanged)
   - What you're building and why
   - Core philosophy: taste vs compliance
   - Future directions (visuals, narrative, promotion)
   - **Added**: "What This Is NOT" section to clarify boundaries

2. **`IMPLEMENTATION_SPEC.md`** (Technical Plan - significantly enhanced)
   - **Added Section 0**: Critical Prerequisites (export policy)
   - **Enhanced**: Cache fingerprinting and validation
   - **Enhanced**: Device adapters with parameter converters
   - **Enhanced**: Activity masking for silence handling
   - **Enhanced**: Confidence/severity gating in rules
   - **Enhanced**: Stop conditions for iteration loop
   - **Enhanced**: Throttling and verification in apply pipeline
   - **Added Section 18**: Known Limitations (MVP)

3. **`TECHNICAL_CONSIDERATIONS.md`** (Edge Cases & Unknowns)
   - 19 documented gotchas and nuances
   - Prioritized by "must address" vs "nice to have"
   - Explains WHY each consideration matters
   - Acts as reference during implementation

---

## What's Ready to Code (Priority Order)

### Phase 0: Integration Confidence (1-2 hours)
**Goal**: Verify OSC bridge works end-to-end

- [ ] Install AbletonOSC (see Section B1 of IMPLEMENTATION_SPEC)
- [ ] Implement basic OSC RPC (ping, get tracks list)
- [ ] Read one device, one parameter
- [ ] Set one parameter value
- [ ] Verify parameter changed by re-reading
- [ ] **Blocker if fails**: OSC setup or Live version incompatibility

**You can do this in parallel with manual setup (standardize one set, export stems).**

### Phase 1: First Closed Loop (4-6 hours)
**Goal**: Minimal devices, one real action, end-to-end

- [ ] Implement scanner → `model_cache.json` (with fingerprint)
- [ ] Implement WAV load + peak + RMS
- [ ] Implement activity masking with hysteresis
- [ ] Implement crest factor calculation
- [ ] Implement headroom detector (peak > -6dB, includes confidence)
- [ ] Implement Utility adapter with `set_gain_db()` converter
- [ ] Generate `actions.json` with ONE action (gain trim only)
- [ ] Apply action with throttling (25ms) and verification
- [ ] Generate `report.json` with pass/fail status
- [ ] **Success criteria**: Gain knob moves in Live, verify confirms change, report shows metrics

### Phase 2: Add Simple Device (2-4 hours)
**Goal**: Add limiter ceiling (easy param mapping, high value)

- [ ] Implement limiter adapter (find "Ceiling" param, set to -1.0 dB)
- [ ] Add master limiter action to rule engine
- [ ] Test on master track
- [ ] **Success criteria**: Master limiter ceiling sets correctly, verify reads back -1.0 dB

### Phase 3: EQ Eight + Mud Detection (6-8 hours)
**Goal**: Complex param mapping, first corrective EQ

- [ ] Implement LUFS (pyloudnorm)
- [ ] Implement STFT + band energy extraction
- [ ] Implement mud detector (with confidence scoring, track role gating)
- [ ] Implement EQ Eight adapter for 1 band peaking cut (freq, gain, Q, on)
- [ ] Test converter functions (Hz → raw param, dB → raw param)
- [ ] Generate one EQ action, apply, verify
- [ ] **Success criteria**: EQ band 1 shows correct freq/gain/Q in Live

### Phase 4: Core Detection Loop (6-8 hours)
**Goal**: Multiple detectors, iteration loop, stop conditions

- [ ] Implement remaining detectors (harsh, sibilance, rumble - all with confidence)
- [ ] Implement standardized Detection schema (violation_id, confidence, role_required)
- [ ] Implement rule engine with:
   * Track role gating
   * Confidence/severity thresholds
   * Priority ordering
   * Max 2 EQ moves per track
- [ ] Implement iteration loop with stop conditions:
   * Max 2 iterations
   * Unfixable violation detection (persists after 2 attempts)
   * Clamp exceeded
- [ ] Implement verification pass/fail criteria
- [ ] **Success criteria**: Full polish_song job runs, stops cleanly, report shows before/after

### Phase 5: Album Batch + Hardening (4-6 hours)
**Goal**: Multi-song processing, error handling, validation

- [ ] Implement album batch (`polish_album`)
- [ ] Implement cache validation (fingerprint mismatch detection)
- [ ] Implement validation command (track names, device chains, export policy)
- [ ] Add action whitelist enforcement (block non-allowed parameters)
- [ ] Test failure modes (OSC timeout, missing devices, wrong track names)
- [ ] Generate timeline.json placeholder (BPM, length, empty markers array)
- [ ] **Success criteria**: Process 3-5 songs, consistent reports, clear errors on failures

---

## Current State of Repository

```
/Users/trev/Repos/finishline_audio_repo/
├── VISION.md                        ✅ Updated (added "What This Is NOT")
├── IMPLEMENTATION_SPEC.md           ✅ Updated (17 major enhancements)
├── TECHNICAL_CONSIDERATIONS.md      ✅ New (19 documented edge cases)
├── FUTURE_ENHANCEMENTS.md           ✅ New (Phase 2-5 roadmap)
├── PLAN_SUMMARY.md                  ✅ Updated (this file, refined phases)
├── README.md                        ⚠️  Basic skeleton (needs update after Phase 1)
├── config.yaml                      ✅ Updated (all new settings integrated)
├── requirements.txt                 ⚠️  Minimal (needs full deps)
└── src/
    └── finishline_audio/
        ├── cli.py                   📝 Stub exists
        ├── config.py                📝 Stub exists
        ├── osc/
        │   └── rpc.py              📝 Stub exists
        └── ableton/
            └── api.py              📝 Stub exists
```

**Legend:**
- ✅ Complete and reviewed
- ⚠️  Needs expansion
- 📝 Stub exists, needs implementation

---

## Before You Write Any Code

### 1. Manual Setup (do this first)

- [ ] Download AbletonOSC from GitHub
- [ ] Install to Live's Remote Scripts folder
- [ ] Enable AbletonOSC in Live preferences
- [ ] Verify Live shows "Listening on port 11000"
- [ ] Open one song in Live
- [ ] Standardize track names (VOCAL_LEAD, BASS, DRUMS, etc.)
- [ ] Add Utility (device 0) and EQ Eight (device 1) to each controlled track
- [ ] Export stems following Section 0 export policy (normalization OFF!)
- [ ] Place stems in `input/TestSong/stems/`

### 2. Create Directory Structure

```bash
mkdir -p data/{caches,reports,actions,profiles}
mkdir -p input/TestSong/stems
mkdir -p output/TestSong
mkdir -p src/finishline_audio/{osc,ableton/devices,analysis,rules,jobs}
mkdir -p tests/{unit,integration}
```

### 3. Update Dependencies

Add to `requirements.txt`:
```
python-osc>=1.8.1
pyyaml>=6.0.1
numpy>=1.24.0
scipy>=1.10.0
soundfile>=0.12.0
pyloudnorm>=0.1.0
librosa>=0.10.0  # for frame utility functions
```

### 4. Verify Config

The `config.yaml` has been updated with all new settings:
- Activity masking with hysteresis
- Crest factor protection
- Verification criteria
- Export policy tracking
- Debug throttling settings

---

## Decision Log

### Decisions Made

1. **Export policy is user responsibility** (no programmatic enforcement in MVP)
   - Rationale: AbletonOSC export control is complex, document checklist instead
   - Future: Add export automation in Phase 2

2. **True-peak is estimate only** (4x oversample, not ITU-R BS.1770-4)
   - Rationale: MVP doesn't need broadcast compliance
   - Future: Add proper true-peak library if needed

3. **Reverb tail detection is optional** (requires dedicated stem)
   - Rationale: Many projects don't isolate returns
   - Future: Add AbletonOSC return track rendering

4. **No undo mechanism in MVP** (user keeps Live set backups)
   - Rationale: Adds complexity, manual workflow is safer initially
   - Future: Store "pre-correction snapshot" actions to reverse changes

5. **Album consistency is Phase 2** (no cross-song median targeting)
   - Rationale: MVP proves single-song automation works first
   - Future: Compute album-level metrics and normalize toward median

6. **Confidence gating is mandatory** (not optional)
   - Rationale: Prevents false positives from breaking mixes
   - Implementation: All rules check `confidence >= 0.7` before applying

### Open Questions (to resolve during implementation)

- [ ] **Utility gain parameter mapping**: Is it linear dB or normalized 0-1? (verify by scanning)
- [ ] **EQ Eight parameter names**: Do they vary between Live 10/11/12? (test on your version)
- [ ] **Limiter ceiling param name**: "Ceiling" or "Ceiling (dB)"? (verify by scanning)
- [ ] **OSC message rate limit**: Is 25ms throttle enough or too slow? (test with rapid actions)
- [ ] **Stem export definition**: Confirm post-fader, post-FX, pre-master-chain works for your workflow

---

## Success Criteria for MVP

The MVP is complete when:

1. ✅ OSC bridge works (ping, scan, set param, verify)
2. ✅ One song polishes successfully (headroom + mud correction at minimum)
3. ✅ Actions generate predictable, auditable results
4. ✅ Report shows before/after metrics
5. ✅ Cache validation prevents applying to wrong set
6. ✅ Iteration loop stops cleanly (no infinite loops)
7. ✅ Batch mode processes 3+ songs without manual intervention
8. ✅ Error messages are clear when things fail

**Non-goals for MVP** (explicitly out of scope):
- ❌ Perfect true-peak measurement
- ❌ Section-aware analysis
- ❌ Album-level consistency
- ❌ Visual/show control features
- ❌ Programmatic export from Live
- ❌ Undo mechanism

---

## What You Said About Implementation

> "the actual programming itself will be kind of like a base level in the sense that whatever the standard is, that's being applied with Python and whatever socket that connects to Ableton"

**You're right.** The programming patterns are straightforward:
- OSC client/server (standard python-osc library)
- JSON serialization (standard dataclasses + json)
- Audio analysis (standard numpy/scipy)
- Parameter mapping (lookups + converters)

**The complexity is domain knowledge:**
- What export settings invalidate measurements
- When silence breaks detectors
- Why track roles matter for rules
- How parameter scales work in Ableton devices
- What confidence levels mean for different detections

That's why we documented TECHNICAL_CONSIDERATIONS.md—so the domain knowledge is captured BEFORE coding starts.

---

## Next Action

**You have two options:**

### Option A: Start Phase 0 (OSC proof of concept) now
I implement the OSC RPC layer and test ping/read/write with your Live set.

### Option B: You do manual setup first, then I code
You install AbletonOSC, standardize one song, export stems—then I build the automation against known-good test data.

**Recommendation: Option B is safer.** Ensures we're building against real-world conditions from the start.

---

## Final Thoughts on the Feedback

**ChatGPT's feedback was 70% excellent, 20% overcomplicated, 10% nitpicking.**

The **excellent parts** (export policy, silence masking, role gating, confidence scoring) are now integrated and will prevent major issues.

The **overcomplicated parts** (Project Graph, separate policy doc) were architectural astronautics that would've slowed you down without adding value.

The **nitpicking parts** (pyloudnorm true-peak) were technically correct but addressed things the spec already acknowledged.

**Your instinct to refine the plan BEFORE coding is exactly right.** Most projects fail because they start coding before understanding the domain. You're doing the opposite: capturing unknowns, documenting edge cases, and building consensus on what "done" looks like.

The plan is now tight, scoped, and ready to execute.
