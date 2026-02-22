# STATUS (LOAD THIS FIRST)

**Last updated**: 2026-02-22 18:50 UTC  
**Primary doc**: `STATE.md` (operational state, single source of truth)  
**This doc**: Operating procedures and contract  
**Repo**: `/Users/trev/Repos/finishline_audio_repo`

---

## A) Contract (non-negotiable)

When operating on this repo, the assistant MUST:

1. **One action per assistant response.**
   - ONE terminal command OR ONE file edit per turn.
   - Wait for terminal output before next action.
   - Do NOT chain multiple independent commands unless explicitly requested.

2. **Terminal-first. Prefer read-only probes.**
   - Before writes, run read-only inspection.
   - Use `--dry` flags when available.
   - Validate with exact terminal outputs (paste into conversation).

3. **If something fails: run the next probe only.**
   - Do NOT attempt multiple fixes speculatively.
   - Follow error taxonomy (Section H).
   - Single probe → observe → diagnose → single fix.

4. **No overtesting; prefer scripted smoke tests when available.**
   - Use `./scripts/run_smoke_tests.sh` instead of manual test sequences.
   - Only run individual commands for targeted debugging.

5. **Commit after validated tasks only.**
   - Every successful task gets ONE commit.
   - Commit message follows repo conventions (see git log).
   - Push to main immediately after commit.

---

## B) Environment (known-good)

**Repo path**: `/Users/trev/Repos/finishline_audio_repo`

**Venv activation**:
```bash
cd /Users/trev/Repos/finishline_audio_repo && source .venv/bin/activate
```

**AbletonOSC ports**:
- Send to: `127.0.0.1:11000` (Ableton listens)
- Receive on: `127.0.0.1:11001` (flaas RPC listener)

**Python version**: >= 3.11  
**Package**: flaas 0.0.2 (editable install)

**Key directories**:
- `src/flaas/` - Python modules
- `docs/` - All documentation
- `data/caches/` - model_cache.json (scan results)
- `data/actions/` - actions.json (planned changes)
- `data/reports/` - analysis/check outputs
- `data/registry/` - device maps (eq8_map, device_map)
- `input/` - test audio files
- `output/` - exported renders
- `scripts/` - automation scripts

---

## C) Current State

**See `STATE.md` for complete operational details.**

**Current task**: Close LUFS gap (3.09 LU remaining) via compression tuning

**Applied state**: Master chain validated (Glue Compressor → Limiter), Master fader 0.0 dB

