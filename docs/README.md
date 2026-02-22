# FLAAS Documentation

**Finish Line Audio Automation System - Engineering Documentation**

## Directory Map

```
docs/
├── README.md (this file)
├── project/         - Vision, philosophy, planning docs
├── architecture/    - Technical specs, implementation guides
├── osc/            - OSC protocol specs and endpoint docs (TBD)
├── cli/            - CLI command reference (TBD)
├── schemas/        - Data artifact schemas (TBD)
├── workflow/       - Development workflows and protocols
├── ui/             - UI specifications (placeholder)
├── reference/      - State snapshots, progress index, engineering notebook
└── archive/        - Extracted original documentation
```

## How to Use These Docs (Terminal-First)

### Quick Start
```bash
# Environment setup
make dev
source .venv/bin/activate

# Validate wiring
flaas --help
flaas ping --wait
flaas scan
```

### Core References (Read in Order)
1. **[reference/FINISHLINE_PROGRESS_INDEX.md](reference/FINISHLINE_PROGRESS_INDEX.md)** - Technical state snapshot + step receipts
2. **[workflow/protocol.md](workflow/protocol.md)** - One-task terminal loop collaboration protocol
3. **[workflow/execution-system.md](workflow/execution-system.md)** ⭐ **Deterministic FSM + stability gates**
4. **[workflow/terminal-cheatsheet.md](workflow/terminal-cheatsheet.md)** - Command quick reference + troubleshooting
5. **[workflow/manual_loop.md](workflow/manual_loop.md)** - Current manual iteration workflow
6. **[reference/ENGINEERING_NOTEBOOK.md](reference/ENGINEERING_NOTEBOOK.md)** - Comprehensive API/function catalog
7. **[reference/unique-lines/INDEX.md](reference/unique-lines/INDEX.md)** - Unique line ledger (complete code transparency)

### For New Contributors
1. Read `reference/FINISHLINE_PROGRESS_INDEX.md` for current state
2. Read `workflow/protocol.md` to understand the development process
3. Use `workflow/terminal-cheatsheet.md` for daily commands
4. Reference `reference/ENGINEERING_NOTEBOOK.md` for implementation details

### For Understanding the System
- **Product spec**: `project/spec-v1.md` ⭐ **Complete vision + build strategy**
- **Project vision**: `project/VISION.md`
- **Architecture**: `architecture/TECHNICAL_CONSIDERATIONS.md`
- **Implementation**: `architecture/IMPLEMENTATION_SPEC.md`
- **What's left**: `project/mvp_remaining.md`

## Key Principles

**Terminal-driven development**: Every change validated by command-line output.

**One atomic task per iteration**: Plan → Edit → Run → Observe → Commit.

**Paste-driven debugging**: Actual terminal output is the source of truth.

**No speculation**: If information can't be proven from repo sources, it's marked "VERIFY".
