# FLAAS Execution System

**Deterministic terminal-first execution loop for no-thrash development.**

**Version**: 1.0  
**Date**: 2026-02-22

---

## Overview

This document defines the operational execution system for FLAAS development. Every state transition, error classification, and decision is specified with exact terminal commands and expected outputs. No speculation, no thrash.

---

## A. Finite-State Machine (FSM)

### States + Transitions

```
     START
       │
       ▼
┌─────────────┐
│   PLAN      │ User provides Step N specification
└──────┬──────┘
       │ Trigger: Task specification received
       │ Required: Step number + imperative statement + exact commands
       ▼
┌─────────────┐
│   EDIT      │ Agent modifies files
└──────┬──────┘
       │ Trigger: Code changes complete
       │ Required: File paths changed (explicit list)
       ▼
┌─────────────┐
│   RUN       │ Execute validation command(s)
└──────┬──────┘
       │ Trigger: Command execution starts
       │ Required: Exact command string + expected timeout
       ▼
┌─────────────┐
│  OBSERVE    │ Terminal produces output
└──────┬──────┘
       │ Trigger: Command completes (exit code available)
       │ Required: Full stdout + stderr + exit code
       │
       ├─ Exit 0 ────────────┐
       │                     │
       └─ Exit ≠0 ───────┐   │
                         │   │
                   ┌─────▼───▼────┐
                   │   DIAGNOSE   │ Classify error + identify probe
                   └─────┬────────┘
                         │ Trigger: Error classification complete
                         │ Required: Error category (1-6) + probe command
                         ▼
                   ┌─────────────┐
                   │    FIX      │ Apply targeted correction
                   └─────┬───────┘
                         │ Trigger: Fix applied
                         │ Required: Changed files listed
                         ▼
                   ┌─────────────┐
                   │  VERIFY     │ Re-run original validation
                   └─────┬───────┘
                         │ Trigger: Re-run completes
                         │ Required: New output + exit code
                         │
                         ├─ Success ────┐
                         │              │
                         └─ Fail ───────┤ (loop to DIAGNOSE max 3x, then STOP)
                                        │
                                  ┌─────▼─────┐
                                  │  COMMIT   │ git add/commit/push
                                  └─────┬─────┘
                                        │ Trigger: Push succeeds
                                        │ Required: git push output
                                        ▼
                                     (DONE)
```

### State: PLAN
**Entry condition**: User message received.

**Required artifacts**:
- Step number (e.g., "Step 100")
- Imperative statement (e.g., "add EQ Eight parameter query")
- Exact bash commands to execute (multi-line heredoc acceptable)
- Specific output to paste (e.g., "Paste output of `git push`")

**Exit condition**: Task specification parsed and understood.

**Next state**: EDIT

**Example valid input**:
```
Step 100 (one task): add EQ Eight device class detection.

Run:
```bash
flaas scan
cat data/caches/model_cache.json | jq '.tracks[0].devices[] | select(.class_name | contains("EQ"))'
```

Paste the jq output.
```

**Invalid inputs** (STOP and ask):
- No step number
- Ambiguous task ("improve error handling")
- No validation command
- Multiple unrelated tasks

---

### State: EDIT
**Entry condition**: Transitioned from PLAN.

**Required actions**:
- Modify files (list all changed files)
- Create files (list all new files)
- Delete files (list all removed files)

**Artifacts produced**: Modified source files.

**Exit condition**: All file edits complete.

**Next state**: RUN

**Transition trigger**: Agent declares "File changes complete, running validation..."

**Rollback**: If error detected before RUN, revert changes with `git checkout -- [files]`

---

### State: RUN
**Entry condition**: Transitioned from EDIT.

**Required actions**:
- Execute exact validation command from PLAN
- Capture stdout, stderr, exit code
- Enforce timeout (default 30s, explicit if longer)

**Artifacts produced**: Terminal output (text).

**Exit condition**: Command completes or times out.

**Next state**: OBSERVE

**Timeout handling**:
- If timeout expected (e.g., `flaas loop` on large file), specify in PLAN
- If unexpected timeout, treat as error (exit code 124)

---

### State: OBSERVE
**Entry condition**: Transitioned from RUN.

**Required analysis**:
- Parse exit code (0 = success, non-zero = failure)
- Scan output for success patterns (see Section D: Paste Templates)
- Scan output for error patterns (see Section B: Error Taxonomy)

**Decision**:
- **If exit 0 AND success patterns present** → COMMIT
- **If exit ≠0 OR error patterns present** → DIAGNOSE

**Artifacts produced**: Classification (success/failure).

**Exit condition**: Decision made.

**Next state**: COMMIT or DIAGNOSE

---

### State: DIAGNOSE
**Entry condition**: Transitioned from OBSERVE (failure path).

**Required actions**:
1. Classify error into taxonomy (1-6, see Section B)
2. Identify single-command probe (read-only preferred)
3. Execute probe
4. Paste probe output

**Artifacts produced**:
- Error category (1-6)
- Probe command
- Probe output

**Exit condition**: Root cause identified OR max probes (3) exhausted.

**Next state**: FIX or STOP (if max probes exhausted)

**Probe sequence** (deterministic):
1. First probe: Category-specific probe (see Section B)
2. Second probe: Read artifact state (e.g., `cat data/caches/model_cache.json`)
3. Third probe: Environment check (e.g., `python3 -m compileall src/flaas/`)

**STOP rule**: If 3 probes don't reveal root cause, escalate to user.

---

### State: FIX
**Entry condition**: Transitioned from DIAGNOSE.

**Required actions**:
- Apply targeted fix (one file or one command)
- List changed files
- State hypothesis (what fix should achieve)

**Artifacts produced**: Modified source files or environment state.

**Exit condition**: Fix applied.

**Next state**: VERIFY

**Iteration limit**: Max 3 attempts through FIX→VERIFY loop, then STOP.

---

### State: VERIFY
**Entry condition**: Transitioned from FIX.

**Required actions**:
- Re-run original validation command from PLAN
- Compare output to expected (from PLAN)

**Artifacts produced**: Terminal output (verification run).

**Exit condition**: Command completes.

**Next state**:
- **If success** → COMMIT
- **If failure AND iterations < 3** → DIAGNOSE
- **If failure AND iterations >= 3** → STOP (escalate)

**Stop rule**: After 3 fix attempts, stop and ask user.

---

### State: COMMIT
**Entry condition**: Validation passed.

**Required actions**:
1. Stage changes: `git add -A` or specific files
2. Commit with descriptive message (see Section D: Commit Template)
3. Push: `git push`
4. Paste git push output

**Artifacts produced**:
- Git commit (SHA)
- Push confirmation output

**Exit condition**: Push succeeds.

**Next state**: DONE (ready for next PLAN)

**Failure handling**:
- If push fails (network, conflicts), paste error and STOP
- User resolves conflict, re-enters at COMMIT

---

## B. Error Taxonomy + Deterministic Probes

### Category 1: Connectivity / Ports
**Symptoms** (regex patterns to match):
- `TimeoutError.*waiting for reply`
- `Connection refused`
- `OSError.*Address already in use`

**Deterministic probe sequence**:

**Probe 1.1** (First):
```bash
flaas ping --wait --timeout 5.0
```
**Expected observations**:
- **Success**: `ok: ('ok',)` → OSC is alive, error is elsewhere
- **Failure**: `TimeoutError` → Ableton or AbletonOSC issue

**Probe 1.2** (If 1.1 fails):
```bash
ps aux | grep -i "ableton live"
```
**Expected observations**:
- **Process running**: Ableton is open → check AbletonOSC config
- **No process**: Ableton not running → instruct user to start

**Probe 1.3** (If Ableton running):
```bash
ls ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC
```
**Expected observations**:
- **Directory exists**: AbletonOSC installed → check loaded in Live
- **Not found**: AbletonOSC not installed → provide install instructions

**Next action rules**:
- If 1.1 succeeds: Error is not connectivity (reclassify)
- If 1.2 shows no Ableton: User action required (STOP with message)
- If 1.3 shows missing AbletonOSC: User action required (STOP with install link)
- If all probes pass but still timing out: Check ports with `lsof -i :11000 -i :11001`

---

### Category 2: Ableton Configuration
**Symptoms** (regex patterns):
- `ok.*false.*scan`
- `num_tracks.*0`
- `IndexError.*device`
- `devices.*\[\]` (empty device list)

**Deterministic probe sequence**:

**Probe 2.1** (First):
```bash
flaas scan && cat data/caches/model_cache.json | jq '{ok, num_tracks, master: .tracks[0]}'
```
**Expected observations**:
- **ok: false**: Scan failed (see note field for error)
- **num_tracks: 0**: Empty Live set
- **tracks[0] missing**: No master track
- **tracks[0].devices empty**: No Utility on master

**Probe 2.2** (If tracks present but device missing):
```bash
cat data/caches/model_cache.json | jq '.tracks[0].devices[] | {index, name, class_name}'
```
**Expected observations**:
- List of devices on master track
- Check if Utility (class StereoGain) is present
- Check device index (should be 0 for MVP)

