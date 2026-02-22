# Technical Considerations & Edge Cases

This document captures the nuances, gotchas, and "unknown unknowns" that emerge when bridging audio analysis and Live automation.

---

## 1) Export Settings Fragility

### The Problem
If Ableton export settings vary, analysis becomes unreliable:
- **Normalization** changes peak values
- **Dither** adds noise floor variations
- **Sample rate conversion** affects frequency content
- **Export with master FX** changes what you're measuring

### The Solution
Lock export policy in documentation:
- Normalization: OFF
- Dither: None (or consistent)
- Sample Rate: 48000 Hz
- Bit Depth: 24-bit minimum
- Length: consistent across stems (pad silence if needed)

### How to Enforce
- Document export checklist
- Later: programmatic export via AbletonOSC (future enhancement)

---

## 2) Silence Breaks Ratio-Based Metrics

### The Problem
Computing `E(mud_band) / E(reference_band)` when both are near zero gives unstable results. Silence or very quiet passages will false-trigger mud/harsh/rumble detectors.

### The Solution
Implement **activity masking**:
- Compute short-window RMS (50ms frames)
- Threshold: -50 dBFS
- Create binary mask: `[True if RMS > threshold]`
- Detectors ignore frames where `mask == False`

### Implementation Location
`src/analysis/activity.py` - runs before detectors.

---

## 3) Track Role Gating is Non-Optional

### The Problem
Rules designed for vocals don't make sense for bass:
- Can't HPF bass (that's the point of bass)
- Sibilance detection on drums is meaningless
- Harshness thresholds differ for cymbals vs vocals

### The Solution
Each detection must know the track role:
- `Detection.track_role` field
- Rules specify `required_roles: ["VOCAL_LEAD", "VOCAL_BG"]`
- Rule engine gates: "only fire if role matches"

### Implementation
Rules engine checks role before generating actions.

---

## 4) Parameter Mapping Complexity

### The Problem
Ableton device parameters aren't always linear dB:
- Some are 0.0-1.0 scaled to dB internally
- Some are quantized (enums like filter type)
- Some have weird min/max ranges
- "Gain" might be normalized (0.85 = 0dB, not raw dB)

### The Solution
Device adapters expose **musical units**, not raw values:

```python
# BAD: rule engine sets raw param value
set_param(track_id, device_id, param_id, 0.75)

# GOOD: adapter handles conversion
utility.set_gain_db(-2.5)
eq.set_peaking_cut(band=1, freq_hz=320, q=2.0, gain_db=-2.0)
```

### Implementation
Each device adapter (`utility.py`, `eq8.py`) has converters.

---

## 5) Cache Invalidation (Drift Detection)

### The Problem
`model_cache.json` is only valid for the exact current Live set state. If user:
- Adds/removes tracks
- Reorders devices
- Changes track names

...cached indices become wrong. Applying actions will target wrong params.

### The Solution
Cache includes **fingerprint**:
- Hash of: `(track_names, device_counts_per_track)`
- Before applying actions: rescan, compare fingerprint
- If mismatch: refuse to apply, force rescan

### Implementation
`src/ableton/cache.py` - add `fingerprint` and `timestamp` fields.

---

## 6) UDP Reliability (OSC Transport)

### The Problem
OSC over UDP can:
- Drop packets (unlikely on localhost, but possible)
- Deliver out of order (rare)
- Overrun AbletonOSC's receive buffer if flooded

### The Solution
- **Retries**: already in spec (2 retries per call)
- **Throttling**: 10-30ms delay between consecutive parameter sets
- **Verify-after-set**: re-read critical params to confirm change

### Implementation
`src/osc/rpc.py` - retries already planned.
`src/ableton/apply.py` - add throttle sleep + optional verify.

---

## 7) Confidence & Severity Gating

### The Problem
Not all detections are equally reliable:
- Mud detection in sparse arrangements is uncertain
- Harsh detection on intentional distortion is false positive
- Rumble in bass is expected, not a violation

### The Solution
Detectors output **confidence** (0.0-1.0):
- High confidence: clear violation, safe to correct
- Low confidence: borderline, report-only

Rules gate on confidence:
```python
if detection.confidence >= 0.7 and detection.severity >= 0.3:
    generate_action()
else:
    report_only()
```

### Implementation
`src/analysis/detectors.py` - each detector computes confidence.
`src/rules/engine.py` - gates on confidence + severity.

---

## 8) Reverb Tail Detection Requires Dedicated Render

### The Problem
If reverb is on a return track (not printed to stems), you can't measure tail behavior from stem exports alone.

### The Solution
- **MVP**: Require `REVERB_RETURN.wav` if reverb tail detection is enabled
- If missing: skip detection or report-only
- Later: AbletonOSC can render return tracks individually

### Implementation
`src/jobs/polish_song.py` - check if `REVERB_RETURN.wav` exists before running tail detector.

---

## 9) LUFS Target is Policy, Not Universal Truth

### The Problem
-10.5 LUFS is loud for streaming contexts (Spotify normalizes to -14, YouTube to -13). Hitting -10.5 means:
- True-peak compliance becomes critical
- Risk of distortion increases
- Streaming platforms will turn you down

### The Solution
Treat loudness as **policy profiles**:
```yaml
targets:
  active_profile: "ALBUM_RELEASE"
  profiles:
    ALBUM_RELEASE:
      master_lufs_i: -10.5
    STREAMING_SAFE:
      master_lufs_i: -14.0
```

Same automation, different target set.

### Implementation
`config.yaml` - add profile system (optional for MVP).

---

