# PRIORITY CORRECTION

**Date**: 2026-02-22 19:00 UTC

---

## THE REAL BOTTLENECK

**Documentation got ahead of execution.**

Discovery framework (DISCOVERY.md, NEXT_CHAPTER.md) maps 300-500 command generation strategy.

**But**: Can't execute that strategy until **export loop works**.

---

## CLOSED-LOOP AUDIO ITERATION

**The loop**:
```
plan-gain → apply → export → verify-audio → adjust → repeat
```

**Current state**: Loop **BLOCKED at export** (third-party plugins hang render)

**Until this works**: Endpoint expansion is premature

---

## IMMEDIATE ACTION

**In Ableton**:
1. Disable **ValhallaSpaceModulator** (track 41, device 1)
2. Disable **StudioVerse** (track 41, device 2)
3. Attempt **4-8 bar export** to `output/master_iter1.wav`

**After export succeeds**:
```bash
flaas verify-audio output/master_iter1.wav
```

**Expected**: Confirm gain delta (+0.250) is reflected in LUFS/peak measurements

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
3. **Applied state**: Master Utility gain = **-0.750 linear** (delta +0.250 applied, NOT reset)
4. **Export blocker**: Third-party plugins (Valhalla, StudioVerse) hang render

---

## NEXT STEPS (CORRECTED PRIORITY)

### 1. Fix Export (IMMEDIATE)
- Disable plugins in Ableton
- Test 4-8 bar export
- Validate gain adjustment via `verify-audio`

### 2. Populate Endpoint Registry (AFTER EXPORT WORKS)
- Fill `docs/ENDPOINT_REGISTRY.json` with top 50 endpoints
- Include full specification per endpoint
- Prioritize track/device/song controls

### 3. Generate Commands (AFTER REGISTRY COMPLETE)
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

## SINGLE MOST IMPORTANT THING

**Fix the export crash.**

Everything else (endpoint expansion, command generation, comprehensive coverage) depends on a working audio iteration loop.

---

**Priority reset complete. Execute export fix first.**
