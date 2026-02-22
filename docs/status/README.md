# FLAAS Status Checkpoint System

**Purpose**: Save-game system for reconstructing project state in new conversation threads.

---

## What This Is

The status checkpoint system captures:
1. **Current state** - Where we are now (CURRENT.md)
2. **Validated wins** - What works and how we know (RECEIPTS/)
3. **Next actions** - Exact command to run next (CURRENT.md Section 7)
4. **Roadmap** - Prioritized remaining work (ROADMAP.md)

**Design principle**: Terminal-first, minimal bloat, reproducible.

---

## How to Use

### Starting a New Session

1. Read **[CURRENT.md](CURRENT.md)** (≤200 lines, primary reference)
2. Run environment checklist (Section 3)
3. Check gate status (Section 4)
4. Execute "next single action" (Section 7)
5. If success: Create receipt → Update CURRENT.md → Commit
6. If failure: Run probe (Section 8) → Diagnose → Fix → Update

### After Completing a Task

1. **Create receipt** using [TEMPLATES/receipt_template.md](TEMPLATES/receipt_template.md)
   - Filename: `YYYY-MM-DD_HHMM_<slug>.md`
   - Keep under ~150 lines
   - Include exact commands + outputs
2. **Update CURRENT.md**:
   - Section 6: Add new capability
   - Section 7: Update "next single action"
   - Section 5: Update fingerprint if scan ran
3. **Commit changes**:
   ```bash
   git add docs/status/
   git commit -m "docs: update status after [task]"
   ```

### Receipt Rules

**Every successful tested addition gets ONE receipt.**

**Receipt must be**:
- ✅ Short (≤150 lines)
- ✅ Terminal-first (commands + outputs)
- ✅ Reproducible (exact commands to recreate)
- ✅ Timestamped (filename has date+time)

**Receipt must NOT be**:
- ❌ Speculative (only validated facts)
- ❌ Verbose (no essay text)
- ❌ Missing rollback (always include undo steps)

---

## File Structure

```
docs/status/
├── README.md              # This file (how to use system)
├── CURRENT.md             # Primary checkpoint (≤200 lines) ⭐
├── ROADMAP.md             # Next 20 expansions (tight)
├── RECEIPTS/              # Validated step receipts
│   ├── 2026-02-22_0354_inspect_selected_device.md
│   ├── 2026-02-22_0330_gate_g1_verified.md
│   └── ...
├── SNAPSHOTS/             # Optional structured dumps
│   ├── model_cache_2026-02-22.json
│   └── ...
└── TEMPLATES/
    ├── receipt_template.md
    └── current_template.md
```

---

## Update Rules

### Rule 1: Update CURRENT.md After Every Validated Task
**Trigger**: Receipt created (task completed and tested).

**Changes**:
- Section 6: Add new capability to "verified capabilities" list
- Section 7: Update "next single action" (use ROADMAP.md)
- Section 5: Update fingerprint/timestamp if scan ran
- Section 4: Update gate status if gate ran

**Validation**: CURRENT.md stays ≤200 lines (archive old items to receipts if needed).

---

### Rule 2: Create Receipt for Every Successful Task
**Trigger**: Task completes, terminal validation passes.

**Process**:
1. Copy `TEMPLATES/receipt_template.md`
2. Fill in all sections (use actual terminal outputs)
3. Name: `YYYY-MM-DD_HHMM_<slug>.md` (slug = 2-4 word task summary)
4. Save to `RECEIPTS/`
5. Link from CURRENT.md Section 9

**Validation**: Receipt is standalone (someone can reproduce task from receipt alone).

---

### Rule 3: Update ROADMAP.md When Priorities Change
**Trigger**: 
- Major blocker resolved
- New high-leverage expansion discovered
- Milestone definition changes

**Changes**:
- Reprioritize next 20 expansions
- Mark completed items
- Add new discoveries

**Validation**: ROADMAP.md top item matches CURRENT.md "next single action".

---

### Rule 4: Snapshot Optional (Not Every Time)
**Trigger**: Useful state to preserve (not captured in receipts).

**Examples**:
- Large model_cache.json excerpt (track structure)
- Endpoint registry table (validated endpoints)
- Parameter mapping table (device-specific ranges)

**Usage**: Reference from receipt (`See SNAPSHOTS/[file]`).

---

## Quick Commands

### Check Current Status
```bash
cat docs/status/CURRENT.md
```

### List Recent Receipts
```bash
ls -lt docs/status/RECEIPTS/ | head -5
```

### Validate Environment (from CURRENT.md Section 3)
```bash
cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate
flaas --version
flaas ping --wait
```

### Create New Receipt
```bash
cp docs/status/TEMPLATES/receipt_template.md docs/status/RECEIPTS/$(date +%Y-%m-%d_%H%M)_task_slug.md
# Edit file, fill in all sections
git add docs/status/
git commit -m "docs: add receipt for [task]"
```

---

## Integration with Existing Docs

**Status system complements** (does not replace):
- **operating-manual-v1.md** - Unified reference (comprehensive)
- **execution-system.md** - FSM + gates (algorithmic)
- **terminal-cheatsheet.md** - Command reference (lookup)
- **ENGINEERING_NOTEBOOK.md** - API catalog (deep detail)

**Status system provides**:
- **CURRENT.md** - Immediate "where are we now" (snapshot)
- **RECEIPTS/** - Validated step history (audit trail)
- **ROADMAP.md** - Prioritized next actions (planning)

**When to use what**:
- New thread → Read CURRENT.md first
- Need command syntax → terminal-cheatsheet.md
- Need function details → ENGINEERING_NOTEBOOK.md
- Need algorithm → execution-system.md
- Need full context → operating-manual-v1.md

---

## Maintenance

**Weekly** (or after 10+ receipts):
- Archive old receipts to `RECEIPTS/archive/YYYY-MM/`
- Keep only last 10 in RECEIPTS/ root
- Update CURRENT.md links to point to archived receipts

**After major milestone**:
- Create snapshot of CURRENT.md → `SNAPSHOTS/CURRENT_vX.Y.Z.md`
- Reset Section 6 (keep only last 5 capabilities)
- Update Section 2 (new milestone)

---

**Last updated**: 2026-02-22
