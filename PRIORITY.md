# PRIORITY CORRECTION

**Date**: 2026-02-22 19:00 UTC

---

## THE REAL BOTTLENECK (RESOLVED)

**Documentation got ahead of execution.**

Discovery framework (DISCOVERY.md, NEXT_CHAPTER.md) maps 300-500 command generation strategy.

**Was blocked**: Export loop crash prevented iteration

**Now**: Export loop functional ✅ Manual iteration working (16 experiments complete)

---

## CLOSED-LOOP AUDIO ITERATION

**The loop**:
```
configure → export → verify-audio → adjust → repeat
```

**Current state**: Loop **FUNCTIONAL** (manual iteration working)

**Latest result**: LUFS -13.59, Peak -6.00 (gap 3.09 LU to target)

**Remaining work**: Tune compression to close LUFS gap

---

## IMMEDIATE ACTION (UPDATED)

**Export loop unblocked** - Manual iteration working ✅

**Next iteration** (in Ableton):
1. Glue Compressor: Lower Threshold → GR 15-18 dB
2. Glue Compressor: Makeup +15-18 dB
3. Limiter: Gain +28-30 dB, Ceiling -6.5 dB
4. Export → `output/master_iter<N>.wav`

**After export**:
```bash
flaas verify-audio output/master_iter<N>.wav
```

**Goal**: Close 3.09 LU gap (-13.59 → -10.50 LUFS) while maintaining peak ≤ -6.00

---

## DOCUMENTATION GAP FIXED

**Problem**: `all_osc_endpoints.txt` contains patterns, not specifications

**Missing**: Arg types, response shapes, safety rules, critical quirks

**Solution**: `docs/ENDPOINT_REGISTRY.json` provides proper specification structure

**Example entries**:
- `/live/track/get/volume` - read track fader level
- `/live/track/set/volume` - write track fader level
- `/live/device/get/parameters/value` - read all device params
- `/live/track/get/devices/name` - get device names (CRITICAL: drop first element)

**Template**: Includes category, args (name/type/range/example), response (type/shape/example), safety (read_only/write_safe/revertable), notes

---

## SYSTEM ARCHITECTURE (CONFIRMED CORRECT)

```
Ableton Live (the set)
    ↓
AbletonOSC Remote Script (exposes /live/* OSC endpoints)
    ↓
OSC UDP bridge (request/response + listeners)
    ↓
FLAAS (Python CLI + modules + tests)
```

**Goal**: Mirror Ableton's control surface in Python  
**Method**: Map OSC endpoints → Python commands  
**Current coverage**: ~15 commands, ~60 control points  
**Target**: 300-500 commands, 95%+ coverage

---

## NON-NEGOTIABLE INVARIANTS (CAPTURED)

1. **Master track_id = -1000** (returns negative, regular 0..N)
2. `/live/track/get/devices/name` returns `(track_id, name0, name1, ...)` - **drop index 0**
3. **Master fader is post-device chain** - Must be 0.0 dB for predictable peak control
4. **Limiter alone insufficient** - Need compression before limiter for loudness
5. **Export settings**: Rendered Track = Master, Normalize = OFF

---

## NEXT STEPS (UPDATED PRIORITY)

### 1. Close LUFS Gap (IMMEDIATE) ✅ IN PROGRESS
- Tune compression (GR 15-18 dB, Makeup 15-18 dB)
- Adjust limiter (Gain 28-30 dB, Ceiling -6.5 dB)
- Export + verify → Iterate until targets hit
- **Status**: Manual workflow functional, 3.09 LU gap remaining

### 2. Automate Master Processing (AFTER LUFS TARGET HIT)
- **Export trigger NOT available via OSC** (verified: `/live/song/export/structure` returns `(1,)`)
- **Semi-automated approach**: Automate params + verify, manual export click
- Add Glue Compressor OSC control (threshold, makeup, ratio)
- Add master fader OSC control (get/set volume)
- Build batch experiment runner (pause for manual export)
- **ROI**: 10x speedup (only export click is manual)

### 3. Populate Endpoint Registry (PARALLEL TO AUTOMATION)
- Fill `docs/ENDPOINT_REGISTRY.json` with top 50 endpoints
- Include full specification per endpoint
- Prioritize track/device/song controls

### 4. Generate Commands (AFTER REGISTRY COMPLETE)
- Use registry as source of truth
- Generate Python modules + CLI parsers + tests
- Batch validate via terminal

---

## DOC ROLES (CLARIFIED)

- **STATE.md** - Volatile operational truth (what's applied, what's blocked, next action)
- **PRIORITY.md** (this file) - Execution order correction
- **ENDPOINT_REGISTRY.json** - Canonical spec (bridge between patterns and codegen)
- **DISCOVERY.md** - Research plan + taxonomy
- **NEXT_CHAPTER.md** - Execution strategy (10→100→1000)
- **all_osc_endpoints.txt** - Raw inventory (108 patterns)

---

## SINGLE MOST IMPORTANT THING (UPDATED)

**Close the LUFS gap (3.09 LU remaining).**

Manual iteration loop is functional. Next: Automate master processing to eliminate manual export bottleneck.

**Then**: Scale to comprehensive control coverage (endpoint expansion, command generation).

---

**Export loop unblocked** ✅ **Manual iteration functional** ✅ **Gap: 3.09 LU**

**See**: `docs/reference/EXPORT_FINDINGS.md` for complete triage findings (16 experiments)