**Probe 2.3** (Direct parameter test):
```bash
flaas util-gain-norm 0 0 0.5 && flaas verify
```
**Expected observations**:
- **Success + readback 0.5**: Device exists and accessible
- **Timeout**: Device doesn't exist at track 0 device 0
- **Wrong readback**: Parameter ID mismatch

**Next action rules**:
- If no tracks: User must create tracks in Ableton (STOP)
- If no Utility: User must add Utility to master track device slot 0 (STOP)
- If device at wrong index: Adjust hardcoded assumptions or move device
- If parameter ID wrong: Re-discover via `/live/device/get/parameters/name`

---

### Category 3: Schema / Fingerprint Mismatch
**Symptoms** (regex patterns):
- `RuntimeError.*fingerprint mismatch`
- `expected.*got.*[a-f0-9]{64}`

**Deterministic probe sequence**:

**Probe 3.1** (First):
```bash
flaas scan && cat data/caches/model_cache.json | jq -r '.fingerprint'
```
**Expected observations**:
- Prints current Live set fingerprint (64-char hex)

**Probe 3.2** (Compare with actions):
```bash
cat data/actions/actions.json | jq -r '.live_fingerprint'
```
**Expected observations**:
- Prints expected fingerprint from planned actions
- Compare with 3.1 output (should differ if set changed)

**Probe 3.3** (Diff details):
```bash
diff <(flaas scan 2>&1) <(cat data/caches/model_cache.json) || echo "Live set changed"
```
**Expected observations**:
- Shows what changed in Live set structure

**Next action rules**:
- **If fingerprints differ**: Regenerate actions (idempotent fix)
  ```bash
  flaas plan-gain input/test.wav
  flaas apply  # Should now succeed
  ```
- **If fingerprints match but still error**: Bug in fingerprint logic (escalate)

**Automatic fix** (no user input):
```bash
flaas scan && flaas plan-gain input/test.wav && flaas apply
```

---

### Category 4: Audio Analysis Failures
**Symptoms** (regex patterns):
- `ValueError.*empty audio`
- `FileNotFoundError.*\.wav`
- `soundfile.*error`
- `nan` or `inf` in analysis output

**Deterministic probe sequence**:

**Probe 4.1** (File existence):
```bash
ls -lh input/test.wav && file input/test.wav
```
**Expected observations**:
- File exists: Shows size + type
- File missing: `No such file or directory`
- Wrong type: `file` shows non-audio type

**Probe 4.2** (WAV metadata):
```bash
python3 -c "import soundfile as sf; print(sf.info('input/test.wav'))"
```
**Expected observations**:
- Success: Prints samplerate, channels, frames
- Failure: `soundfile` exception (corrupt file)

**Probe 4.3** (Manual analysis):
```bash
python3 -c "from flaas.analyze import analyze_wav; print(analyze_wav('input/test.wav'))"
```
**Expected observations**:
- Success: Prints AnalysisResult
- ValueError: Empty audio (0 samples)
- Other exception: Specific audio issue

**Next action rules**:
- **If file missing**: Regenerate test file (deterministic script):
  ```python
  import numpy as np, soundfile as sf, os
  os.makedirs("input", exist_ok=True)
  sr = 48000
  t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
  x = 0.2*np.sin(2*np.pi*440*t)
  sf.write("input/test.wav", x, sr)
  ```
- **If corrupt**: Delete and regenerate
- **If empty audio**: Check export settings (normalization, length)

---

### Category 5: Path / Permissions
**Symptoms** (regex patterns):
- `PermissionError`
- `FileNotFoundError.*data/`
- `OSError.*cannot create directory`

**Deterministic probe sequence**:

**Probe 5.1** (Directory structure):
```bash
ls -la data/ 2>&1 || echo "data/ missing"
```
**Expected observations**:
- **Exists**: Shows subdirectories (caches, reports, actions)
- **Missing**: `No such file or directory`

**Probe 5.2** (Write permissions):
```bash
touch data/.test_write && rm data/.test_write && echo "writable" || echo "not writable"
```
**Expected observations**:
- `writable`: Permissions OK
- `not writable`: Permission issue

**Probe 5.3** (Create missing):
```bash
mkdir -p data/caches data/reports data/actions data/timelines data/profiles
ls -la data/
```
**Expected observations**:
- All subdirectories now exist

**Next action rules**:
- **If data/ missing**: Run probe 5.3 (mkdir), re-run original command
- **If not writable**: Check repo ownership (`ls -ld .`), fix with `chmod` if needed
- **If parent missing**: Create full path with `mkdir -p`

**Automatic fix** (no user input):
```bash
mkdir -p data/caches data/reports data/actions data/timelines data/profiles
```

---

### Category 6: Packaging / Import
**Symptoms** (regex patterns):
- `ModuleNotFoundError: No module named 'flaas'`
- `ImportError: cannot import name`
- `command not found: flaas`
- `SyntaxError` in Python code

**Deterministic probe sequence**:

**Probe 6.1** (Package installation):
```bash
pip show flaas
```
**Expected observations**:
- **Installed**: Shows version 0.0.2, location
- **Not found**: `WARNING: Package(s) not found: flaas`

**Probe 6.2** (Direct module execution):
```bash
python3 -m flaas.cli --help
```
**Expected observations**:
- **Success**: Shows help text (package importable)
- **ModuleNotFoundError**: Package not in Python path
- **SyntaxError**: Code syntax issue

**Probe 6.3** (Syntax check):
```bash
python3 -m compileall src/flaas/
```
**Expected observations**:
- **Success**: `Listing 'src/flaas/'...` (no errors)
- **Failure**: Shows syntax error file + line

**Next action rules**:
- **If not installed**: Run `pip install -e .` (reinstall)
- **If syntax error**: Fix syntax, re-run 6.3
- **If import error**: Check import statement, verify module exists

**Automatic fix** (packaging issue):
```bash
source .venv/bin/activate
pip install -e .
python3 -m flaas.cli --version  # Verify
```

**Automatic fix** (syntax issue):
- Fix syntax error (agent edits file)
- Re-run `python3 -m compileall src/flaas/`
- If passes, re-run original validation

---

## C. Single-Command Decision Algorithm

### Input: Pasted Terminal Output

**Step 1: Parse Exit Code**
```
if exit_code == 0:
    goto SUCCESS_PATH
else:
    goto ERROR_PATH
```

---

### SUCCESS_PATH

**Step 2: Validate Success Patterns**

Match against:
- `sent` (OSC fire-and-forget)
- `ok: \(.*\)` (OSC reply)
- `APPLIED:` (parameter changed)
- `PASS` (compliance achieved)
- `data/.*/.*\.json` (file written)
- `To https://github.com/.*/` (git push)

**If matched**:
1. State: Transition to COMMIT
2. Action: `git add -A && git commit -m "..." && git push`
3. Output: Paste git push output

**If no pattern matched but exit 0**:
- Warn: "Success exit but no success pattern matched"
- Action: Review output manually, proceed to COMMIT if looks correct

---

### ERROR_PATH

**Step 2: Classify Error Category**

**Pattern matching** (first match wins):

| Pattern | Category | Probe | Next State |
|---------|----------|-------|------------|
| `TimeoutError.*waiting.*reply` | 1 (Connectivity) | `flaas ping --wait` | DIAGNOSE |
| `Connection refused` | 1 (Connectivity) | `ps aux \| grep Ableton` | DIAGNOSE |
| `ok.*false` in scan output | 2 (Ableton Config) | `flaas scan \|\| jq .` | DIAGNOSE |
| `num_tracks.*0` | 2 (Ableton Config) | Check Live has tracks | STOP (user action) |
| `RuntimeError.*fingerprint` | 3 (Schema) | `flaas scan && flaas plan-gain` | FIX (auto) |
| `ValueError.*empty audio` | 4 (Audio) | `ls -lh input/test.wav` | DIAGNOSE |
| `FileNotFoundError.*\.wav` | 4 (Audio) | Regenerate test file | FIX (auto) |
| `PermissionError` | 5 (Permissions) | `ls -la data/` | DIAGNOSE |
| `cannot create directory` | 5 (Permissions) | `mkdir -p data/*` | FIX (auto) |
| `ModuleNotFoundError` | 6 (Packaging) | `pip show flaas` | DIAGNOSE |
| `command not found: flaas` | 6 (Packaging) | `pip install -e .` | FIX (auto) |
| `SyntaxError` | 6 (Packaging) | `python3 -m compileall src/` | DIAGNOSE |

**If no pattern matched**:
- Category: UNKNOWN
- Action: Paste full output, escalate to user
- State: STOP

---

**Step 3: Choose Action Type**

**Read-only probe** (preferred):
- No file changes
- No OSC sets
- Just read current state
- Examples: `cat`, `ls`, `jq`, `flaas verify`, `flaas scan`

**Fix + verify**:
- Targeted file edit or command
- Re-run original validation
- Examples: Fix syntax, regenerate file, reinstall package

**User action required**:
- External dependency (start Ableton, install AbletonOSC)
- Ambiguous fix (multiple solutions)
- State: STOP with clear instruction

**Decision tree**:
```
if category in [1, 2] and Ableton not running:
    action_type = USER_ACTION (start Ableton)
elif category == 3:
    action_type = FIX_AUTO (regenerate fingerprint)
elif category == 4 and file missing:
    action_type = FIX_AUTO (regenerate test file)
elif category == 5 and dir missing:
    action_type = FIX_AUTO (mkdir)
elif category == 6 and not installed:
    action_type = FIX_AUTO (pip install)
else:
    action_type = PROBE (read state first)
```

