# Philosophy Alignment Check

This document confirms that all refinements remain consistent with the core philosophy.

---

## The Question ChatGPT Asked (and the answer)

> **"What exactly is a 'stem export' in your workflow?"**

**Answer (now locked in IMPLEMENTATION_SPEC.md Section 0.0):**

Stems are:
* **Post-fader** (volume automation applied)
* **Post-insert-FX** (track's device chain applied)
* **Pre-master-chain** (master bus processing NOT included)
* **Returns policy:** Reverb/delay returns exported as separate stem if tail detection desired, otherwise printed into source stems
* **Routing:** Group tracks only (not individual tracks within groups)

This is **locked for MVP**. Everything downstream depends on this definition.

---

## Core Philosophy Reminder

From `VISION.md`:

> **You define intent.**
> **The system enforces consistency and handles repetition.**
> **Everything becomes addressable and automatable.**
> **Outputs are explainable and logged (reports), not magical.**

---

## Does Every Refinement Pass the Philosophy Test?

### 1. Export Policy (Section 0.1)

**Refinement:** Machine-verifiable tracking in `report.json`, export policy assumed/confirmed fields.

**Philosophy Check:**
* ✅ **Explainable:** Reports show assumed policy, user confirms compliance
* ✅ **You define intent:** User sets export settings, system verifies
* ✅ **Not magical:** Clear documentation of what must be locked

**PASSES** - Makes the "invisible" (export settings) visible in reports.

---

### 2. Action Whitelist (Section 0.2)

**Refinement:** Explicit table of allowed devices/parameters. Hard fail if rule attempts blocked parameter.

**Philosophy Check:**
* ✅ **Enforces consistency:** Same parameters used across all songs
* ✅ **You define intent:** Whitelist defines policy, system enforces
* ✅ **No taste changes:** Blocks Drive, Saturation, Character, etc.
* ✅ **Not magical:** Clear error if policy violated

**PASSES** - This IS the "no taste changes" enforcement mechanism.

---

### 3. Activity Masking with Hysteresis (Section 10.1.5)

**Refinement:** Enter/exit thresholds with minimum duration to prevent flutter.

**Philosophy Check:**
* ✅ **Explainable:** Clear thresholds documented
* ✅ **Handles repetition:** Automated masking for all analysis
* ✅ **Not magical:** Deterministic state machine, not heuristic

**PASSES** - Makes detectors reliable across sparse/dense material.

---

### 4. Crest Factor Protection (Section 10.3.5)

**Refinement:** If crest factor < 6 dB, disable compression, reduce burst sensitivity.

**Philosophy Check:**
* ✅ **Enforces consistency:** Same crest threshold for all songs
* ✅ **Preserves intent:** Doesn't "fix" intentionally loud/compressed material
* ✅ **Explainable:** Report shows crest factor, explains why actions limited

**PASSES** - Prevents system from undoing intentional sound design.

---

### 5. Confidence/Severity Gating (Section 10.5)

**Refinement:** Detectors express uncertainty, rules gate on confidence >= 0.7.

**Philosophy Check:**
* ✅ **Explainable:** Detection outputs include confidence + evidence
* ✅ **You define intent:** Confidence threshold is policy (configurable)
* ✅ **Not magical:** Clearly labeled uncertainty, not hidden AI

**PASSES** - Makes probabilistic nature of audio analysis explicit.

---

### 6. Standardized Detection Schema (Section 10.5)

**Refinement:** `violation_id`, `confidence`, `role_required`, `recommended_action_candidates`.

**Philosophy Check:**
* ✅ **Explainable:** Every detection traceable via violation_id
* ✅ **Addressable:** Can query "show all mud violations"
* ✅ **Separation of concerns:** Detectors suggest, rules decide

**PASSES** - Makes system debuggable and auditable.

---

### 7. Verification Criteria (Section 13.1)

**Refinement:** Pass requires: LUFS ±0.5 dB, peak ±0.1 dB, no severe violations.

**Philosophy Check:**
* ✅ **Explainable:** Clear numbers, tolerances documented
* ✅ **You define intent:** Target values are policy
* ✅ **Repeatable:** Same criteria for all songs

**PASSES** - Objective, measurable success criteria.

---

### 8. Stop Conditions for Unfixable Violations (Section 11.2.5)

**Refinement:** If same violation persists after 2 attempts, mark "unfixable", report-only.

**Philosophy Check:**
* ✅ **Handles repetition:** Automated detection of persistent issues
* ✅ **Not magical:** Clear logic, logged in report
* ✅ **Explainable:** User sees "unfixable" status + reason

**PASSES** - Prevents infinite loops, surfaces real issues.

---

### 9. Timeline.json Placeholder (Section 18)

**Refinement:** Passive artifact with BPM, length, markers array (empty for now).

**Philosophy Check:**
* ✅ **Addressable:** Future features (visuals, sections) can reference it
* ✅ **Not magical:** Just data, no processing in MVP
* ✅ **Explainable:** Plain JSON, human-readable

**PASSES** - Future-proofs without adding complexity now.

---

### 10. Export Policy Tracking in Reports (Section 0.1)

**Refinement:** `report.json` includes `export_policy` block with assumed settings.

**Philosophy Check:**
* ✅ **Explainable:** Report shows what was assumed
* ✅ **Logged:** Audit trail of export settings used
* ✅ **Addressable:** Can query "which songs had normalization on?"

**PASSES** - Makes implicit assumptions explicit.

---

### 11. Parameter Converters (Section 9.2)

**Refinement:** Device adapters expose `set_gain_db()`, not `set_raw_param()`.

**Philosophy Check:**
* ✅ **Explainable:** Actions logged in dB/Hz (musical units)
* ✅ **Repeatable:** Same dB value produces same result across versions
* ✅ **Not magical:** Conversion logic is deterministic

**PASSES** - Abstracts away Live version differences correctly.

---

### 12. True-Peak Labeling (Section 10.2)

**Refinement:** Always labeled as `true_peak_estimate_db`, never just "true_peak".

**Philosophy Check:**
* ✅ **Explainable:** Report clarifies "estimate, not ITU compliant"
* ✅ **Not magical:** Doesn't claim more accuracy than it has

**PASSES** - Honest about limitations.

---

### 13. Throttling (Section 12.1)

**Refinement:** 25ms delay between OSC parameter sets.

**Philosophy Check:**
* ✅ **Repeatable:** Prevents UDP packet loss issues
* ✅ **Not magical:** Simple delay, not heuristic

**PASSES** - Practical reliability measure.

---

### 14. Cache Fingerprinting (Section 8.5)

**Refinement:** Hash of track names + device counts, refuse to apply if mismatch.

**Philosophy Check:**
* ✅ **Enforces consistency:** Prevents applying wrong actions
* ✅ **Explainable:** Clear error if set changed
* ✅ **Not magical:** Deterministic hash comparison

**PASSES** - Safety mechanism that prevents corruption.

---

### 15. Stem Definition Lock (Section 0.0)

**Refinement:** Explicit definition (post-fader, post-FX, pre-master, group tracks).

**Philosophy Check:**
* ✅ **You define intent:** User chooses this definition once
* ✅ **Enforces consistency:** Same definition for all songs
* ✅ **Explainable:** Documented, not inferred

**PASSES** - Foundation for all analysis.

---

## Philosophy Alignment Score: 15/15 ✅

**Every refinement passes the philosophy test.**

---

## What Changed vs. Original Philosophy?

**Nothing fundamental.** The refinements ADD:
* More explicitness (export policy, stem definition)
* More guardrails (crest factor, confidence gating)
* More clarity (verification criteria, stop conditions)
* More future-proofing (timeline.json)

But the core philosophy is **unchanged**:
* You still define intent (targets, thresholds, policy)
* System still enforces consistency (same rules, same actions)
* Everything still logged and explainable (reports, violation_ids)
* No taste changes still enforced (action whitelist)

---

## Future Enhancements Philosophy Check

From `FUTURE_ENHANCEMENTS.md`, do Phase 2-5 features align?

### Phase 2: Enhanced Audio Automation
* **Album consistency:** ✅ Enforces YOUR median across songs
* **Programmatic export:** ✅ Removes manual error, repeatability
* **Section-aware analysis:** ✅ Uses YOUR markers, not invented

### Phase 3: Show Control
* **Event detection:** ✅ READS musical data, doesn't CHANGE it
* **Lighting output:** ✅ YOU write show script, system executes timing
* **Choreography:** ✅ Coordination tool, not generative

### Phase 4: Narrative & Release
* **Lyric integration:** ✅ Organizational data, not analysis
* **Multi-format export:** ✅ Automated pipeline from YOUR source
* **Metadata:** ✅ Central registry, consistent across formats

### Phase 5: Intelligence (Optional)
* **Anomaly detection:** ✅ FLAGS issues, doesn't auto-fix
* **Adaptive thresholds:** ✅ Learned from YOUR approved references
* **Setlist optimizer:** ✅ Constraint solver, not taste maker

**All future features pass philosophy test.**

---

## What Would VIOLATE the Philosophy?

Examples of features we **will not** build:

### ❌ "Make it sound like Drake"
* Violates: "No taste changes"
* Why: Replaces YOUR sound with someone else's

### ❌ "AI suggests better chord progression"
* Violates: "You define intent"
* Why: Changes creative decisions

### ❌ "Auto-master to maximize loudness"
* Violates: "Enforces standards YOU believe in"
* Why: Chases metrics instead of your target

### ❌ "Boost vocals because they sound quiet"
* Violates: "Measurable violations only"
* Why: "Sounds quiet" is subjective, not measurable

### ❌ "Add reverb to improve depth"
* Violates: "No new devices"
* Why: Changes creative sound design

### ❌ "Black box neural mastering"
* Violates: "Explainable, logged outputs"
* Why: Can't audit what it did or why

---

## Summary: Everything Is Aligned

1. ✅ All 15 refinements pass philosophy test
2. ✅ Core philosophy unchanged
3. ✅ Future enhancements (Phase 2-5) all aligned
4. ✅ Clear examples of what would violate philosophy
5. ✅ Stem definition locked (post-fader, post-FX, pre-master)
6. ✅ Action whitelist enforces "no taste"
7. ✅ Reports make everything explainable
8. ✅ User defines intent, system enforces consistency

**The plan is philosophically sound and ready to execute.**
