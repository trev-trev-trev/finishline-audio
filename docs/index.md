# FLAAS Documentation Index

**Quick navigation for Finish Line Audio Automation System documentation.**

---

## Start Here

**For new conversation threads or quick context loading**:

1. **[status/CURRENT.md](status/CURRENT.md)** ⭐⭐⭐ **PRIMARY CHECKPOINT** (≤200 lines, where-we-are-now)
2. **[status/ROADMAP.md](status/ROADMAP.md)** - Next 20 actions (prioritized)
3. **[status/README.md](status/README.md)** - How to use checkpoint system

**For deep understanding**:

1. **[project/operating-manual-v1.md](project/operating-manual-v1.md)** ⭐⭐ **UNIFIED DAILY REFERENCE**
2. **[reference/FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md)** - Current technical state
3. **[workflow/execution-system.md](workflow/execution-system.md)** - Deterministic FSM
4. **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Command reference

---

## By Topic

### Status & Checkpoints
- **[status/CURRENT.md](status/CURRENT.md)** ⭐⭐⭐ **Load this FIRST in new threads**
- **[status/ROADMAP.md](status/ROADMAP.md)** - Next 20 expansions
- **[status/RECEIPTS/](status/RECEIPTS/)** - Validated step history
- **[status/README.md](status/README.md)** - Checkpoint system usage

### Getting Started
- **[../README.md](../README.md)** - Main README (quickstart, installation)
- **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Essential commands

### Understanding the System
- **[project/VISION.md](project/VISION.md)** - Project vision and philosophy
- **[architecture/TECHNICAL_CONSIDERATIONS.md](architecture/TECHNICAL_CONSIDERATIONS.md)** - Design decisions
- **[architecture/IMPLEMENTATION_SPEC.md](architecture/IMPLEMENTATION_SPEC.md)** - Detailed spec

### Development
- **[workflow/protocol.md](workflow/protocol.md)** - Collaboration protocol
- **[workflow/execution-system.md](workflow/execution-system.md)** - Deterministic FSM + stability gates
- **[reference/ENGINEERING_NOTEBOOK.md](reference/ENGINEERING_NOTEBOOK.md)** - Comprehensive API reference
- **[project/mvp_remaining.md](project/mvp_remaining.md)** - What's left to build

### Reference
- **[status/CURRENT.md](status/CURRENT.md)** ⭐ **Primary checkpoint** (use this for quick state)
- **[reference/finishline_context_state.json](reference/finishline_context_state.json)** - Machine-readable state
- **[reference/FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md)** - Step-by-step build history
- **[reference/unique-lines/INDEX.md](reference/unique-lines/INDEX.md)** - Unique line ledger (code transparency)

### Workflow
- **[workflow/execution-system.md](workflow/execution-system.md)** - Deterministic FSM + error taxonomy
- **[workflow/manual_loop.md](workflow/manual_loop.md)** - Current manual iteration workflow
- **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Command quick reference

---

## All Documents

### Status (Checkpoints)
- [CURRENT.md](status/CURRENT.md) ⭐⭐⭐ **PRIMARY** (≤200 lines, load FIRST)
- [ROADMAP.md](status/ROADMAP.md) - Next 20 expansions
- [README.md](status/README.md) - System usage guide
- [RECEIPTS/](status/RECEIPTS/) - Validated steps
- [TEMPLATES/](status/TEMPLATES/) - Receipt + status templates

### Project (Vision & Planning)
- [operating-manual-v1.md](project/operating-manual-v1.md) ⭐⭐ **UNIFIED DAILY REFERENCE**
- [spec-v1.md](project/spec-v1.md) ⭐ **Complete Product & Systems Spec**
- [VISION.md](project/VISION.md)
- [PHILOSOPHY_ALIGNMENT_CHECK.md](project/PHILOSOPHY_ALIGNMENT_CHECK.md)
- [PLAN_SUMMARY.md](project/PLAN_SUMMARY.md)
- [FUTURE_ENHANCEMENTS.md](project/FUTURE_ENHANCEMENTS.md)
- [mvp_remaining.md](project/mvp_remaining.md)

### Architecture (Technical Design)
- [TECHNICAL_CONSIDERATIONS.md](architecture/TECHNICAL_CONSIDERATIONS.md)
- [IMPLEMENTATION_SPEC.md](architecture/IMPLEMENTATION_SPEC.md)
- [MASTER_IMPLEMENTATION_GUIDE.md](architecture/MASTER_IMPLEMENTATION_GUIDE.md)
- [INTEGRATION_COMPLETE.md](architecture/INTEGRATION_COMPLETE.md)

### Workflow (Development Process)
- [protocol.md](workflow/protocol.md) ⭐ **Essential**
- [execution-system.md](workflow/execution-system.md) ⭐ **Essential - Deterministic FSM**
- [terminal-cheatsheet.md](workflow/terminal-cheatsheet.md) ⭐ **Essential**
- [manual_loop.md](workflow/manual_loop.md)

### Reference (Technical State)
- [ENGINEERING_NOTEBOOK.md](reference/ENGINEERING_NOTEBOOK.md) ⭐ **Comprehensive**
- [FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md) ⭐ **Current State**
- [finishline_context_state.json](reference/finishline_context_state.json)
- [unique-lines/INDEX.md](reference/unique-lines/INDEX.md) ⭐ **Code Transparency**

### UI (Future Work)
- [ui-spec-running.md](ui/ui-spec-running.md) - Placeholder (no work until MVP complete)

### Archive (Historical)
- [INDEX.md](archive/INDEX.md) - Archive contents
- [extracted/](archive/extracted/) - Original documentation

### OSC, CLI, Schemas (To Be Created)
- `osc/` - OSC protocol documentation (TBD)
- `cli/` - CLI command deep-dives (TBD)
- `schemas/` - Data format specifications (TBD)

---

## Document Status Legend

- ⭐ **Essential** - Must-read for contributors
- ✅ **Current** - Up-to-date with codebase
- 📝 **Placeholder** - Future work only
- 🗄️ **Archive** - Historical reference

---

## Search Tips

### Find by keyword (terminal)
```bash
cd docs/
grep -r "keyword" . --include="*.md"
```

### Browse by category
```bash
ls docs/workflow/    # Development workflows
ls docs/reference/   # Technical reference
ls docs/project/     # Vision and planning
```

### Quick lookups
- **Command syntax**: `workflow/terminal-cheatsheet.md`
- **Function signature**: `reference/ENGINEERING_NOTEBOOK.md` (Section 2)
- **OSC endpoints**: `reference/ENGINEERING_NOTEBOOK.md` (Section 3)
- **Error taxonomy**: `workflow/execution-system.md` (Section B)
- **Stability gates**: `workflow/execution-system.md` (Section E)

---

**Last updated**: 2026-02-22
