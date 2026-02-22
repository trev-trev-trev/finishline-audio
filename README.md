# FLAAS (Finish Line Audio Automation System)

Deterministic "technical compliance" automation for Ableton Live.

## Quickstart
```bash
make dev
source .venv/bin/activate
```

## Commands

* `flaas --version`
* `flaas ping` — fire-and-forget `/live/test` to AbletonOSC (default 127.0.0.1:11000)
* `flaas scan` — writes `data/caches/model_cache.json` (stub for now)
* `flaas analyze <wav>` — writes `data/reports/analysis.json` (peak dBFS + LUFS-I)
* `flaas check <wav>` — writes `data/reports/check.json` (targets: LUFS -10.5 ±0.5, peak <= -6 dBFS)
* `flaas plan-gain <wav>` — writes `data/actions/actions.json` (Utility gain delta, clamped ±6 dB)
* `flaas apply` — prints actions (dry-run)

## Repo layout

* `src/flaas/` — library + CLI
* `data/` — caches/reports/actions (generated, mostly ignored by git)
* `input/` — local audio inputs (ignored)
* `output/` — renders/exports (ignored)

## Next MVP milestones

* Real AbletonOSC model scan (tracks/devices/params)
* Action apply via OSC + readback
* Iteration loop: export → analyze → plan → apply → re-export → verify