---

**Step 4: Choose Next Single Command**

**Preference order**:
1. **Category-specific probe** (see Section B)
2. **Read artifact state**: `cat data/caches/model_cache.json`
3. **Environment check**: `python3 -m compileall src/flaas/`
4. **Targeted fix**: Edit one file or run one fix command
5. **Re-run validation**: Original command from PLAN

**Examples by category**:

| Category | Next Command (in order of preference) |
|----------|---------------------------------------|
| 1 (Connectivity) | `flaas ping --wait`, `ps aux \| grep Ableton`, `ls ~/Music/.../AbletonOSC` |
| 2 (Config) | `flaas scan`, `cat model_cache.json \| jq .tracks[0]`, `flaas util-gain-norm 0 0 0.5` |
| 3 (Schema) | `flaas scan && flaas plan-gain input/test.wav` (auto-fix) |
| 4 (Audio) | `ls -lh input/test.wav`, `file input/test.wav`, regenerate script |
| 5 (Permissions) | `ls -la data/`, `mkdir -p data/*` |
| 6 (Packaging) | `pip show flaas`, `python3 -m compileall src/`, `pip install -e .` |

---

**Step 5: Execute Decision**

**If action_type == PROBE**:
- Execute next command (read-only)
- Paste output
- State: Stay in DIAGNOSE, analyze probe result

**If action_type == FIX_AUTO**:
- Execute fix command
- Re-run original validation
- Paste verification output
- State: VERIFY

**If action_type == USER_ACTION**:
- Print clear instruction for user
- State: STOP
- Example: "Ableton Live is not running. Start Ableton, load AbletonOSC, then re-run: `flaas ping --wait`"

---

## D. Paste Templates

### Template 1: Normal Success
**Minimum required context**:
```
✅ **Step [N] complete.**

**Validation output:**
```
[exact terminal output, full stdout+stderr]
```

**Files changed:**
- [file1]
- [file2]

**git push output:**
```
[exact git push output]
```
```

**Example**:
```
✅ **Step 100 complete.**

**Validation output:**
```
ok: ('ok',)
```

**Files changed:**
- src/flaas/eq8.py (created)
- src/flaas/cli.py (modified)

**git push output:**
```
[main abc1234] feat: add EQ Eight device class detection
 2 files changed, 45 insertions(+)
To https://github.com/trev-trev-trev/finishline-audio.git
   9497db6..abc1234  main -> main
```
```

---

### Template 2: Error Encountered
**Minimum required context**:
```
⚠️ **Error during Step [N].**

**Command that failed:**
```bash
[exact command]
```

**Terminal output:**
```
[exact stdout+stderr, include full traceback]
```

**Exit code:** [N]

**Error category:** [1-6 or UNKNOWN]

**Next probe:**
```bash
[single diagnostic command]
```
```

**Example**:
```
⚠️ **Error during Step 100.**

**Command that failed:**
```bash
flaas scan
```

**Terminal output:**
```
Traceback (most recent call last):
  File "src/flaas/osc_rpc.py", line 35, in request_once
    args = q.get(timeout=timeout_sec)
TimeoutError: Timed out waiting for reply on :11001 for /live/song/get/num_tracks
```

**Exit code:** 1

**Error category:** 1 (Connectivity / Ports)

**Next probe:**
```bash
flaas ping --wait --timeout 5.0
```
```

---

### Template 3: Partial Success
**Minimum required context**:
```
⚠️ **Step [N] partial.**

**What worked:**
```bash
[successful command]
```
[successful output]

**What failed:**
```bash
[failed command]
```
[error output]

**Exit code:** [N]

**Analysis:** [1-2 sentences on what succeeded vs failed]

**Next action:** [edit vs probe vs user-action]
```

**Example**:
```
⚠️ **Step 100 partial.**

**What worked:**
```bash
python3 -m compileall src/flaas/
```
Listing 'src/flaas/'...
Compiling 'src/flaas/eq8.py'...

**What failed:**
```bash
flaas eq-cut 0 1 --band 2 --gain -2.0
```
flaas: error: unrecognized arguments: --band 2 --gain -2.0

**Exit code:** 2

**Analysis:** Module compiles but CLI wiring incomplete (missing argument parser).

**Next action:** Add argparse wiring for eq-cut command.
```

---

### Template 4: Ambiguous Output
**Use when unclear if success or failure**:
```
❓ **Step [N] unclear.**

**Command:**
```bash
[command]
```

**Output:**
```
[full output]
```

**Exit code:** [N]

**Ambiguity:** [what's unclear - success markers present but warnings too?]

**Clarification needed:** [specific question]
```

**Example**:
```
❓ **Step 100 unclear.**

**Command:**
```bash
flaas loop input/test.wav
```

**Output:**
```
MEASURE: LUFS=-17.72 peak_dBFS=-13.98
WARNING: delta clamped to 0.250 (raw would exceed clamp).
CUR_LINEAR: 0.000  DELTA: 0.250
APPLIED: Utility.Gain 0.000 -> 0.250 (norm 0.500->0.625)
DONE: planned+applied (norm=0.625)
```

**Exit code:** 0

**Ambiguity:** Exit 0 (success) but WARNING present. Is clamping expected or a problem?

**Clarification needed:** Is WARNING normal behavior or should clamp be adjusted?
```

---

### Commit Message Template
**Format**:
```
<type>: <imperative description>

<optional body: what/why, not how>
```

**Types**:
- `feat:` - New feature or capability
- `fix:` - Bug fix
- `chore:` - Maintenance (deps, config, build)
- `docs:` - Documentation only
- `test:` - Test additions/fixes
- `refactor:` - Code restructure (no behavior change)

**Examples**:
```
feat: add EQ Eight parameter query

fix: fingerprint enforcement in apply

chore: update dependencies to latest

docs: add surface area registry
```

---

## E. Stability Gates (G1-G5)

### Gate G1: OSC Health + Scan Stability
**Purpose**: Verify basic Ableton communication and set structure query.

**Commands**:
```bash
# 1.1: Bidirectional ping
flaas ping --wait

# 1.2: Scan Live set
flaas scan

# 1.3: Verify scan output
cat data/caches/model_cache.json | jq '{ok, num_tracks, fingerprint}'
```

**Expected outputs**:
```
# 1.1:
ok: ('ok',)

# 1.2:
data/caches/model_cache.json

# 1.3:
{
  "ok": true,
  "num_tracks": 1,
  "fingerprint": "a1b2c3..." (64 hex chars)
}
```

**Pass criteria**:
- ✅ All 3 commands exit 0
- ✅ Ping returns `('ok',)` tuple
- ✅ Scan writes valid JSON
- ✅ JSON has `ok: true`, `num_tracks > 0`, non-empty fingerprint

**Fail scenarios**:
- ❌ Ping timeout → Category 1 error
- ❌ Scan `ok: false` → Category 2 error
- ❌ Fingerprint empty or missing → Scan bug (escalate)

**Frequency**: Run on every session start, after Ableton restart.

---

### Gate G2: Fingerprint Safety + Action Correctness
**Purpose**: Verify fingerprint enforcement prevents stale actions.

**Commands**:
```bash
# 2.1: Generate baseline actions
flaas reset
flaas plan-gain input/test.wav

# 2.2: Check actions fingerprint
cat data/actions/actions.json | jq -r '.live_fingerprint'

# 2.3: Apply should succeed (fingerprint matches)
flaas apply

# 2.4: Modify Live set (user manually adds track in Ableton)
echo "USER: Add a track in Ableton now."

# 2.5: Re-plan (new fingerprint)
flaas plan-gain input/test.wav

# 2.6: Old actions should be rejected
cat > /tmp/old_actions.json < data/actions/actions.json.backup
cp /tmp/old_actions.json data/actions/actions.json
flaas apply  # Should FAIL
```

**Expected outputs**:
```
# 2.1:
data/actions/actions.json
CUR_LINEAR: 0.000  DELTA: 0.XXX

# 2.2:
a1b2c3... (64 hex chars, matches scan)

# 2.3:
APPLIED: Utility.Gain 0.000 -> 0.XXX (norm 0.500->0.XXX)

# 2.6:
RuntimeError: Live fingerprint mismatch: expected a1b2c3..., got d4e5f6...
```

**Pass criteria**:
- ✅ 2.3 succeeds (apply with matching fingerprint)
- ✅ 2.6 fails with RuntimeError (apply rejects stale fingerprint)
- ✅ Error message includes expected vs actual fingerprints

**Fail scenarios**:
- ❌ 2.3 fails despite matching fingerprint → Apply bug
- ❌ 2.6 succeeds despite mismatched fingerprint → Enforcement bypassed (critical bug)

**Frequency**: Run after changes to `apply.py` or `scan.py`.

---

### Gate G3: Audio Analysis Correctness
**Purpose**: Verify audio analysis produces expected values on known WAV.

