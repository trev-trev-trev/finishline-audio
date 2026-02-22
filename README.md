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

## Repo layout

* `src/flaas/` — library + CLI
* `data/` — caches/reports/actions (generated, mostly ignored by git)
* `input/` — local audio inputs (ignored)
* `output/` — renders/exports (ignored)

## Note on Utility Gain
Utility “Gain” via AbletonOSC device parameters is exposed as a normalized control (often with min=-1, max=1). Current MVP treats gain actions as *linear* values mapped into normalized 0..1.

## Next MVP milestones

* Real AbletonOSC model scan (tracks/devices/params)
* Action apply via OSC + readback
* Iteration loop: export → analyze → plan → apply → re-export → verify
