# FLAAS (Finish Line Audio Automation System)

Deterministic "technical compliance" automation for Ableton Live.

## Quickstart
```bash
make dev
source .venv/bin/activate
```

## Commands

* `flaas --version`
* `flaas ping` — `/live/test` to AbletonOSC (use `--wait` for reply)
* `flaas scan` — writes `data/caches/model_cache.json` (tracks+devices)
* `flaas analyze <wav>` — writes `data/reports/analysis.json` (peak dBFS + LUFS-I)
* `flaas check <wav>` — writes `data/reports/check.json`
* `flaas plan-gain <wav>` — writes `data/actions/actions.json` (Utility gain *linear delta*, clamped)
* `flaas apply` — applies actions via OSC (fingerprint enforced)
* `flaas verify` — reads back Utility gain (normalized)
* `flaas reset` — sets Utility gain to center
* `flaas util-gain-linear <track> <device> <val>` — set Utility gain in exposed linear range (ex: -1..+1)
* `flaas util-gain-norm <track> <device> <val>` — set Utility gain normalized 0..1
* `flaas loop <wav>` — analyze → plan → apply
* `flaas loop <wav> --dry` — preview only

## Documentation

**All documentation has been reorganized** into `docs/`. Start here:

- **[docs/project/spec-v1.md](docs/project/spec-v1.md)** - Product & systems architecture specification ⭐
- **[docs/README.md](docs/README.md)** - Documentation overview and navigation
- **[docs/workflow/protocol.md](docs/workflow/protocol.md)** - How this project was built (one-task terminal loop)
- **[docs/workflow/terminal-cheatsheet.md](docs/workflow/terminal-cheatsheet.md)** - Command reference and troubleshooting
- **[docs/reference/ENGINEERING_NOTEBOOK.md](docs/reference/ENGINEERING_NOTEBOOK.md)** - Comprehensive API reference
- **[docs/project/mvp_remaining.md](docs/project/mvp_remaining.md)** - What's left to build

## Repo layout

* `src/flaas/` — library + CLI
* `docs/` — all documentation (workflow, reference, architecture, project planning)
* `data/` — caches/reports/actions (generated, mostly ignored by git)
* `input/` — local audio inputs (ignored)
* `output/` — renders/exports (ignored)

## Note on Utility Gain
Utility "Gain" via AbletonOSC device parameters is exposed as a normalized control (often with min=-1, max=1). Current MVP treats gain actions as *linear* values mapped into normalized 0..1.
