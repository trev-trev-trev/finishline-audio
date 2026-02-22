# Remaining MVP blocks

## 1) Export loop (manual -> automated)
- Add `flaas export` placeholder command (documents exact Ableton export settings)
- Later: drive export via AbletonOSC `/live/song/export/*` endpoints (if supported) or use a deterministic manual-export checklist + verifier.

## 2) Multi-stem support
- Define stem naming contract + validate files
- Analyze per-stem peak/headroom + basic band energy metrics
- Generate per-stem actions (Utility on stem groups)

## 3) True-peak estimate
- Oversampling true-peak estimator (offline)
- Add true-peak target and limiter ceiling policy (still via Ableton devices)

## 4) Device mapping beyond Utility
- Find device indices + parameter ids via scan
- Apply to: EQ Eight cuts, limiter ceiling, mono-bass policy (as allowed)

## 5) Verification + iteration cap
- `flaas verify-audio` compares before/after against targets
- Stop conditions: pass, clamped, or unfixable
- Max 2 iterations

## 6) Hardening
- Unit tests for analysis/plan/apply mapping
- Replay logs + artifacts per run
- Better error messages for missing AbletonOSC, wrong track, missing Utility, etc.