**Commands**:
```bash
# 3.1: Generate test WAV (known properties)
python3 - <<'PY'
import numpy as np, soundfile as sf, os
os.makedirs("input", exist_ok=True)
sr = 48000
t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
x = 0.2*np.sin(2*np.pi*440*t)  # -13.98 dBFS peak, ~-17.7 LUFS
sf.write("input/test.wav", x, sr)
print(f"Generated: {x.shape[0]} samples at {sr} Hz, peak={np.max(np.abs(x)):.4f}")
PY

# 3.2: Analyze
flaas analyze input/test.wav

# 3.3: Verify values
cat data/reports/analysis.json | jq '{peak_dbfs, lufs_i}'
```

**Expected outputs**:
```
# 3.1:
Generated: 96000 samples at 48000 Hz, peak=0.2000

# 3.2:
data/reports/analysis.json

# 3.3:
{
  "peak_dbfs": -13.98 (±0.1),
  "lufs_i": -17.7 (±0.5)
}
```

**Pass criteria**:
- ✅ All 3 commands exit 0
- ✅ Peak dBFS within ±0.1 of -13.98
- ✅ LUFS-I within ±0.5 of -17.7
- ✅ Analysis JSON includes all required fields

**Fail scenarios**:
- ❌ Peak off by >0.1 dB → Calculation bug
- ❌ LUFS off by >0.5 LU → LUFS meter bug
- ❌ ValueError empty audio → WAV generation bug

**Frequency**: Run after changes to `analyze.py`, `audio_io.py`.

---

### Gate G4: Apply Correctness + Readback
**Purpose**: Verify parameter changes are applied correctly and readable.

**Commands**:
```bash
# 4.1: Reset to known state
flaas reset
flaas verify

# 4.2: Set specific value
flaas util-gain-linear 0 0 0.3

# 4.3: Verify readback matches
flaas verify

# 4.4: Compute expected norm
python3 - <<'PY'
from flaas.param_map import get_param_range, linear_to_norm
pr = get_param_range(0, 0, 9)
print(f"Expected norm: {linear_to_norm(0.3, pr):.3f}")
PY

# 4.5: Apply delta via actions
echo '{"schema_version":"1.0","created_at_utc":"2026-02-22T00:00:00Z","live_fingerprint":"'$(flaas scan 2>&1 | tail -1 | jq -r .fingerprint)'","actions":[{"track_role":"MASTER","device":"Utility","param":"Gain","delta_db":0.1}]}' > data/actions/actions.json
flaas apply

# 4.6: Verify delta applied
flaas verify
```

**Expected outputs**:
```
# 4.1:
sent
0.500 (center)

# 4.2:
sent

# 4.3:
0.650 (or similar, depends on param range)

# 4.4:
Expected norm: 0.650

# 4.5:
APPLIED: Utility.Gain 0.650 -> 0.750 (norm 0.650->0.750)

# 4.6:
0.750
```

**Pass criteria**:
- ✅ 4.1: Reset returns to center (0.500)
- ✅ 4.3: Readback matches set value (within ±0.01)
- ✅ 4.4: Expected norm calculated correctly
- ✅ 4.6: Delta applied (0.650 + 0.1 → 0.750, accounting for linear→norm conversion)

**Fail scenarios**:
- ❌ 4.3 ≠ 4.4: Conversion bug in `linear_to_norm`
- ❌ 4.6 ≠ 4.5: Delta not applied correctly (relative vs absolute bug)

**Frequency**: Run after changes to `apply.py`, `util.py`, `param_map.py`.

---

### Gate G5: Render Automation Reliability (Future)
**Purpose**: Verify automated export/re-render (when implemented).

**Status**: 🚧 Not yet implemented (requires `/live/song/export/*` endpoint mapping).

**Commands** (hypothetical):
```bash
# 5.1: Trigger export
flaas export --track master --output output/test_export.wav

# 5.2: Wait for export completion
timeout 30 bash -c 'until [ -f output/test_export.wav ]; do sleep 1; done' && echo "Export complete"

# 5.3: Verify file exists and is valid
ls -lh output/test_export.wav
file output/test_export.wav

# 5.4: Analyze exported file
flaas analyze output/test_export.wav

# 5.5: Compare with expected (pre-export scan + known Utility gain)
cat data/reports/analysis.json | jq '.lufs_i'
```

**Expected outputs** (TBD, pending discovery):
```
# 5.1:
Export started (or "Export command sent")

# 5.2:
Export complete

# 5.3:
-rw-r--r-- 1 user staff 384044 ... output/test_export.wav
output/test_export.wav: RIFF (little-endian) data, WAVE audio, ...

# 5.4:
data/reports/analysis.json

# 5.5:
-XX.X (depends on Utility gain setting)
```

**Pass criteria** (TBD):
- ✅ Export command triggers successfully
- ✅ File appears within timeout
- ✅ File is valid WAV (per `file` command)
- ✅ Analysis succeeds
- ✅ LUFS value reflects applied gain