## 10) Detector Band Energy Correlates with Intentional Sound Design

### The Problem
Band energy spikes don't always mean "violation":
- High harsh-band energy might be intentional synth brightness
- Mud-band energy might be intentional low-mid warmth
- Sibilance spikes might be normal vocal formants

### The Solution
Detectors should express **uncertainty** via confidence scoring:
- Compare to reference profile (if available)
- Use burst detection (spikes vs median) instead of absolute levels
- Track-role gating (vocal sibilance ≠ synth sibilance)
- Report but don't auto-correct if confidence < threshold

### Implementation
`src/analysis/detectors.py` - confidence calculation per detector.

---

## 11) Section Boundaries & Arrangement Context (Future)

### Current Limitation
MVP analyzes entire song as one block. It doesn't know:
- Intro vs chorus vs outro
- Sparse verse vs dense drop
- Intentional quiet sections vs silence

### Future Enhancement
Use Ableton locators/markers to segment:
- Analyze per section
- Different thresholds per section type
- Transition detection (tail cleanup at section boundaries)

### Not MVP
Track this as future work, don't implement yet.

---

## 12) Album-Level Consistency (Future)

### Current Limitation
MVP optimizes each song independently. Can still yield:
- Vocal brightness varying song-to-song
- Bass weight inconsistency
- Different loudness "feel" despite hitting same LUFS

### Future Enhancement
Compute album-level median per stem role:
- Median vocal brightness across all songs
- Median bass low-end energy
- Apply minimal correction toward album median

### Not MVP
Phase 2 feature, document for later.

---

## 13) Testing Without Live Running (CI/CD)

### The Problem
You can't run integration tests in CI without Ableton Live running and responding to OSC.

### The Solution
Two test modes:
- **Offline unit tests**: analysis, rules, serialization (no OSC)
- **Live integration tests**: OSC communication, manual invocation only

### Implementation
`tests/unit/` - pure functions, no Live required.
`tests/integration/` - requires Live, run manually.

---

## 14) Parameter Name Variations Across Live Versions

### The Problem
Live 10 vs 11 vs 12 might name params differently:
- "Gain" vs "Gain (dB)" vs "Output"
- "Ceiling" vs "Ceiling (dB)"

### The Solution
Device adapters use **fuzzy matching + candidate lists**:
```python
GAIN_CANDIDATES = ["Gain", "Gain (dB)", "Output", "Level"]
```

If no match: print available param names, fail with helpful error.

### Implementation
`src/ableton/find.py` - fuzzy param matching.

---

## 15) False Positives from Intentional Creative Choices

### The Problem
The system might flag:
- Intentional lo-fi/distortion as "harsh"
- Intentional sub-bass as "rumble" (on non-bass material)
- Intentional dynamics as "inconsistent"

### The Solution
- **Guardrails**: max cut depth (1-3dB), never boost
- **Confidence gating**: only correct if high confidence
- **Report-only mode**: user reviews before applying
- **Undo mechanism**: keep pre-correction snapshots (future)

### Philosophy
System enforces policy, but policy should be conservative. When in doubt, report and don't touch.

---

## 16) OSC Message Ordering & Atomicity

### The Problem
If setting multiple params (gain + EQ freq + EQ gain), there's no guarantee they apply atomically. Live might render audio mid-update.

### The Solution
- **Throttle**: 25ms delay between sets minimizes window
- **Order matters**: set "enable" params last (e.g. EQ band "On" after freq/gain set)
- **Verify**: re-read after batch to confirm all changes applied

### Not a Blocker
In practice, Live's audio thread is separate from OSC thread. Small glitches unlikely, but document the risk.

---

## 17) Headroom Target Rationale (-6dBFS for Stems)

### Why -6dBFS?
- Leaves room for master bus processing (glue comp, EQ)
- Prevents cumulative clipping when stems sum
- Standard pro mixing practice

### Adjustable?
Yes, via `config.yaml` - but -6dB is a safe default.

---

## 18) Iteration Loop Termination (Convergence)

### The Problem
What if violations never fully resolve?
- Low-end rumble persists despite HPF (it's baked into source)
- Mud persists because arrangement is dense (not fixable via EQ)

### The Solution
Stop conditions:
- Max 2 iterations (prevents endless loop)
- "Same violation persists after 2 attempts" → mark unfixable, report-only
- "Next action would exceed clamps" → stop, report

### Implementation
`src/jobs/polish_song.py` - track violation history, detect persistence.

---

## 19) Future: Show Control & Visuals (Data Model Bridge)

### Current State
MVP focuses on audio compliance only.

### Future Vision
System can drive:
- Lighting (beat-synced)
- Visuals (section-aware)
- Stage choreography (narrative-aligned)

### Bridge Concept
All driven by same data:
- Beat grid from Live (tempo, bar count)
- Section markers (intro/verse/chorus)
- Energy curves (measured from audio)
- Detected events (impacts, drops, tails)

### Not MVP
Document as future direction, don't implement.

---

## Summary: What to Prioritize

### Must Address Before Coding
1. Export policy documentation
2. Activity masking (silence handling)
3. Track role gating
4. Parameter converters (musical units)
5. Cache fingerprinting
6. Confidence/severity in detections

### Should Add During MVP
7. UDP throttling
8. Stop conditions (unfixable violations)
9. Verify-after-set (critical params)

### Nice to Have (Not Blocking)
10. Profile system (loudness targets)
11. Reference profile mode
12. Album consistency (Phase 2)

### Document But Don't Build Yet
13. Section-aware analysis
14. Visual/show control bridge
15. Undo mechanism
