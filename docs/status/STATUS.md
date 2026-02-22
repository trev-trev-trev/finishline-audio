# STATUS (LOAD THIS FIRST)

**Last updated**: 2026-02-22 12:41 UTC  
**Commit**: `5a99e6b` - docs: add smoke test script to terminal cheatsheet  
**Repo**: https://github.com/trev-trev-trev/finishline-audio  
**Branch**: main  
**Version**: 0.0.2

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

## C) Where We Are

**Milestone**: MVP (v0.1.0)  
**Progress**: ~95% complete

**Last known-good commit**: `5a99e6b`  
**Last known fingerprint**: `fff1ca7052cdab9c637ec6bdea73bea7cc34ae0f6aa2904f8fd6bb27a72fae64`  
**Last validated**: 2026-02-22 12:41 UTC (smoke tests: 14/14 passed)

**Tracks**: 1 (Master)  
**Devices on track 0**: Utility (d0), EQ Eight (d1), Limiter (d2)

---

## D) Verified Capabilities (short)

✅ **OSC**: `ping --wait`, `scan`, `inspect-selected-track`, `inspect-selected-device`, `device-param-info`  
✅ **Audio**: `analyze`, `check`, `verify-audio`  
✅ **Generic control**: `device-set-param`, `device-map`  
✅ **EQ Eight**: `eq8-map`, `eq8-set`, `eq8-reset-gains`  
✅ **Limiter**: `limiter-set` (gain, ceiling, release, auto, link, lookahead)  
✅ **Loop**: `loop`, `reset`, `apply --dry`  
✅ **Smoke tests**: `./scripts/run_smoke_tests.sh` (6 read-only), `--write` (14 with revert)

---

## E) Current Context Snapshot (tight)

**Last completed**:
- ✅ `limiter-set` command (semantic Limiter control)
- ✅ Smoke test script (14 tests pass: read-only + write+revert)
- 📊 Surface area: Utility (Gain), EQ Eight (8 bands A/B), Limiter (6 params)

**Critical gotchas**:
- OSC port conflict: Sleep 1 sec between commands or use smoke script
- Selected device timeout: Use explicit track/device IDs on Master/Return
- Map files required: `eq8-set`/`eq8-reset-gains`/`limiter-set` need map generated first
- Fingerprint enforcement: `apply` rejects if Live set changed since `plan-gain`

**Assumptions**: Track 0 has Utility (d0), EQ Eight (d1), Limiter (d2)

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

**Task**: Validate smoke tests can be run standalone (confirm it works for new user)

**Command**:
```bash
cd /Users/trev/Repos/finishline_audio_repo && ./scripts/run_smoke_tests.sh
```

**Expected output**:
- ✅ All 6 read-only tests PASS
- Duration: ~25 seconds
- Report written: `data/reports/smoke_latest.txt`
- Exit code: 0

**Pass criteria**:
- Output contains "Passed: 6"
- Output contains "Failed: 0"
- Exit code 0

**On success**: Print "✅ Smoke tests validated. Ready for next expansion."

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

## I) Quick Reference Links

**Order**: STATUS.md (this) → CURRENT.md → ROADMAP.md → operating-manual-v1.md → terminal-cheatsheet.md  
**Recent**: RECEIPTS/ (smoke tests, limiter-set, device-map, inspect-selected-device)

---

## J) Known Issues + Workarounds

**OSC port conflict**: Sleep 1 sec between commands OR use smoke test script  
**Selected device timeout**: Use explicit track/device IDs instead of selected_device on Master/Return  
**Map file missing**: Error message shows exact command (e.g., `flaas eq8-map 0 1`)

**Surface area** (track 0): Utility (d0, Gain), EQ Eight (d1, 8 bands A/B), Limiter (d2, 6 params)  
**Ranges**: Utility Gain -1/+1, EQ Gain -15/+15 dB, Limiter Ceiling -24/0 dB  
**Discovery**: `flaas device-param-info <t> <d> --param-id N` or `flaas device-map <t> <d>`

---

**File length**: ~200 lines (under 250 limit)  
**Usage**: Upload this file to new ChatGPT thread, paste NEW_CHAT_MESSAGE.md, type "run".
