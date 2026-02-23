# Finishline Audio MVP — Progress Index + Technical State
Generated: 2026-02-22T08:58:00Z

Repo: https://github.com/trev-trev-trev/finishline-audio
Package: flaas v0.0.2

## Current capabilities (tight)
- OSC ping roundtrip (`/live/test`) working (11000/11001)
- Scan: tracks/devices + fingerprint
- Control: Utility Gain set/readback on track 0 device 0 (param_id=9)
- Analyze: peak dBFS + LUFS-I on WAV
- Plan: bounded Utility Gain *delta* from LUFS error
- Apply: fingerprint-enforced relative delta
- Verify: read back Utility gain
- Loop: analyze → plan → apply (+ dry + max stop)
- Manual export loop documented (export → verify-audio → loop → repeat)

## Process used (operator loop)
1) Cursor agent writes code changes
2) Terminal validates (commands + OSC reads)
3) Paste output back into ChatGPT
4) Next one-step command

## Technical manual

### Ports
- AbletonOSC listen: UDP 11000
- AbletonOSC reply: UDP 11001

### Required Ableton config
- AbletonOSC installed in:
  `~/Music/Ableton/User Library/Remote Scripts/AbletonOSC`
- Ableton Preferences → Link/Tempo/MIDI → Control Surface:
  - Slot 1: AbletonOSC / None / None

### Endpoints used
- Health: `/live/test "ok"` → reply `("ok",)`
- Scan:
  - `/live/song/get/num_tracks`
  - `/live/song/get/track_names`
  - `/live/track/get/num_devices`
  - `/live/track/get/devices/name`
  - `/live/track/get/devices/class_name`
- Device params:
  - `/live/device/get/parameters/name`
  - `/live/device/get/parameters/min`
  - `/live/device/get/parameters/max`
  - `/live/device/get/parameter/value`
  - `/live/device/set/parameter/value`

### Key constants / assumptions
- Target track/device: track_id=0, device_id=0
- Utility class: `StereoGain`
- Utility Gain param id: `UTILITY_GAIN_PARAM_ID = 9`
- Parameter values are normalized 0..1
- Utility “linear” range derived from min/max (often -1..+1):
  - `linear = min + norm*(max-min)`
  - `norm = (clamp(linear,min,max) - min)/(max-min)`

### Planning model
- LUFS error (dB) = target_lufs - measured_lufs
- Raw delta_linear ≈ error/12
- Clamp delta_linear to ±0.25

### Safety
- actions.json includes `live_fingerprint`
- apply refuses if fingerprint mismatch
- loop stops if Utility norm ≥ 0.99

### Commands
- `flaas ping [--wait]`
- `flaas scan`
- `flaas analyze <wav>`
- `flaas check <wav>`
- `flaas plan-gain <wav>`
- `flaas apply [--dry]`
- `flaas verify`
- `flaas reset`
- `flaas util-gain-norm <track> <device> <0..1>`
- `flaas util-gain-linear <track> <device> <linear>`
- `flaas loop <wav> [--dry]`
- `flaas export-guide`
- `flaas verify-audio <wav>`

## Completed steps (receipt index)
- Step 00: **Git/GitHub bridge established** — HTTPS auth failed; switched to SSH; push to main working.
- Step 01: **Repo initialized + first pushes** — Remote set; commits pushed to origin/main.
- Step 02: **Create repo structure folders** — data/{caches,reports,actions,timelines,profiles} + input/output + tests created.
- Step 03: **Add .gitkeep placeholders + push** — Folders tracked cleanly.
- Step 04: **Set git identity** — user.name=Trevor Reynolds; user.email set.
- Step 05: **Add .gitignore** — Ignore OS/editor, python env, audio, generated json, logs.
- Step 06: **Python package skeleton (src layout)** — pyproject.toml + src/flaas + CLI entrypoint created.
- Step 07: **Create venv + install editable** — python3 -m venv .venv; pip install -e .; flaas --version works.
- Step 08: **OSC ping (fire-and-forget)** — flaas ping sends /live/test.
- Step 09: **Ignore build artifacts** — *.egg-info removed from git and ignored.
- Step 10: **Scan stub writes model_cache.json** — flaas scan creates data/caches/model_cache.json.
- Step 11: **Validate scan stub output** — cat data/caches/model_cache.json shows stub payload.
- Step 12: **WAV analyzer added** — peak dBFS + LUFS-I to data/reports/analysis.json.
- Step 13: **Validate analyzer** — Generated sine WAV; analysis produced expected peak/LUFS values.
- Step 14: **Compliance targets + check command** — flaas check writes data/reports/check.json (pass/fail flags).
- Step 15: **Ignore generated report JSON** — data/reports/*.json ignored; removed tracked analysis.json.
- Step 16: **Validate check output** — flaas check input/test.wav shows LUFS fail, peak pass.
- Step 17: **Plan actions (plan-gain)** — Generate data/actions/actions.json from analysis.
- Step 18: **Validate planned actions file** — cat data/actions/actions.json shows planned Utility.Gain action.
- Step 19: **Apply dry-run** — flaas apply prints DRY_RUN action lines.
- Step 20: **Makefile dev target** — make dev sets up venv + editable install.
- Step 21: **README quickstart** — README.md added with commands/structure.
- Step 22: **OSC request/response (RPC) ping** — Added listener on 11001; request_once() added.
- Step 23: **Install AbletonOSC remote script** — Cloned AbletonOSC into User Library Remote Scripts; loaded in Live.
- Step 24: **Fix /live/test argument** — Ping now sends 'ok' and expects ('ok',) reply.
- Step 25: **Real OSC connectivity verified** — flaas ping --wait returns ok: ('ok',).
- Step 26: **Readback + getters exploration** — Moved to supported /live/song/get and /live/track/get endpoints.
- Step 27: **Real scan implemented** — scan_live() queries tracks/devices and fingerprints set.
- Step 28: **Utility device detection** — Track 0 device 0 shows Utility class StereoGain.
- Step 29: **Utility Gain param id discovered** — parameters/name shows Gain is param_id=9 (in names[2:]).
- Step 30: **Normalized parameter semantics** — Confirmed parameter/value uses 0..1; device min/max returned -1..1 for Utility Gain.
- Step 31: **Linear mapping utilities** — Added util-gain-norm and util-gain-linear; mapping via min/max to norm.
- Step 32: **Apply uses device param mapping** — apply writes Utility Gain param via /live/device/set/parameter/value.
- Step 33: **Loop + verify + reset** — loop (analyze→plan→apply), verify readback, reset center.
- Step 34: **Actions schema + fingerprint** — actions.json includes schema_version + live_fingerprint; apply enforces.
- Step 35: **Plan/apply stability** — apply is relative delta; plan emits bounded deltas (±0.25) and loop stops near max.
- Step 36: **Version bump + docs** — bumped to 0.0.2; added remaining MVP blocks + manual loop docs.
- Step 37: **Export guide + verify-audio** — export-guide prints settings; verify-audio prints PASS/FAIL and exit code.

## Handoff: how to continue in a new chat
- This file is the authoritative snapshot of:
  - current code behaviors
  - key constants and endpoints
  - step receipts (what was done)
- Next work should start from docs/mvp_remaining.md block (1): automate export/re-render.