**Latest result**: LUFS -13.59, Peak -6.00 (experiment #14)

**Status**: Export loop functional ✅

---

## D) Commands

**See `STATE.md` for command reference.**

**Key**: `plan-gain`, `apply`, `verify` (master track auto-resolution), `device-set-safe-param`, `eq8-set`, `limiter-set`

**Smoke tests**: `make smoke` (7s), `make write-fast` (9s), `make write` (39s)

---

## E) Critical Facts

**See `STATE.md` for technical details.**

**Master track**: track_id=-1000 (NOT 0)  
**Device resolution**: Query `/live/track/get/devices/name`, response is `(track_id, name0, name1, ...)`, skip first element  
**Master fader**: Post-device chain, must be 0.0 dB for predictable peak control  
**Limiter alone insufficient**: Need compression before limiter for loudness  
**Export settings**: Rendered Track = Master, Normalize = OFF

---

## F) Console Commands (startup menu)

When a fresh chat loads STATUS.md, the assistant MUST begin by printing:

```
Available commands:
- run / run program
- continue
- save
- back
- forward

Type a command.
```

**Command semantics**:

- **run / run program**: Execute RUN PROGRAM section (G) strictly. Read STATUS.md fully, then output NEXT ACTION command only, wait for output, repeat.

- **continue**: Execute the NEXT ACTION (Section G) once, then stop and wait for output.

- **save**: Update STATUS.md with latest progress. Assistant asks: "Paste latest terminal output or summary." Then updates:
  - Section C: commit hash (if new commit)
  - Section E: context snapshot (what just completed)
  - Section G: NEXT ACTION (based on ROADMAP or user input)

- **back / forward**: Navigate task list. Changes NEXT ACTION pointer in Section G. Does NOT execute commands. Prints new NEXT ACTION.

**Default behavior**: If user message unclear, assume "continue".

---

## G) RUN PROGRAM (startup script)

**When user types "run program" or "run", execute this strictly:**

### Step 1: Read and understand
- Read this STATUS.md file fully and carefully.
- Parse NEXT ACTION below.
- Do NOT ask clarifying questions unless blocked.

### Step 2: Output ONE command
- Print the NEXT ACTION command exactly as written.
- Execute it.
- Wait for terminal output.

### Step 3: Observe and decide
- If PASS: Print short summary. Stop. Wait for "continue" or next user input.
- If FAIL: Execute fallback probe (see below). Stop. Wait for user input.

### Step 4: Repeat
- When user says "continue" or "run", execute next action.

---

### NEXT ACTION

**Task**: Close LUFS gap (manual compression tuning)

**Status**: Export loop functional ✅ (16 experiments complete)

**Current gap**: 3.09 LU (-13.59 → -10.50 LUFS)

**Best result so far**: LUFS -13.59, Peak -6.00 (experiment #14)

**Step 1: Tune compression (in Ableton)**
1. Master chain: `[Utility] → [EQ Eight] → [Glue Compressor] → [Limiter]`
2. Master fader: 0.0 dB (critical for peak control)
3. Glue Compressor:
   - Lower Threshold → GR 15-18 dB
   - Makeup +15-18 dB
4. Limiter:
   - Gain +28-30 dB
   - Ceiling -6.5 dB

**Step 2: Export**
- File → Export Audio/Video
- Rendered Track = Master
- Normalize = OFF
- File: `output/master_iter<N>.wav`

**Step 3: Verify**
```bash
flaas verify-audio output/master_iter<N>.wav
```

**Step 4: Adjust**
- Peak > -6.0: Reduce limiter gain OR lower ceiling
- LUFS < -10.5: Increase compression OR increase limiter gain
- Repeat

**Expected outcome**: 
- Hit targets: LUFS -10.50, Peak -6.00
- Validate compression + limiter strategy

**On success**: 
- Document final settings
- Begin master processing automation (OSC control for Glue/Limiter)

**See detailed workflow**: `docs/reference/EXPORT_FINDINGS.md`

---

### FALLBACK PROBE (if NEXT ACTION fails)

**Command**:
```bash
cd /Users/trev/Repos/finishline_audio_repo && source .venv/bin/activate && flaas ping --wait
```

**Expected**: `ok: ('ok',)`

**If ping fails**: Ableton or AbletonOSC issue. Stop and report to user.  
**If ping succeeds**: Investigate smoke script error. Run with bash -x for debug output.

---

### STOP RULE

Stop when: non-zero exit after fallback probe, user says "stop", task needs decision, major milestone done.  
Do NOT stop for: warnings (exit 0), test file updates, long output.

---

## H) Error Taxonomy + Probes

| **Category** | **Symptoms** | **Probe** |
|--------------|--------------|-----------|
| 1. Connectivity | TimeoutError | `flaas ping --wait` |
| 2. Ableton | Empty scan | `flaas scan` |
| 3. Fingerprint | RuntimeError: mismatch | `flaas scan` |
| 4. Audio | ValueError | `ls -lh input/test.wav` |
| 5. Packaging | ImportError | `pip install -e .` |
| 6. Map Missing | "Map file not found" | Run command from error msg |

After probe: ONE action (read/edit/run), then stop.

---

## I) Documentation

**Primary**: `STATE.md` (operational state)  
**This file**: Operating procedures  
**Legacy docs**: `docs/` (reference only)

---

## J) Known Issues

**See `STATE.md` for complete issue list and workarounds.**

**Current**: Export loop functional → Close LUFS gap via compression tuning

**See**: `docs/reference/EXPORT_FINDINGS.md` for 16 experiments + critical findings

---

**File length**: ~200 lines (under 250 limit)  
**Usage**: Upload this file to new ChatGPT thread, paste NEW_CHAT_MESSAGE.md, type "run".
