# Unique Lines: Cli Wiring

**Total unique lines**: 52

---

## Line: `analyze = sub.add_parser("analyze", help="Analyze a WAV and write analysis.json")`

**Occurrences**: 1

- `src/flaas/cli.py:33`

## Line: `analyze.add_argument("--out", default="data/reports/analysis.json")`

**Occurrences**: 1

- `src/flaas/cli.py:35`

## Line: `analyze.add_argument("wav")`

**Occurrences**: 1

- `src/flaas/cli.py:34`

## Line: `ap = sub.add_parser("apply", help="Apply actions")`

**Occurrences**: 1

- `src/flaas/cli.py:45`

## Line: `ap.add_argument("--actions", default="data/actions/actions.json")`

**Occurrences**: 1

- `src/flaas/cli.py:46`

## Line: `ap.add_argument("--dry", action="store_true")`

**Occurrences**: 1

- `src/flaas/cli.py:47`

## Line: `ap.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:48`

## Line: `ap.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:49`

## Line: `args = p.parse_args()`

**Occurrences**: 1

- `src/flaas/cli.py:84`

## Line: `check = sub.add_parser("check", help="Check WAV against compliance targets")`

**Occurrences**: 1

- `src/flaas/cli.py:37`

## Line: `check.add_argument("--out", default="data/reports/check.json")`

**Occurrences**: 1

- `src/flaas/cli.py:39`

## Line: `check.add_argument("wav")`

**Occurrences**: 1

- `src/flaas/cli.py:38`

## Line: `eg = sub.add_parser("export-guide", help="Print Ableton export settings (manual MVP)")`

**Occurrences**: 1

- `src/flaas/cli.py:79`

## Line: `lp = sub.add_parser("loop", help="analyze -> plan-gain -> apply (manual export/verify)")`

**Occurrences**: 1

- `src/flaas/cli.py:65`

## Line: `lp.add_argument("--dry", action="store_true")`

**Occurrences**: 1

- `src/flaas/cli.py:67`

## Line: `lp.add_argument("wav")`

**Occurrences**: 1

- `src/flaas/cli.py:66`

## Line: `p = argparse.ArgumentParser(prog="flaas")`

**Occurrences**: 1

- `src/flaas/cli.py:17`

## Line: `p.add_argument("--version", action="store_true")`

**Occurrences**: 1

- `src/flaas/cli.py:20`

## Line: `pg = sub.add_parser("plan-gain", help="Plan Utility gain action to hit LUFS target (writes actions.json)")`

**Occurrences**: 1

- `src/flaas/cli.py:41`

## Line: `pg.add_argument("--out", default="data/actions/actions.json")`

**Occurrences**: 1

- `src/flaas/cli.py:43`

## Line: `pg.add_argument("wav")`

**Occurrences**: 1

- `src/flaas/cli.py:42`

## Line: `ping = sub.add_parser("ping", help="Ping AbletonOSC via /live/test")`

**Occurrences**: 1

- `src/flaas/cli.py:22`

## Line: `ping.add_argument("--arg", default="ok", help="Argument sent to /live/test (default: ok)")`

**Occurrences**: 1

- `src/flaas/cli.py:28`

## Line: `ping.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:23`

## Line: `ping.add_argument("--listen-port", type=int, default=11001)`

**Occurrences**: 1

- `src/flaas/cli.py:26`

## Line: `ping.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:24`

## Line: `ping.add_argument("--timeout", type=float, default=2.0)`

**Occurrences**: 1

- `src/flaas/cli.py:27`

## Line: `ping.add_argument("--wait", action="store_true", help="Wait for /live/test reply on 11001")`

**Occurrences**: 1

- `src/flaas/cli.py:25`

## Line: `rs = sub.add_parser("reset", help="Reset master Utility gain to center")`

**Occurrences**: 1

- `src/flaas/cli.py:75`

## Line: `rs.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:76`

## Line: `rs.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:77`

## Line: `scan = sub.add_parser("scan", help="Write model_cache.json (stub for now)")`

**Occurrences**: 1

- `src/flaas/cli.py:30`

## Line: `scan.add_argument("--out", default="data/caches/model_cache.json")`

**Occurrences**: 1

- `src/flaas/cli.py:31`

## Line: `ugl = sub.add_parser("util-gain-linear", help="Set Utility Gain in exposed linear range (ex: -1..+1)")`

**Occurrences**: 1

- `src/flaas/cli.py:58`

## Line: `ugl.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:62`

## Line: `ugl.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:63`

## Line: `ugl.add_argument("device_id", type=int)`

**Occurrences**: 1

- `src/flaas/cli.py:60`

## Line: `ugl.add_argument("gain_linear", type=float)`

**Occurrences**: 1

- `src/flaas/cli.py:61`

## Line: `ugl.add_argument("track_id", type=int)`

**Occurrences**: 1

- `src/flaas/cli.py:59`

## Line: `ugn = sub.add_parser("util-gain-norm", help="Set Utility Gain normalized 0..1")`

**Occurrences**: 1

- `src/flaas/cli.py:51`

## Line: `ugn.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:55`

## Line: `ugn.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:56`

## Line: `ugn.add_argument("device_id", type=int)`

**Occurrences**: 1

- `src/flaas/cli.py:53`

## Line: `ugn.add_argument("gain_norm", type=float)`

**Occurrences**: 1

- `src/flaas/cli.py:54`

## Line: `ugn.add_argument("track_id", type=int)`

**Occurrences**: 1

- `src/flaas/cli.py:52`

## Line: `va = sub.add_parser("verify-audio", help="Analyze+check a WAV and print PASS/FAIL")`

**Occurrences**: 1

- `src/flaas/cli.py:81`

## Line: `va.add_argument("wav")`

**Occurrences**: 1

- `src/flaas/cli.py:82`

## Line: `vf = sub.add_parser("verify", help="Read back master Utility gain normalized")`

**Occurrences**: 1

- `src/flaas/cli.py:69`

## Line: `vf.add_argument("--device-id", type=int, default=0)`

**Occurrences**: 1

- `src/flaas/cli.py:71`

## Line: `vf.add_argument("--host", default="127.0.0.1")`

**Occurrences**: 1

- `src/flaas/cli.py:72`

## Line: `vf.add_argument("--port", type=int, default=11000)`

**Occurrences**: 1

- `src/flaas/cli.py:73`

## Line: `vf.add_argument("--track-id", type=int, default=0)`

**Occurrences**: 1

- `src/flaas/cli.py:70`

