# FLAAS Documentation Index

**Quick navigation for Finish Line Audio Automation System documentation.**

---

## Start Here

New to the project? Read these in order:

1. **[docs/README.md](README.md)** - Documentation overview and navigation
2. **[reference/FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md)** - Current technical state
3. **[workflow/protocol.md](workflow/protocol.md)** - How this project was built (one-task loop)
4. **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Command reference

---

## By Topic

### Getting Started
- **[../README.md](../README.md)** - Main README (quickstart, installation)
- **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Essential commands

### Understanding the System
- **[project/VISION.md](project/VISION.md)** - Project vision and philosophy
- **[architecture/TECHNICAL_CONSIDERATIONS.md](architecture/TECHNICAL_CONSIDERATIONS.md)** - Design decisions
- **[architecture/IMPLEMENTATION_SPEC.md](architecture/IMPLEMENTATION_SPEC.md)** - Detailed spec

### Development
- **[workflow/protocol.md](workflow/protocol.md)** - Collaboration protocol
- **[reference/ENGINEERING_NOTEBOOK.md](reference/ENGINEERING_NOTEBOOK.md)** - Comprehensive API reference
- **[project/mvp_remaining.md](project/mvp_remaining.md)** - What's left to build

### Reference
- **[reference/finishline_context_state.json](reference/finishline_context_state.json)** - Machine-readable state
- **[reference/FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md)** - Step-by-step build history
- **[reference/unique-lines/INDEX.md](reference/unique-lines/INDEX.md)** - Unique line ledger (code transparency)

### Workflow
- **[workflow/manual_loop.md](workflow/manual_loop.md)** - Current manual iteration workflow
- **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Command quick reference

---

## All Documents

### Project (Vision & Planning)
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
- **Error taxonomy**: `workflow/protocol.md` (Error Taxonomy section)

---

**Last updated**: 2026-02-22
