# Export Contract

**Status**: PERMANENT (canon)  
**Scope**: Defines "correct export" and verification

---

## Contract

**Correct export requires**:

1. **Rendered Track = Master**
   - Includes full Master device chain
   - NOT "All Individual Tracks" (stems)
   - NOT "Selected Tracks Only" (partial)

2. **Normalize = OFF**
   - No post-processing after render
   - Preserves peak levels set by Limiter
   - Critical for closed-loop control

3. **Loop/selection defines segment**
   - Exports only bracketed region
   - NOT entire project (saves time)
   - Typical: 4-8 bars for testing

4. **File stabilizes before measurement**
   - Size stable for 2+ seconds
   - Mtime stable for 2+ seconds
   - Prevents reading incomplete export

5. **Measurement reflects chain**
   - LUFS/peak values match expected from chain settings
   - If not, export path is broken (fix before continuing)

---

## Ableton Export Settings

**Menu**: File → Export Audio/Video

**Required**:
- Rendered Track: **Master**
- Normalize: **OFF**
- File Type: WAV
- Sample Rate: Match project (44.1 or 48 kHz)
- Bit Depth: 16-bit or 24-bit (24-bit preferred)

**Output folder**: `/Users/trev/Repos/finishline_audio_repo/output`

**Filename**: Set to exact path expected by automation

---

## Proof Tests

### Test 1: Master Mute

**Purpose**: Verify export renders Master track

**Steps**:
1. Mute Master track in Ableton
2. Export → `output/proof_mute.wav`
3. Measure: `flaas verify-audio output/proof_mute.wav`
4. Expected: Peak ≈ -inf dBFS (silent or near-silent)
5. Unmute Master, re-export, verify normal levels

**If fails**: Export not rendering Master (wrong Rendered Track)

---

### Test 2: Limiter Ceiling Proof

**Purpose**: Verify Limiter is in render path and functioning

**Steps**:
1. Set Limiter Ceiling = -20 dB (extreme, obvious)
2. Export → `output/proof_limiter.wav`
3. Measure: `flaas verify-audio output/proof_limiter.wav`
4. Expected: Peak ≤ -20 dBFS
5. Reset Limiter Ceiling to normal

**If fails**: Limiter bypassed, not last in chain, or not rendering

---

### Test 3: Determinism Test

**Purpose**: Verify identical settings produce identical exports

**Steps**:
1. Export → `output/proof_a.wav`
2. Export again (no changes) → `output/proof_b.wav`
3. Compute SHA256 hashes
4. Expected: Identical hashes

**If fails**: Non-deterministic render (time-based effects, randomization, etc.)

---

## Automation (macOS)

**Implementation**: `src/flaas/ui_export_macos.py`

**Function**: `auto_export_wav(out_path, timeout_s=600)`

**Method**:
1. Delete existing output file (if exists)
2. Bring Ableton Live frontmost
3. Send keystrokes via AppleScript:
   - Cmd+Shift+R (Export shortcut)
   - Return (confirm default render settings)
   - Cmd+Shift+G (Go to folder)
   - Type folder path + Return
   - Type filename + Return
   - Return (confirm overwrite)
4. Wait for file to stabilize (size + mtime stable, 2s checks)
5. Return when complete or timeout

**Requirements**:
- macOS Accessibility permission (Terminal)
- macOS Automation permission (Terminal → System Events)
- Ableton Live running
- Export defaults set correctly (reuses last config)

**Timeout**: 600s (handles complex projects with heavy plugins)

---

## File Stabilization

**Algorithm**:
```python
size_prev = mtime_prev = None
stable_checks = 0

while elapsed < timeout_s:
    if file.exists():
        size_now = file.stat().st_size
        mtime_now = file.stat().st_mtime
        
        if size_now == size_prev and mtime_now == mtime_prev:
            stable_checks += 1
            if stable_checks >= 2:  # Stable for 2 checks (4 seconds)
                return  # Export complete
        else:
            stable_checks = 0
        
        size_prev = size_now
        mtime_prev = mtime_now
    
    sleep(2)

raise TimeoutError("File did not stabilize")
```

**Why both size AND mtime**: Some systems update mtime without changing size (metadata flush)

---

## Failure Modes

**Export hangs**:
- Third-party plugin crash or infinite loop
- Solution: Disable plugins one-by-one, isolate culprit

**Export silent**:
- Master track muted or wrong Rendered Track
- Solution: Run Master Mute proof test

**Peak doesn't match Limiter**:
- Master fader boosted or Limiter bypassed
- Solution: Run Limiter Ceiling proof test

**File never stabilizes**:
- Disk full, permission issue, or export actually hung
- Solution: Check disk space, permissions, kill Ableton if hung

**AppleScript fails**:
- Ableton not running or wrong app frontmost
- Solution: Verify Ableton Live is running, check permissions

---

## SHA256 Fingerprinting

**Purpose**: Detect duplicate exports

**Implementation**:
```python
h = hashlib.sha256()
with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        h.update(chunk)
return h.hexdigest()
```

**Use case**: Skip redundant measurement if hash matches previous

---

## Non-Negotiable Rules

1. **Rendered Track = Master** (always)
2. **Normalize = OFF** (always)
3. **File must stabilize** before measurement (no racing)
4. **Run proof tests** if export behavior seems wrong
5. **Log every export** (path, sha256, timestamp, status)

---

**This export contract is permanent. Export correctness is the foundation of closed-loop optimization.**