**Fail scenarios** (TBD):
- ❌ Export timeout (>30s, no file)
- ❌ File corrupt or empty
- ❌ LUFS unchanged (export didn't include Utility effect)

**VERIFY**: Does AbletonOSC support `/live/song/export/*`?  
**Discovery probe**:
```bash
python3 -c "from flaas.osc_rpc import *; help='Check AbletonOSC docs'; print(help)"
# Manual: Review ideoforms/AbletonOSC README for export endpoints
```

**Frequency**: Run after implementing export automation.

---

## F. Next 12 Atomic Tasks

**Context**: Starting from current state (MVP with Utility Gain control).  
**Goal**: Progress toward post-MVP capabilities (multi-stem, EQ, export automation).

---

### Task 1: Discover `/live/song/export/*` endpoint existence
**Type**: Discovery Mode (read-only)

**Action**: Query AbletonOSC documentation and attempt probe.

**Command**:
```bash
# Check AbletonOSC GitHub for export endpoints
curl -s https://raw.githubusercontent.com/ideoforms/AbletonOSC/master/README.md | grep -i export

# Attempt probe (may timeout if unsupported)
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once
try:
    resp = request_once(OscTarget(), "/live/song/export/audio", [], timeout_sec=3.0)
    print(f"SUCCESS: {resp}")
except TimeoutError as e:
    print(f"TIMEOUT: Endpoint may not exist or requires different args")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
PY
```

**Expected output**:
- **If supported**: Response with export status or parameters
- **If unsupported**: `TIMEOUT: Endpoint may not exist`

**Success criteria**: Determination of endpoint existence (yes/no/unknown).

**Rollback**: None (read-only probe).

**Next task if supported**: Task 2 (map export parameters).  
**Next task if unsupported**: Skip to Task 5 (EQ Eight discovery).

---

### Task 2: Map `/live/song/export/audio` parameters (conditional on Task 1)
**Type**: Discovery Mode

**Action**: Determine request format for export endpoint.

**Command**:
```bash
# Try various request formats
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once

formats = [
    ([], "empty list"),
    (["output/test.wav"], "filepath only"),
    ([0, 1, "output/test.wav"], "track range + filepath"),
]

for args, desc in formats:
    print(f"\nTrying: {desc}")
    try:
        resp = request_once(OscTarget(), "/live/song/export/audio", args, timeout_sec=5.0)
        print(f"  SUCCESS: {resp}")
        break
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
PY
```

**Expected output**: One format succeeds, reveals required arguments.

**Success criteria**: Document request format in engineering notebook.

**Rollback**: None (read-only).

---

### Task 3: Implement `export.py` module with validated endpoint
**Type**: Shipping Mode (depends on Task 1-2)

**Action**: Create module wrapping export endpoint.

**Command**:
```bash
cat > src/flaas/export.py <<'EOF'
from __future__ import annotations
from pathlib import Path
from flaas.osc_rpc import OscTarget, request_once

def export_master(
    output_path: str | Path,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 30.0,
) -> None:
    """
    Trigger Ableton export via OSC.
    
    Blocks until export completes or times out.
    """
    resp = request_once(
        target,
        "/live/song/export/audio",
        [str(output_path)],  # Adjust based on Task 2 discovery
        timeout_sec=timeout_sec,
    )
    print(f"Export response: {resp}")
EOF

python3 -m compileall src/flaas/export.py
```

**Expected output**:
```
Compiling 'src/flaas/export.py'...
```

**Success criteria**: Module compiles without syntax errors.

**Rollback**: `rm src/flaas/export.py`

---

### Task 4: Add `flaas export` CLI command + validate
**Type**: Shipping Mode

**Action**: Wire export module to CLI, test end-to-end.

**Command**:
```bash
# Update cli.py (agent edits file to add export parser + handler)

# Validate CLI wiring
flaas export --help

# Test export (requires Ableton with track to export)
flaas export --output output/test_export.wav

# Verify file created
ls -lh output/test_export.wav
file output/test_export.wav
```

**Expected output**:
```
# flaas export --help:
usage: flaas export [-h] [--output OUTPUT] [--timeout TIMEOUT]

# flaas export:
Export response: (...)
Export started or completed

# ls:
-rw-r--r-- 1 user staff 384044 ... output/test_export.wav

# file:
output/test_export.wav: RIFF ... WAVE audio
```

**Success criteria**:
- ✅ `--help` works
- ✅ Export command triggers
- ✅ File appears
- ✅ File is valid WAV

**Rollback**: Revert cli.py changes, remove export.py.

---

### Task 5: Discover EQ Eight device class name + param count
**Type**: Discovery Mode

**Action**: Query EQ device in Live set to map parameter structure.

**Command**:
```bash
# Requires: Ableton Live set with EQ Eight on a track

# 5.1: Scan for EQ devices
flaas scan
cat data/caches/model_cache.json | jq '.tracks[] | select(.devices[] | .class_name | contains("Eq")) | {track_id, name, devices: [.devices[] | select(.class_name | contains("Eq"))]}'

# 5.2: Get EQ parameter names (assumes track 1 device 0 has EQ)
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once
try:
    # Adjust track_id/device_id based on 5.1 output
    resp = request_once(OscTarget(), "/live/device/get/parameters/name", [1, 0], timeout_sec=3.0)
    print(f"EQ params: {resp}")
    for i, name in enumerate(resp[2:], start=0):  # Skip track_id, device_id
        print(f"  param_{i}: {name}")
except Exception as e:
    print(f"ERROR: {e}")
PY
```

**Expected output**:
```
# 5.1:
{
  "track_id": 1,
  "name": "Audio",
  "devices": [
    {
      "index": 0,
      "name": "EQ Eight",
      "class_name": "Eq8"
    }
  ]
}

# 5.2:
EQ params: (1, 0, 'Band 1 Frequency', 'Band 1 Gain', 'Band 1 Q', ...)
  param_0: Band 1 Frequency
  param_1: Band 1 Gain
  param_2: Band 1 Q
  ...
```

**Success criteria**: EQ class name identified (`Eq8`), parameter names listed.

**Rollback**: None (read-only).

**Next**: Document in engineering notebook, Task 6 (EQ adapter).

---

### Task 6: Create `eq8.py` adapter for band control
**Type**: Shipping Mode (depends on Task 5)

**Action**: Build EQ Eight parameter wrapper.

**Command**:
```bash
cat > src/flaas/eq8.py <<'EOF'
from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget
from flaas.param_map import get_param_range, linear_to_norm

# Parameter offsets (per band): [freq, gain, q, filter_type, enabled]
# For 8 bands, params span 0-39 (5 params * 8 bands)
# Band 1: params 0-4, Band 2: params 5-9, etc.

def _band_param_offset(band: int, param_name: str) -> int:
    """Get parameter ID for EQ band parameter."""
    band_base = (band - 1) * 5  # 0-indexed bands
    offsets = {"freq": 0, "gain": 1, "q": 2, "type": 3, "enabled": 4}
    if param_name not in offsets:
        raise ValueError(f"Unknown param: {param_name}")
    return band_base + offsets[param_name]

def set_band_gain(
    track_id: int,
    device_id: int,
    band: int,  # 1-8
    gain_db: float,  # Linear gain (min/max from OSC)
    target: OscTarget = OscTarget(),
) -> None:
    """
    Set EQ Eight band gain.
    
    Note: gain_db is in device's linear units (from min/max), not actual dB.
    """
    param_id = _band_param_offset(band, "gain")
    pr = get_param_range(track_id, device_id, param_id, target=target)
    norm = linear_to_norm(gain_db, pr)
    
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, param_id, float(norm)])
    print(f"Set EQ band {band} gain to {gain_db:.2f} (norm {norm:.3f})")
EOF

python3 -m compileall src/flaas/eq8.py
```

**Expected output**:
```
Compiling 'src/flaas/eq8.py'...
```

**Success criteria**: Module compiles, functions defined.

**Rollback**: `rm src/flaas/eq8.py`

---

### Task 7: Add `flaas eq-gain` CLI command + validate
**Type**: Shipping Mode

**Action**: Wire EQ adapter to CLI, test on live Ableton.

**Command**:
```bash
# Agent edits cli.py to add eq-gain parser + handler

# Validate CLI wiring
flaas eq-gain --help

# Test on Ableton (requires EQ Eight on track 1 device 0)
flaas eq-gain 1 0 --band 2 --gain -2.0

# Verify via scan (parameter names don't show values, need readback)
python3 - <<'PY'
from flaas.osc_rpc import OscTarget, request_once
from flaas.eq8 import _band_param_offset
param_id = _band_param_offset(2, "gain")
resp = request_once(OscTarget(), "/live/device/get/parameter/value", [1, 0, param_id])
print(f"EQ band 2 gain (norm): {resp[3]}")
PY
```

**Expected output**:
```
# --help:
usage: flaas eq-gain [-h] track_id device_id --band BAND --gain GAIN

# Command:
Set EQ band 2 gain to -2.00 (norm 0.XXX)

# Verify:
EQ band 2 gain (norm): 0.XXX (should be <0.5 for negative gain)
```

**Success criteria**:
- ✅ Help text displays
- ✅ Command executes without error
- ✅ Readback shows changed parameter

**Rollback**: Revert cli.py, remove eq8.py.

---

### Task 8: Generate test WAV with known frequency content
**Type**: Shipping Mode (audio intelligence)

**Action**: Create multi-band test signal for EQ validation.

**Command**:
```bash
python3 - <<'PY'
import numpy as np, soundfile as sf, os

os.makedirs("input", exist_ok=True)
sr = 48000
dur = 2.0
t = np.linspace(0, dur, int(sr * dur), endpoint=False)

# Multi-band signal
sub_bass = 0.1 * np.sin(2*np.pi*40*t)    # 40 Hz
mid = 0.1 * np.sin(2*np.pi*320*t)        # 320 Hz (mud range)
high = 0.1 * np.sin(2*np.pi*4000*t)      # 4 kHz (presence)

x = sub_bass + mid + high
sf.write("input/test_multiband.wav", x, sr)

print(f"Generated: {x.shape[0]} samples, peak={np.max(np.abs(x)):.4f}")
print("Bands: 40 Hz, 320 Hz, 4000 Hz (equal amplitude)")
PY

flaas analyze input/test_multiband.wav
cat data/reports/analysis.json | jq '{peak_dbfs, lufs_i}'
```

**Expected output**:
```
Generated: 96000 samples, peak=0.3000
Bands: 40 Hz, 320 Hz, 4000 Hz (equal amplitude)

data/reports/analysis.json

{
  "peak_dbfs": -10.46,
  "lufs_i": -XX.X
}
```

**Success criteria**: Multi-band WAV generated, analysis succeeds.

**Rollback**: `rm input/test_multiband.wav`

---

### Task 9: Add band energy analysis to `analyze.py`
**Type**: Shipping Mode (audio intelligence)

**Action**: Implement frequency band RMS calculation.

**Command**:
```bash
# Agent edits analyze.py to add band energy analysis
# Uses scipy.signal.butter + filtfilt for bandpass filters

python3 -m compileall src/flaas/analyze.py

# Validate on test file
python3 - <<'PY'
from flaas.analyze import analyze_wav
result = analyze_wav("input/test_multiband.wav")
print(f"Peak: {result.peak_dbfs:.2f}, LUFS: {result.lufs_i:.2f}")
# Should also print band energies if implemented
PY
```

**Expected output**:
```
Compiling 'src/flaas/analyze.py'...

Peak: -10.46, LUFS: -XX.X
(If band energy added: Sub: -XX dB, Mid: -XX dB, High: -XX dB)
```

**Success criteria**: Module compiles, analysis runs without error.

**Rollback**: `git checkout -- src/flaas/analyze.py`

---

### Task 10: Create true-peak estimator module
**Type**: Shipping Mode (audio intelligence)

**Action**: Add oversampling true-peak calculation.

**Command**:
```bash
cat > src/flaas/truepeak.py <<'EOF'
from __future__ import annotations
import numpy as np
from scipy import signal

def estimate_true_peak_dbtp(audio: np.ndarray, sr: int, oversample: int = 4) -> float:
    """
    Estimate true peak via oversampling.
    
    Note: Not ITU-R BS.1770 compliant oversampling filter,
    but good enough for safety margin estimation.
    """
    if audio.size == 0:
        return -float("inf")
    
    # Simple linear interpolation upsample
    upsampled = signal.resample(audio, len(audio) * oversample)
    
    peak = float(np.max(np.abs(upsampled)))
    if peak == 0.0:
        return -float("inf")
    
    return float(20.0 * np.log10(peak))
EOF

python3 -m compileall src/flaas/truepeak.py

# Test on known file
python3 - <<'PY'
from flaas.audio_io import read_mono_float
from flaas.truepeak import estimate_true_peak_dbtp
audio, sr = read_mono_float("input/test.wav")
tp = estimate_true_peak_dbtp(audio, sr)
print(f"True peak estimate: {tp:.2f} dBTP")
PY
```

**Expected output**:
```
Compiling 'src/flaas/truepeak.py'...

True peak estimate: -13.50 dBTP (should be slightly higher than peak dBFS)
```

**Success criteria**: Module compiles, true-peak > peak dBFS on test file.

**Rollback**: `rm src/flaas/truepeak.py`

---

### Task 11: Add `--true-peak` flag to `flaas analyze`
**Type**: Shipping Mode

**Action**: Integrate true-peak into analysis command.

**Command**:
```bash
# Agent edits analyze.py to add true_peak field to AnalysisResult
# Agent edits cli.py to add --true-peak flag

python3 -m compileall src/flaas/analyze.py src/flaas/cli.py

flaas analyze input/test.wav --true-peak
cat data/reports/analysis.json | jq '{peak_dbfs, true_peak_dbtp}'
```

**Expected output**:
```
Compiling 'src/flaas/analyze.py'...
Compiling 'src/flaas/cli.py'...

data/reports/analysis.json

{
  "peak_dbfs": -13.98,
  "true_peak_dbtp": -13.50
}
```

**Success criteria**:
- ✅ Compilation succeeds
- ✅ Flag accepted
- ✅ JSON includes true_peak_dbtp
- ✅ True-peak >= peak dBFS (always)

**Rollback**: Revert analyze.py and cli.py changes.

---

### Task 12: Add stem naming contract validation
**Type**: Shipping Mode (multi-stem foundation)

**Action**: Create module to parse and validate stem file naming.

**Command**:
```bash
cat > src/flaas/stems.py <<'EOF'
from __future__ import annotations
from pathlib import Path
from typing import Optional
import re

# Naming contract: {song}_{role}.wav
# Roles: MASTER, VOCAL_LEAD, VOCAL_BG, BASS, DRUMS, KEYS, etc.

STEM_PATTERN = re.compile(r'^(.+)_(MASTER|VOCAL_LEAD|VOCAL_BG|BASS|DRUMS|KEYS|OTHER)\.wav$')

def parse_stem_filename(path: str | Path) -> tuple[str, str]:
    """
    Parse stem filename into (song_name, role).
    
    Raises ValueError if filename doesn't match contract.
    """
    filename = Path(path).name
    match = STEM_PATTERN.match(filename)
    if not match:
        raise ValueError(f"Invalid stem filename: {filename}. Expected: {{song}}_{{ROLE}}.wav")
    return match.group(1), match.group(2)

def validate_stem_set(paths: list[str | Path]) -> dict[str, list[str]]:
    """
    Validate a set of stem files.
    
    Returns: {song_name: [roles]}
    Raises ValueError if multiple songs or invalid naming.
    """
    stems = {}
    for path in paths:
        song, role = parse_stem_filename(path)
        if song not in stems:
            stems[song] = []
        if role in stems[song]:
            raise ValueError(f"Duplicate role {role} for song {song}")
        stems[song].append(role)
    
    if len(stems) > 1:
        raise ValueError(f"Multiple songs in stem set: {list(stems.keys())}")
    
    return stems
EOF

python3 -m compileall src/flaas/stems.py

# Test valid naming
python3 - <<'PY'
from flaas.stems import parse_stem_filename, validate_stem_set

# Valid examples
print(parse_stem_filename("track01_VOCAL_LEAD.wav"))
print(parse_stem_filename("mysong_BASS.wav"))

# Invalid example (should raise)
try:
    parse_stem_filename("invalid_name.wav")
except ValueError as e:
    print(f"Correctly rejected: {e}")

# Validate set
files = ["song_MASTER.wav", "song_VOCAL_LEAD.wav", "song_BASS.wav"]
print(validate_stem_set(files))
PY
```

**Expected output**:
```
Compiling 'src/flaas/stems.py'...

('track01', 'VOCAL_LEAD')
('mysong', 'BASS')
Correctly rejected: Invalid stem filename: invalid_name.wav. Expected: {song}_{ROLE}.wav
{'song': ['MASTER', 'VOCAL_LEAD', 'BASS']}
```

**Success criteria**:
- ✅ Module compiles
- ✅ Valid names parse correctly
- ✅ Invalid names raise ValueError
- ✅ Stem set validation detects duplicates and multi-song issues

**Rollback**: `rm src/flaas/stems.py`

---

### Task 13: Add `flaas validate-stems` CLI command
**Type**: Shipping Mode

**Action**: CLI command to check stem naming before analysis.

**Command**:
```bash
# Agent edits cli.py to add validate-stems parser + handler

flaas validate-stems --help

# Test with valid stems
touch input/song_MASTER.wav input/song_VOCAL_LEAD.wav input/song_BASS.wav
flaas validate-stems input/song_*.wav

# Test with invalid stem
touch input/invalid.wav
flaas validate-stems input/invalid.wav
```

**Expected output**:
```
# --help:
usage: flaas validate-stems [-h] stems [stems ...]

# Valid:
✓ song_MASTER.wav - MASTER
✓ song_VOCAL_LEAD.wav - VOCAL_LEAD
✓ song_BASS.wav - BASS
VALID: 3 stems for song 'song'

# Invalid:
ERROR: Invalid stem filename: invalid.wav. Expected: {song}_{ROLE}.wav
```

**Success criteria**:
- ✅ Help text works
- ✅ Valid stems pass
- ✅ Invalid stems fail with clear error

**Rollback**: Revert cli.py changes.

---

### Task 14: Add `--max-iterations` flag to `flaas loop`
**Type**: Shipping Mode (safety)

**Action**: Enforce hard iteration cap in loop.

**Command**:
```bash
# Agent edits loop.py to add iteration counter + max check
# Agent edits cli.py to add --max-iterations arg (default 5)

python3 -m compileall src/flaas/loop.py src/flaas/cli.py

flaas loop input/test.wav --dry --max-iterations 2
```

**Expected output**:
```
Compiling 'src/flaas/loop.py'...
Compiling 'src/flaas/cli.py'...

MEASURE: LUFS=-17.72 peak_dBFS=-13.98
CUR_LINEAR: 0.000  DELTA: 0.XXX
DRY_RUN: MASTER :: Utility.Gain += 0.XXX
DONE: planned (dry-run, no OSC)
```

**Success criteria**:
- ✅ Compilation succeeds
- ✅ Flag accepted
- ✅ Loop respects max iterations (future: test with real iterations)

**Rollback**: Revert loop.py and cli.py changes.

---

### Task 15: Add iteration timeline logging
**Type**: Shipping Mode (audit trail)

**Action**: Log each loop iteration to `data/timelines/{timestamp}.jsonl`.

**Command**:
```bash
# Agent edits loop.py to write JSONL log per iteration

python3 -m compileall src/flaas/loop.py

flaas reset
flaas loop input/test.wav --dry

# Check timeline log created
ls -lh data/timelines/
cat data/timelines/*.jsonl | tail -5
```

**Expected output**:
```
Compiling 'src/flaas/loop.py'...

MEASURE: ...
DONE: ...

-rw-r--r-- 1 user staff 256 ... data/timelines/2026-02-22T10-30-00.jsonl

{"iteration": 1, "timestamp": "...", "lufs_i": -17.72, "delta": 0.XXX, ...}
```

**Success criteria**:
- ✅ Timeline file created
- ✅ JSONL format (one JSON object per line)
- ✅ Includes iteration, timestamp, measurements, delta

**Rollback**: Revert loop.py changes, remove timeline file.

---

### Task 16: Add `flaas scan --verbose` to show all parameter names
**Type**: Discovery Mode (extended visibility)

**Action**: Optional verbose scan showing all device parameters.

**Command**:
```bash
# Agent edits scan.py to add verbose parameter query (optional)
# Agent edits cli.py to add --verbose flag to scan parser

python3 -m compileall src/flaas/scan.py src/flaas/cli.py

flaas scan --verbose
cat data/caches/model_cache.json | jq '.tracks[0].devices[0].parameters | length'
```

**Expected output**:
```
Compiling 'src/flaas/scan.py'...
Compiling 'src/flaas/cli.py'...

data/caches/model_cache.json

10 (or number of parameters for Utility device)
```

**Success criteria**:
- ✅ Verbose flag accepted
- ✅ model_cache.json includes parameters array (if --verbose)
- ✅ Regular scan (no --verbose) still works without parameters

**Rollback**: Revert scan.py and cli.py changes.

---

### Task 17: Add pre-flight environment check command
**Type**: Shipping Mode (reliability)

**Action**: Create `flaas doctor` command that checks environment.

**Command**:
```bash
cat > src/flaas/doctor.py <<'EOF'
from __future__ import annotations
import sys
from pathlib import Path
from flaas.osc_rpc import OscTarget, request_once

def run_doctor() -> int:
    """
    Run environment health checks.
    
    Returns: 0 if all pass, 1 if any fail.
    """
    checks = []
    
    # Check 1: Python version
    py_ver = sys.version_info
    py_ok = py_ver >= (3, 11)
    checks.append(("Python >=3.11", py_ok, f"{py_ver.major}.{py_ver.minor}"))
    
    # Check 2: OSC connectivity
    try:
        request_once(OscTarget(), "/live/test", "ok", timeout_sec=2.0)
        osc_ok = True
        osc_msg = "Connected"
    except Exception as e:
        osc_ok = False
        osc_msg = str(e)
    checks.append(("OSC connectivity", osc_ok, osc_msg))
    
    # Check 3: Data directories
    dirs = ["data/caches", "data/reports", "data/actions"]
    dirs_ok = all(Path(d).exists() for d in dirs)
    checks.append(("Data directories", dirs_ok, "All present" if dirs_ok else "Missing"))
    
    # Check 4: Input directory
    input_ok = Path("input").exists()
    checks.append(("Input directory", input_ok, "Exists" if input_ok else "Missing"))
    
    # Print results
    for name, ok, msg in checks:
        status = "✓" if ok else "✗"
        print(f"{status} {name}: {msg}")
    
    return 0 if all(ok for _, ok, _ in checks) else 1
EOF

python3 -m compileall src/flaas/doctor.py

# Agent adds to cli.py

flaas doctor
```

**Expected output**:
```
Compiling 'src/flaas/doctor.py'...

✓ Python >=3.11: 3.11
✓ OSC connectivity: Connected
✓ Data directories: All present
✓ Input directory: Exists
```

**Success criteria**:
- ✅ All checks pass (exit 0)
- ✅ Clear status indicators (✓/✗)

**Rollback**: `rm src/flaas/doctor.py`, revert cli.py.

---

### Task 18: Add `CHANGELOG.md` with version history
**Type**: Documentation

**Action**: Formalize version tracking.

**Command**:
```bash
cat > CHANGELOG.md <<'EOF'
# Changelog

All notable changes to FLAAS will be documented in this file.

## [0.0.2] - 2026-02-22

### Added
- Fingerprint-enforced action application
- Relative delta planning (bounded ±0.25)
- Loop safety stops (max gain 0.99)
- OSC request/response (RPC) support
- Real Live set scanning (tracks, devices, fingerprint)
- Utility Gain control (linear and normalized)
- Export guide command
- Audio verification command (PASS/FAIL)
- Manual loop workflow documentation
- Complete documentation reorganization

### Fixed
- OSC ping now sends "ok" string (not integer)
- Parameter values use normalized 0..1 (not dB)
- Apply uses relative delta (not absolute set)
- Parameter min/max queried via plural endpoints

## [0.0.1] - 2026-02-21

### Added
- Initial package structure (src layout)
- Basic CLI with --version
- OSC fire-and-forget ping
- Audio analysis (peak dBFS + LUFS-I)
- Compliance checking (targets)
- Action planning (gain delta)
- Apply dry-run

EOF

git add CHANGELOG.md
git commit -m "docs: add changelog for version tracking"
git push
```

**Expected output**:
```
[main XYZ] docs: add changelog for version tracking
 1 file changed, 35 insertions(+)
 create mode 100644 CHANGELOG.md

To https://github.com/trev-trev-trev/finishline-audio.git
   1ffe59a..XYZ  main -> main
```

**Success criteria**: CHANGELOG.md created and committed.

**Rollback**: `git reset --soft HEAD~1 && rm CHANGELOG.md`

---

## G. Decision Algorithm: Action Type Selection

### Input: Current FSM State + Output

**Decision table**:

| State | Exit Code | Patterns Matched | Action Type | Next State |
|-------|-----------|------------------|-------------|------------|
| RUN | 0 | Success patterns | COMMIT_DIRECT | COMMIT |
| RUN | ≠0 | Error category 1-6 | PROBE_CLASSIFY | DIAGNOSE |
| RUN | ≠0 | No patterns | ESCALATE | STOP |
| DIAGNOSE | 0 | Probe reveals fix | FIX_AUTO | FIX |
| DIAGNOSE | 0 | Probe reveals user action | STOP_INSTRUCT | STOP |
| DIAGNOSE | ≠0 | Probe fails | PROBE_NEXT | DIAGNOSE |
| FIX | - | Fix applied | VERIFY_RERUN | VERIFY |
| VERIFY | 0 | Success patterns | COMMIT_DIRECT | COMMIT |
| VERIFY | ≠0 | Iterations < 3 | PROBE_CLASSIFY | DIAGNOSE |
| VERIFY | ≠0 | Iterations >= 3 | ESCALATE | STOP |

---

### Action Type: COMMIT_DIRECT
**Trigger**: Validation passed on first try.

**Actions**:
1. `git add -A` (or specific files if listed)
2. Generate commit message (feat/fix/chore based on change type)
3. `git commit -m "..."`
4. `git push`
5. Paste push output

**No intermediate steps** (fast path).

---

### Action Type: PROBE_CLASSIFY
**Trigger**: Error detected, need to identify cause.

**Actions**:
1. Match error output against taxonomy patterns
2. Identify category (1-6)
3. Select category-specific probe
4. Execute probe (read-only)
5. Paste probe output

**Prefer read-only probes** (minimize side effects during diagnosis).

---

### Action Type: FIX_AUTO
**Trigger**: Root cause identified, fix is deterministic.

**Actions**:
1. Execute fix command (e.g., `mkdir`, `pip install`, `flaas scan`)
2. Re-run original validation
3. Paste verification output

**Automatic fixes** (no user confirmation):
- `mkdir -p data/*` (missing directories)
- `pip install -e .` (package not installed)
- `flaas scan && flaas plan-gain` (fingerprint mismatch)
- Regenerate test file (missing audio)

---

### Action Type: STOP_INSTRUCT
**Trigger**: Fix requires user action (external to system).

**Actions**:
1. Print clear instruction
2. Suggest validation command to run after fix
3. State: STOP
4. Do NOT commit, push, or modify files

**Examples**:
```
STOP: Ableton Live is not running.

Action required:
1. Start Ableton Live
2. Load a Live set with at least one track
3. Verify AbletonOSC loaded: Preferences → Control Surface → AbletonOSC

Then re-run: flaas ping --wait
```

---

### Action Type: ESCALATE
**Trigger**: Can't diagnose or fix after 3 attempts.

**Actions**:
1. Paste full context (all probe outputs)
2. State: STOP
3. Message: "Unable to resolve after 3 attempts. User input required."

**Escalation includes**:
- Original task specification
- All probe commands executed
- All probe outputs
- Current file states (list modified files)

---

## H. Stop Rules (When to STOP and Escalate)

### Immediate STOP Conditions

1. **Ambiguous task specification** (no deterministic validation)
2. **No Ableton running** (Category 1, user must start)
3. **AbletonOSC not installed** (Category 1, user must install)
4. **Empty Live set** (Category 2, user must create tracks)
5. **Missing Utility device** (Category 2, user must add)
6. **3 fix attempts exhausted** (VERIFY fails 3x)
7. **Unclassified error** (no taxonomy match)
8. **Circular dependency** (fix requires unfixed component)

### Conditional STOP Conditions

1. **Timeout on long-running command** (if not specified in PLAN)
   - Check if expected (e.g., large file analysis)
   - If unexpected, STOP and clarify

2. **Git conflict on push**
   - Paste conflict error
   - STOP (user resolves conflict manually)

3. **Schema version mismatch** (if future: old actions.json with new code)
   - Paste version error
   - STOP (user confirms migration or regeneration)

### Continue Conditions (NO STOP)

1. **Deterministic error** (Category 1-6 with known fix)
2. **Auto-fixable** (mkdir, pip install, fingerprint regen)
3. **Clear syntax error** (can fix and re-verify)
4. **Type/import error** (obvious fix)

---

## I. Rollback Procedures

### Scenario: Error Before First Commit
**State**: EDIT or RUN, no commit yet.

**Procedure**:
```bash
git status  # See modified files
git checkout -- src/flaas/module.py  # Revert specific file
# Or:
git checkout -- .  # Revert all changes
```

**Validation**: `git status` should show clean working tree.

---

### Scenario: Error After Commit (Not Pushed)
**State**: COMMIT succeeded locally, push not attempted yet.

**Procedure**:
```bash
git log -1 --oneline  # Confirm commit to revert
git reset --soft HEAD~1  # Uncommit, keep changes
# Fix issue
git add -A
git commit -m "fix: [description]"
git push
```

**Validation**: `git log` shows fix commit, not broken commit.

---

### Scenario: Error After Push
**State**: COMMIT + push succeeded, but issue discovered later.

**Procedure**:
```bash
# DO NOT rewrite history (no force push)
# Create new commit with fix
git add -A
git commit -m "fix: [description of issue]"
git push
```

**Validation**: Git history shows both commits (broken + fix).

---

### Scenario: Multiple Files Modified, Partial Revert Needed
**State**: Some edits good, some bad.

**Procedure**:
```bash
git add src/flaas/good_module.py  # Stage good changes
git checkout -- src/flaas/bad_module.py  # Revert bad changes
# Test good changes
flaas [validation]
# If pass:
git commit -m "feat: add good changes only"
# Re-attempt bad changes in next task
```

**Validation**: Only intended files staged (`git diff --cached`).

---

## J. Stability Gate Sequencing

**When to run gates** (checklist):

### On Session Start:
1. ✅ Run G1 (OSC health + scan stability)
2. If G1 fails → Fix before any development work

### After Module Changes:
- Changed `osc*.py` → Run G1
- Changed `scan.py` → Run G1 + G2
- Changed `analyze.py` → Run G3
- Changed `apply.py` or `param_map.py` → Run G4
- Changed `loop.py` → Run G1 + G3 + G4 (full golden path)

### Before Major Milestone:
- Run all implemented gates (G1-G4 currently)
- Document results in FINISHLINE_PROGRESS_INDEX.md

### After Git Pull:
- Run G1 (verify environment still works)
- If others collaborating: Run G2-G4 (detect breaking changes)

---

## K. Operational Checklist (Per Task)

### Pre-Task (PLAN State)
- [ ] Step number assigned
- [ ] Task is atomic (one file or one command)
- [ ] Exact bash commands specified
- [ ] Specific output to paste identified
- [ ] Expected success pattern defined

### During Task (EDIT → RUN)
- [ ] All file changes logged
- [ ] Validation command executed
- [ ] Full output captured (stdout + stderr + exit code)

### Post-Task (OBSERVE → COMMIT)
- [ ] Output classified (success or error category)
- [ ] If error: Probe executed, category determined
- [ ] If success: Changes committed
- [ ] Git push output pasted

### Error Recovery (DIAGNOSE → FIX → VERIFY)
- [ ] Error category identified (1-6)
- [ ] Probe executed (read-only preferred)
- [ ] Probe output analyzed
- [ ] Fix applied (targeted, not shotgun)
- [ ] Original validation re-run
- [ ] Max 3 fix attempts enforced

---

## L. Constants + Operational Parameters

### Timeouts
| Operation | Default | Reason | Override |
|-----------|---------|--------|----------|
| OSC ping | 2.0s | Fast connectivity test | `--timeout 5.0` |
| OSC param query | 3.0s | Slower than ping | In code |
| Command execution | 30s | Shell default | `block_until_ms` |
| Export (future) | 60s | Large file write | `--timeout 60` |

### Clamps
| Parameter | Value | Enforced In | Override |
|-----------|-------|-------------|----------|
| Delta linear | ±0.25 | `plan.py` | Function param `clamp_linear` |
| Normalized value | [0.0, 1.0] | `util.py`, `apply.py` | None (hard clamp) |
| Max gain norm | 0.99 | `loop.py` | None (safety invariant) |

### Retries
| Operation | Retry Count | Reason |
|-----------|-------------|--------|
| OSC query | 0 | Fail fast |
| File I/O | 0 | Fail fast |
| Git push | 0 | Manual conflict resolution |

**Philosophy**: No automatic retries. Deterministic errors, deterministic fixes.

---

## M. Terminal Output Signatures (Pattern Library)

### Success Signatures
```regex
^sent$                                  # Fire-and-forget OSC
^ok: \(.*\)$                           # OSC reply received
^APPLIED: Utility\.Gain                # Parameter changed
^PASS$                                  # Compliance achieved
^data/.*\.json$                         # File written
^To https://github\.com/.*/finishline  # Git push succeeded
^\[main [a-f0-9]{7}\]                  # Git commit SHA
```

### Warning Signatures (not errors, but noteworthy)
```regex
^WARNING: delta clamped                # Safety clamp triggered
^STOP: utility gain already near max   # Early exit (not error)
^SKIP: unsupported action              # Action ignored
```

### Error Signatures (classified)
```regex
TimeoutError.*waiting for reply        # Category 1
Connection refused                      # Category 1
ok.*false                              # Category 2
num_tracks.*0                          # Category 2
RuntimeError.*fingerprint              # Category 3
ValueError.*empty audio                # Category 4
FileNotFoundError.*\.wav               # Category 4
PermissionError                        # Category 5
cannot create directory                # Category 5
ModuleNotFoundError                    # Category 6
ImportError                            # Category 6
command not found: flaas               # Category 6
SyntaxError                            # Category 6
```

### Usage
**In OBSERVE state**:
```python
output = captured_stdout + captured_stderr

if re.search(r'^sent$', output, re.MULTILINE):
    classification = SUCCESS
elif re.search(r'TimeoutError.*waiting for reply', output):
    classification = ERROR_CATEGORY_1
elif re.search(r'RuntimeError.*fingerprint', output):
    classification = ERROR_CATEGORY_3
# ... etc
```

---

## N. Recovery Procedures (Operational Playbook)

### Procedure: Full System Reset
**When**: After multiple errors, unknown state, want clean slate.

**Steps**:
```bash
# 1. Reset Utility Gain
flaas reset

# 2. Clear caches
rm -rf data/caches/* data/reports/* data/actions/*

# 3. Regenerate test file
python3 - <<'PY'
import numpy as np, soundfile as sf, os
os.makedirs("input", exist_ok=True)
sr = 48000
t = np.linspace(0, 2.0, int(sr*2.0), endpoint=False)
x = 0.2*np.sin(2*np.pi*440*t)
sf.write("input/test.wav", x, sr)
print("Test WAV regenerated")
PY

# 4. Re-scan
flaas scan

# 5. Verify
flaas verify

# 6. Run golden path
flaas ping --wait && flaas scan && flaas analyze input/test.wav && echo "System ready"
```

**Validation**: All commands succeed, echo "System ready".

---

### Procedure: Recover from Bad Commit (Not Pushed)
**When**: Committed locally, realized it's broken, haven't pushed.

**Steps**:
```bash
git log -1 --oneline  # Confirm HEAD is the bad commit
git reset --soft HEAD~1  # Uncommit, keep file changes
git status  # See modified files
# Fix issues
python3 -m compileall src/flaas/  # Verify syntax
flaas [validation]  # Test fix
git add -A
git commit -m "fix: corrected [issue]"
git push
```

**Validation**: `git log` shows only fix commit on remote.

---

### Procedure: Recover from Bad Push
**When**: Pushed broken commit, discovered later.

**Steps**:
```bash
# DO NOT rewrite history (no reset --hard, no force push)
# Create fix commit

# Fix issues
[edit files]

# Validate fix
flaas [original_failing_command]

# Commit fix
git add -A
git commit -m "fix: resolve [issue] from commit [SHA]"
git push
```

**Validation**: Remote has both commits (broken + fix), tests pass.

---

### Procedure: Recover from Fingerprint Mismatch Loop
**When**: Repeatedly getting fingerprint mismatches, unclear why.

**Steps**:
```bash
# 1. Freeze Live set (don't modify in Ableton)

# 2. Force regenerate all artifacts
flaas scan
cat data/caches/model_cache.json | jq -r '.fingerprint' > /tmp/fp1.txt

# 3. Immediately re-scan (should match)
flaas scan
cat data/caches/model_cache.json | jq -r '.fingerprint' > /tmp/fp2.txt

# 4. Compare
diff /tmp/fp1.txt /tmp/fp2.txt && echo "Fingerprints stable" || echo "Fingerprints unstable (BUG)"

# 5. If stable, regenerate actions
flaas plan-gain input/test.wav

# 6. Immediately apply (should succeed)
flaas apply
```

**Validation**: If fingerprints stable, apply should succeed. If unstable, escalate (scan bug).

---

## O. FSM Transition Log Format (Future)

**Purpose**: Machine-readable log of all FSM transitions for replay/debugging.

**Format** (JSONL):
```json
{"timestamp": "ISO8601", "state": "PLAN", "trigger": "user_input", "artifact": "Step 100 specification"}
{"timestamp": "ISO8601", "state": "EDIT", "trigger": "parse_complete", "artifact": ["src/flaas/eq8.py"]}
{"timestamp": "ISO8601", "state": "RUN", "trigger": "edit_complete", "artifact": "flaas scan"}
{"timestamp": "ISO8601", "state": "OBSERVE", "trigger": "command_exit", "artifact": {"exit_code": 0, "output": "..."}}
{"timestamp": "ISO8601", "state": "COMMIT", "trigger": "validation_pass", "artifact": {"sha": "abc1234", "push": "..."}}
```

**Storage**: `data/timelines/fsm_{session_id}.jsonl`

**Usage**: Replay session to understand decision path.

**Implementation**: Future enhancement (not in MVP).

---

## P. Validation Matrix (Testing Checklist)

### Matrix: Gate × Module

| Gate | Modules Tested | Pass Criteria | Run After |
|------|----------------|---------------|-----------|
| G1 | `osc.py`, `osc_rpc.py`, `scan.py` | Ping + scan succeed | Any OSC change |
| G2 | `scan.py`, `apply.py`, `actions.py` | Fingerprint enforced | Schema changes |
| G3 | `audio_io.py`, `analyze.py` | Known WAV → expected values | Analysis changes |
| G4 | `util.py`, `apply.py`, `param_map.py`, `verify.py` | Set + readback match | Parameter logic |
| G5 | `export.py` (future) | Export + file valid | Export implementation |

### Matrix: Command × Expected Exit Code

| Command | Normal Exit | Error Exits | Validation |
|---------|-------------|-------------|------------|
| `flaas ping` | 0 | - | Always succeeds (fire-and-forget) |
| `flaas ping --wait` | 0 | 1 (timeout) | `ok: ('ok',)` or TimeoutError |
| `flaas scan` | 0 | - | Writes JSON even if scan fails (ok: false) |
| `flaas analyze <wav>` | 0 | 1 (file error) | analysis.json or exception |
| `flaas plan-gain <wav>` | 0 | 1 (OSC/file error) | actions.json + stdout |
| `flaas apply` | 0 | 1 (fingerprint) | APPLIED or RuntimeError |
| `flaas loop <wav>` | 0 | 0 (early exit) | DONE or STOP message |
| `flaas verify-audio <wav>` | 0 (PASS) | 1 (FAIL) | PASS/FAIL + exit code |

---

**End of Execution System Document**

This FSM is the operational contract for FLAAS development. Every state, transition, error, and decision is specified with exact terminal commands.

**Next**: Use this system for all development work. Update when patterns emerge or edge cases discovered.

**Regenerate unique line ledger after changes**: `python3 scripts/generate_unique_lines.py`
