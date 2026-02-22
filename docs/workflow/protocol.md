# One-Task Terminal Loop Protocol

**How this project was built: atomic tasks validated by terminal output.**

## Collaboration Contract

### Core Principle
**One atomic task at a time.**  
Each iteration completes a single, testable unit of work before proceeding.

### Roles
- **AI Agent (Cursor)**: Writes code changes, creates files, runs commands
- **Human Operator**: Provides task specification, pastes terminal output, validates results
- **Terminal**: Source of truth for validation

### State Machine

```
┌─────────┐
│  PLAN   │ User provides next single task (Step N)
└────┬────┘
     │
┌────▼────┐
│  EDIT   │ Agent writes code/config changes
└────┬────┘
     │
┌────▼────┐
│   RUN   │ Agent executes validation command(s)
└────┬────┘
     │
┌────▼─────┐
│ OBSERVE  │ Terminal outputs result
└────┬─────┘
     │
     ├─ SUCCESS ──┐
     │            │
     └─ FAILURE ──┤
                  │
            ┌─────▼─────┐
            │ DIAGNOSE  │ Analyze error class
            └─────┬─────┘
                  │
            ┌─────▼────┐
            │   FIX    │ Correct specific issue
            └─────┬────┘
                  │
            ┌─────▼─────┐
            │  VERIFY   │ Re-run validation
            └─────┬─────┘
                  │
            ┌─────▼─────┐
            │  COMMIT   │ git add/commit/push
            └───────────┘
```

## Task Atomicity Rules

### What counts as "one task"
✅ Add a Python module + CLI command  
✅ Fix a parameter mapping bug  
✅ Add schema versioning to actions.json  
✅ Implement OSC request/response  

❌ "Add full LUFS automation" (too broad)  
❌ "Make the system work" (undefined)  
❌ "Improve error handling everywhere" (no scope)  

### Task Specification Format (from user)
```
**Step NNN (one task): [imperative verb] [object].**

Run:
```bash
<exact commands to execute>
```

Paste the output of [specific command].
```

### Output Requirement
Every task MUST produce observable terminal output.  
The agent MUST paste this output back to validate success.

## Error Taxonomy

### 1. OSC / Connectivity Errors
**Symptoms**:
- `TimeoutError: Timed out waiting for reply`
- `Connection refused`
- Ping fails with `--wait`

**Single-command probe**:
```bash
flaas ping --wait
```

**Triage**:
- Check AbletonOSC installed: `ls ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC`
- Check Live open with correct Control Surface
- Check ports not blocked: `lsof -i :11000 -i :11001`

### 2. Ableton Configuration Errors
**Symptoms**:
- Scan returns 0 tracks
- Device endpoints fail
- Utility not found at track 0 device 0

**Single-command probe**:
```bash
flaas scan
cat data/caches/model_cache.json
```

**Triage**:
- Verify Ableton has tracks
- Verify track 0 device 0 is Utility (StereoGain)
- Run `flaas util-gain-norm 0 0 0.5` to test direct control

### 3. Schema / Fingerprint Mismatch
**Symptoms**:
- `RuntimeError: Live fingerprint mismatch`
- actions.json rejected

**Single-command probe**:
```bash
flaas scan  # regenerate fingerprint
flaas plan-gain input/test.wav  # regenerate actions
```

**Triage**:
- Live set changed (tracks added/removed/reordered)
- Devices changed on master track
- Solution: Re-scan and re-plan

### 4. Audio Analysis Errors
**Symptoms**:
- `ValueError: empty audio`
- Peak/LUFS calculation errors
- File not found

**Single-command probe**:
```bash
flaas analyze input/test.wav
cat data/reports/analysis.json
```

**Triage**:
- Verify WAV file exists and is valid
- Check sample rate (48kHz required)
- Regenerate test file if needed

### 5. Path / Permissions Errors
**Symptoms**:
- `PermissionError`
- `FileNotFoundError`
- Directory creation fails

**Single-command probe**:
```bash
ls -la data/
mkdir -p data/caches data/reports data/actions
```

**Triage**:
- Verify directories exist
- Check write permissions
- Verify relative paths from repo root

### 6. Packaging / Import Errors
**Symptoms**:
- `ModuleNotFoundError`
- `ImportError`
- Command not found

**Single-command probe**:
```bash
python3 -m pip install -e .
python3 -m flaas.cli --help
```

**Triage**:
- Verify venv activated
- Reinstall: `pip install -e .`
- Check `PYTHONPATH` if needed

## Paste Templates

### Normal Success Paste
```
✅ **Done! [Task name].**

**git push output:**
[exact terminal output]

**What was added/changed:**
- [bullet list of changes]

[Brief validation of correctness]
```

### Error Encountered Paste
```
⚠️ **Error encountered during [command].**

**Terminal output:**
[exact error output]

**Error class**: [OSC/Config/Schema/Audio/Path/Package]

**Next probe**:
[single command to diagnose]
```

### Partial Success Paste
```
✅ **Partial success - [what worked].**
⚠️ **Issue**: [what failed]

**Working output:**
[successful command output]

**Failed output:**
[error command output]

**Fix required**: [specific next action]
```

## Decision Algorithm: Choosing Next Command

### After code changes
1. If added new module → run `python3 -m compileall src/flaas/`
2. If added CLI command → run `flaas [command] --help`
3. If changed OSC logic → run `flaas ping --wait`
4. If changed analysis → run `flaas analyze input/test.wav`
5. If changed apply → run `flaas apply --dry`

### After validation passes
1. Stage changes: `git add -A` or specific files
2. Commit with descriptive message
3. Push: `git push`
4. Paste git push output

### If validation fails
1. DO NOT commit
2. Diagnose using error taxonomy (above)
3. Run single-command probe
4. Paste probe output
5. Apply targeted fix
6. Re-run original validation

## Stop Rules

### When to STOP and ask for clarification
- Ambiguous requirements (multiple valid interpretations)
- Missing external dependencies not in repo
- Requires Ableton Live open but can't verify state
- Circular dependency or architectural conflict

### When to CONTINUE without asking
- Error message is clear and fix is deterministic
- Standard Python/OSC issue with known solution
- Missing directory can be created
- Type/import error with obvious fix

## Rollback Rules

### Never committed yet
- Just revert file changes and try again
- `git checkout -- [file]` if needed

### Already committed locally
- `git reset --soft HEAD~1` to uncommit (keep changes)
- Fix and recommit

### Already pushed
- Create a new commit with fix (DO NOT rewrite history)
- Use commit message: `fix: [description of issue]`

## Safety Invariants

### Must NEVER bypass
1. **Fingerprint enforcement** in `apply` (unless explicitly disabled)
2. **Gain clamps** (±0.25 linear delta, 0.99 norm max)
3. **Parameter range validation** (0..1 normalized, min/max bounds)
4. **Relative delta application** (read current → add delta → set new)

### Can be temporarily disabled for debugging
- `enforce_fingerprint=False` in apply
- Dry-run modes (`--dry`)
- Manual parameter setting via `util-gain-norm`

## Iteration Hygiene

### Each task should
- Start with a clear step number and imperative statement
- Include exact bash commands to run
- Specify which output to paste back
- Complete with a commit

### Between tasks
- Terminal output is the handoff artifact
- No hidden state assumptions
- Each step is reproducible from command + output

### Documentation updates
- Update FINISHLINE_PROGRESS_INDEX.md when major milestones complete
- Update README.md when commands change
- Add to mvp_remaining.md when gaps discovered
