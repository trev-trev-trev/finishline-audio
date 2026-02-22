# Unique Lines: Logic

**Total unique lines**: 278

---

## Line: `"""`

**Occurrences**: 8

- `src/flaas/apply.py`: lines 46, 49
- `src/flaas/osc_rpc.py`: lines 23, 25
- `src/flaas/plan.py`: lines 34, 37
- `src/flaas/util.py`: lines 14, 17

## Line: `"/live/test",`

**Occurrences**: 1

- `src/flaas/cli.py:94`

## Line: `)`

**Occurrences**: 11

- `src/flaas/actions.py:35`
- `src/flaas/analyze.py:44`
- `src/flaas/apply.py`: lines 32-33
- `src/flaas/audio_io.py:22`
- `src/flaas/check.py:30`
- `src/flaas/cli.py:98`
- `src/flaas/plan.py`: lines 54, 64
- `src/flaas/scan.py`: lines 71, 87

## Line: `) -> None:`

**Occurrences**: 1

- `src/flaas/apply.py:45`

## Line: `) -> Path:`

**Occurrences**: 1

- `src/flaas/actions.py:27`

## Line: `) -> PlanGainResult:`

**Occurrences**: 1

- `src/flaas/plan.py:33`

## Line: `) -> tuple[Any, ...]:`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:22`

## Line: `Assumes track 0 device 0 is Utility.`

**Occurrences**: 1

- `src/flaas/apply.py:48`

## Line: `Compute LUFS error and convert to a SMALL delta (bounded) to avoid runaway stacking.`

**Occurrences**: 1

- `src/flaas/plan.py:35`

## Line: `GainAction(`

**Occurrences**: 1

- `src/flaas/plan.py:59`

## Line: `LoadedAction(`

**Occurrences**: 1

- `src/flaas/apply.py:27`

## Line: `MVP apply: supports MASTER Utility Gain as a RELATIVE delta.`

**Occurrences**: 1

- `src/flaas/apply.py:47`

## Line: `RpcTarget(host=args.host, port=args.port),`

**Occurrences**: 1

- `src/flaas/cli.py:93`

## Line: `Send one OSC message, wait for one reply on `listen_port`, then return reply args.`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:24`

## Line: `Utility gain exposed via AbletonOSC appears as linear-ish range (often -1..+1).`

**Occurrences**: 1

- `src/flaas/util.py:15`

## Line: `We map it into normalized 0..1 using min/max from /parameters/min|max.`

**Occurrences**: 1

- `src/flaas/util.py:16`

## Line: `]`

**Occurrences**: 1

- `src/flaas/plan.py:65`

## Line: `_, actions = _read_actions_file(path)`

**Occurrences**: 1

- `src/flaas/apply.py:37`

## Line: `__all__ = ["__version__"]`

**Occurrences**: 1

- `src/flaas/__init__.py:1`

## Line: `__version__ = "0.0.2"`

**Occurrences**: 1

- `src/flaas/__init__.py:2`

## Line: `actions = [`

**Occurrences**: 1

- `src/flaas/plan.py:58`

## Line: `actions.append(`

**Occurrences**: 1

- `src/flaas/apply.py:26`

## Line: `actions: list[GainAction]`

**Occurrences**: 1

- `src/flaas/actions.py:20`

## Line: `actions: list[GainAction],`

**Occurrences**: 1

- `src/flaas/actions.py:23`

## Line: `actions: list[LoadedAction] = []`

**Occurrences**: 1

- `src/flaas/apply.py:24`

## Line: `actions=actions,`

**Occurrences**: 1

- `src/flaas/actions.py:34`

## Line: `actions_path: str | Path = "data/actions/actions.json",`

**Occurrences**: 1

- `src/flaas/apply.py:42`

## Line: `address: str,`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:18`

## Line: `apply_actions_dry_run()`

**Occurrences**: 1

- `src/flaas/loop.py:20`

## Line: `apply_actions_dry_run(args.actions)`

**Occurrences**: 1

- `src/flaas/cli.py:127`

## Line: `apply_actions_osc()`

**Occurrences**: 1

- `src/flaas/loop.py:24`

## Line: `apply_actions_osc(args.actions, target=RpcTarget(host=args.host, port=args.port))`

**Occurrences**: 1

- `src/flaas/cli.py:129`

## Line: `args = q.get(timeout=timeout_sec)`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:43`

## Line: `args.arg,`

**Occurrences**: 1

- `src/flaas/cli.py:95`

## Line: `channels: int`

**Occurrences**: 2

- `src/flaas/analyze.py:15`
- `src/flaas/audio_io.py:11`

## Line: `channels=info.channels,`

**Occurrences**: 1

- `src/flaas/analyze.py:38`

## Line: `channels=int(info.channels),`

**Occurrences**: 1

- `src/flaas/audio_io.py:20`

## Line: `class_name: str`

**Occurrences**: 1

- `src/flaas/scan.py:14`

## Line: `client = SimpleUDPClient(target.host, target.port)`

**Occurrences**: 4

- `src/flaas/apply.py:57`
- `src/flaas/osc.py:12`
- `src/flaas/osc_rpc.py:39`
- `src/flaas/util.py:10`

## Line: `created_at_utc: str`

**Occurrences**: 3

- `src/flaas/actions.py:18`
- `src/flaas/analyze.py:20`
- `src/flaas/scan.py:27`

## Line: `created_at_utc=datetime.now(timezone.utc).isoformat(),`

**Occurrences**: 4

- `src/flaas/actions.py:32`
- `src/flaas/analyze.py:43`
- `src/flaas/scan.py`: lines 67, 83

## Line: `cur_linear = _get_current_utility_linear(target=target_osc)`

**Occurrences**: 1

- `src/flaas/plan.py:47`

## Line: `cur_linear = pr.min + cur_norm * (pr.max - pr.min)`

**Occurrences**: 1

- `src/flaas/apply.py:64`

## Line: `cur_linear: float`

**Occurrences**: 1

- `src/flaas/plan.py:20`

## Line: `cur_linear=float(cur_linear),`

**Occurrences**: 1

- `src/flaas/plan.py:53`

## Line: `cur_norm = float(cur[3])`

**Occurrences**: 2

- `src/flaas/apply.py:63`
- `src/flaas/plan.py:25`

## Line: `cur_norm = verify_master_utility_gain()`

**Occurrences**: 1

- `src/flaas/loop.py:10`

## Line: `current_fp = scan_live(target=target).fingerprint`

**Occurrences**: 1

- `src/flaas/apply.py:53`

## Line: `delta = raw`

**Occurrences**: 1

- `src/flaas/plan.py:41`

## Line: `delta_db: float`

**Occurrences**: 1

- `src/flaas/actions.py:13`

## Line: `delta_db: float  # "linear delta" for Utility Gain (-1..+1)`

**Occurrences**: 1

- `src/flaas/apply.py:16`

## Line: `delta_db=float(a["delta_db"]),`

**Occurrences**: 1

- `src/flaas/apply.py:31`

## Line: `delta_db=r.delta_linear,`

**Occurrences**: 1

- `src/flaas/plan.py:63`

## Line: `delta_linear: float`

**Occurrences**: 1

- `src/flaas/plan.py:16`

## Line: `delta_linear=float(delta),`

**Occurrences**: 1

- `src/flaas/plan.py:49`

## Line: `dev_class = list(dc[1:]) if len(dc) > 1 else []`

**Occurrences**: 1

- `src/flaas/scan.py:53`

## Line: `dev_names = list(dn[1:]) if len(dn) > 1 else []`

**Occurrences**: 1

- `src/flaas/scan.py:52`

## Line: `device: str`

**Occurrences**: 2

- `src/flaas/actions.py:11`
- `src/flaas/apply.py:14`

## Line: `device="Utility",`

**Occurrences**: 1

- `src/flaas/plan.py:61`

## Line: `device=a["device"],`

**Occurrences**: 1

- `src/flaas/apply.py:29`

## Line: `devices.append(DeviceInfo(index=i, name=str(dev_names[i]), class_name=str(dev_class[i])))`

**Occurrences**: 1

- `src/flaas/scan.py:57`

## Line: `devices: list[DeviceInfo]`

**Occurrences**: 1

- `src/flaas/scan.py:21`

## Line: `devices: list[DeviceInfo] = []`

**Occurrences**: 1

- `src/flaas/scan.py:55`

## Line: `disp = Dispatcher()`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:28`

## Line: `disp.map(address, _handler)`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:33`

## Line: `dur = info.samples / info.sr`

**Occurrences**: 1

- `src/flaas/analyze.py:34`

## Line: `duration_sec: float`

**Occurrences**: 1

- `src/flaas/analyze.py:17`

## Line: `duration_sec=float(dur),`

**Occurrences**: 1

- `src/flaas/analyze.py:40`

## Line: `else:`

**Occurrences**: 3

- `src/flaas/apply.py:71`
- `src/flaas/cli.py`: lines 100, 128

## Line: `enforce_fingerprint: bool = True,`

**Occurrences**: 1

- `src/flaas/apply.py:44`

## Line: `err_db = targets.master_lufs - a.lufs_i`

**Occurrences**: 1

- `src/flaas/plan.py:39`

## Line: `except Exception as e:`

**Occurrences**: 1

- `src/flaas/scan.py:79`

## Line: `except queue.Empty as e:`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:44`

## Line: `expected_fp, actions = _read_actions_file(actions_path)`

**Occurrences**: 1

- `src/flaas/apply.py:50`

## Line: `file: str`

**Occurrences**: 2

- `src/flaas/analyze.py:13`
- `src/flaas/check.py:10`

## Line: `file=a.file,`

**Occurrences**: 1

- `src/flaas/check.py:23`

## Line: `file=info.path,`

**Occurrences**: 1

- `src/flaas/analyze.py:36`

## Line: `fingerprint = _sha256(";".join(fp_parts))`

**Occurrences**: 1

- `src/flaas/scan.py:62`

## Line: `fingerprint: str`

**Occurrences**: 1

- `src/flaas/scan.py:30`

## Line: `fingerprint="",`

**Occurrences**: 1

- `src/flaas/scan.py:86`

## Line: `fingerprint=fingerprint,`

**Occurrences**: 1

- `src/flaas/scan.py:70`

## Line: `for a in actions:`

**Occurrences**: 2

- `src/flaas/apply.py`: lines 38, 60

## Line: `for a in obj.get("actions", []):`

**Occurrences**: 1

- `src/flaas/apply.py:25`

## Line: `for tid, tname in enumerate(track_names):`

**Occurrences**: 1

- `src/flaas/scan.py:43`

## Line: `fp = obj.get("live_fingerprint")`

**Occurrences**: 1

- `src/flaas/apply.py:23`

## Line: `fp_parts.append(f"{tid}:{tname}:{num_devices}:" + "|".join([d.class_name for d in devices]))`

**Occurrences**: 1

- `src/flaas/scan.py:60`

## Line: `fp_parts: list[str] = []`

**Occurrences**: 1

- `src/flaas/scan.py:41`

## Line: `host: str = "127.0.0.1"`

**Occurrences**: 2

- `src/flaas/osc.py:8`
- `src/flaas/osc_rpc.py:13`

## Line: `idx = 2 + int(param_id)`

**Occurrences**: 1

- `src/flaas/param_map.py:13`

## Line: `if __name__ == "__main__":`

**Occurrences**: 1

- `src/flaas/cli.py:165`

## Line: `if a.track_role == "MASTER" and a.device == "Utility" and a.param == "Gain":`

**Occurrences**: 1

- `src/flaas/apply.py:61`

## Line: `if args.cmd == "analyze":`

**Occurrences**: 1

- `src/flaas/cli.py:110`

## Line: `if args.cmd == "apply":`

**Occurrences**: 1

- `src/flaas/cli.py:125`

## Line: `if args.cmd == "check":`

**Occurrences**: 1

- `src/flaas/cli.py:115`

## Line: `if args.cmd == "export-guide":`

**Occurrences**: 1

- `src/flaas/cli.py:156`

## Line: `if args.cmd == "loop":`

**Occurrences**: 1

- `src/flaas/cli.py:142`

## Line: `if args.cmd == "ping":`

**Occurrences**: 1

- `src/flaas/cli.py:90`

## Line: `if args.cmd == "plan-gain":`

**Occurrences**: 1

- `src/flaas/cli.py:120`

## Line: `if args.cmd == "reset":`

**Occurrences**: 1

- `src/flaas/cli.py:151`

## Line: `if args.cmd == "scan":`

**Occurrences**: 1

- `src/flaas/cli.py:105`

## Line: `if args.cmd == "util-gain-linear":`

**Occurrences**: 1

- `src/flaas/cli.py:137`

## Line: `if args.cmd == "util-gain-norm":`

**Occurrences**: 1

- `src/flaas/cli.py:132`

## Line: `if args.cmd == "verify":`

**Occurrences**: 1

- `src/flaas/cli.py:146`

## Line: `if args.cmd == "verify-audio":`

**Occurrences**: 1

- `src/flaas/cli.py:160`

## Line: `if args.dry:`

**Occurrences**: 1

- `src/flaas/cli.py:126`

## Line: `if args.version:`

**Occurrences**: 1

- `src/flaas/cli.py:86`

## Line: `if args.wait:`

**Occurrences**: 1

- `src/flaas/cli.py:91`

## Line: `if cur_norm >= 0.99:`

**Occurrences**: 1

- `src/flaas/loop.py:11`

## Line: `if current_fp != expected_fp:`

**Occurrences**: 1

- `src/flaas/apply.py:54`

## Line: `if dry:`

**Occurrences**: 1

- `src/flaas/loop.py:19`

## Line: `if enforce_fingerprint and expected_fp:`

**Occurrences**: 1

- `src/flaas/apply.py:52`

## Line: `if mono.size == 0:`

**Occurrences**: 1

- `src/flaas/analyze.py:25`

## Line: `if pr.max == pr.min:`

**Occurrences**: 1

- `src/flaas/param_map.py:19`

## Line: `index: int`

**Occurrences**: 1

- `src/flaas/scan.py:12`

## Line: `info = read_audio_info(path)`

**Occurrences**: 1

- `src/flaas/analyze.py:23`

## Line: `info = sf.info(str(p))`

**Occurrences**: 1

- `src/flaas/audio_io.py:16`

## Line: `listen_port: int = 11001,  # AbletonOSC reply port`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:20`

## Line: `listen_port=args.listen_port,`

**Occurrences**: 1

- `src/flaas/cli.py:96`

## Line: `live_fingerprint: Optional[str]`

**Occurrences**: 1

- `src/flaas/actions.py:19`

## Line: `live_fingerprint: str | None = None,`

**Occurrences**: 1

- `src/flaas/actions.py:25`

## Line: `live_fingerprint=live_fingerprint,`

**Occurrences**: 1

- `src/flaas/actions.py:33`

## Line: `lufs_i = float(meter.integrated_loudness(mono))`

**Occurrences**: 1

- `src/flaas/analyze.py:32`

## Line: `lufs_i: float`

**Occurrences**: 3

- `src/flaas/analyze.py:19`
- `src/flaas/check.py:13`
- `src/flaas/plan.py:17`

## Line: `lufs_i=a.lufs_i,`

**Occurrences**: 1

- `src/flaas/check.py:26`

## Line: `lufs_i=float(a.lufs_i),`

**Occurrences**: 1

- `src/flaas/plan.py:50`

## Line: `lufs_i=lufs_i,`

**Occurrences**: 1

- `src/flaas/analyze.py:42`

## Line: `main()`

**Occurrences**: 1

- `src/flaas/cli.py:166`

## Line: `master_lufs: float = -10.5`

**Occurrences**: 1

- `src/flaas/targets.py:6`

## Line: `max: float`

**Occurrences**: 1

- `src/flaas/param_map.py:8`

## Line: `meter = pyln.Meter(sr)  # BS.1770`

**Occurrences**: 1

- `src/flaas/analyze.py:31`

## Line: `min: float`

**Occurrences**: 1

- `src/flaas/param_map.py:7`

## Line: `mono = x.mean(axis=1)`

**Occurrences**: 1

- `src/flaas/audio_io.py:27`

## Line: `mono, sr = read_mono_float(path)`

**Occurrences**: 1

- `src/flaas/analyze.py:24`

## Line: `n = linear_to_norm(gain_linear, pr)`

**Occurrences**: 1

- `src/flaas/util.py:19`

## Line: `name: str`

**Occurrences**: 2

- `src/flaas/scan.py`: lines 13, 19

## Line: `new_linear = cur_linear + float(a.delta_db)`

**Occurrences**: 1

- `src/flaas/apply.py:66`

## Line: `new_norm = linear_to_norm(new_linear, pr)`

**Occurrences**: 1

- `src/flaas/apply.py:67`

## Line: `new_norm = verify_master_utility_gain()`

**Occurrences**: 1

- `src/flaas/loop.py:25`

## Line: `note: str`

**Occurrences**: 1

- `src/flaas/scan.py:26`

## Line: `note="live scan",`

**Occurrences**: 1

- `src/flaas/scan.py:66`

## Line: `note=f"scan failed: {type(e).__name__}: {e}",`

**Occurrences**: 1

- `src/flaas/scan.py:82`

## Line: `num_devices = int(nd[1]) if len(nd) > 1 else 0`

**Occurrences**: 1

- `src/flaas/scan.py:46`

## Line: `num_devices: int`

**Occurrences**: 1

- `src/flaas/scan.py:20`

## Line: `num_tracks: int`

**Occurrences**: 1

- `src/flaas/scan.py:28`

## Line: `num_tracks=0,`

**Occurrences**: 1

- `src/flaas/scan.py:84`

## Line: `num_tracks=num_tracks,`

**Occurrences**: 1

- `src/flaas/scan.py:68`

## Line: `ok = c.pass_lufs and c.pass_peak`

**Occurrences**: 1

- `src/flaas/verify_audio.py:12`

## Line: `ok: bool`

**Occurrences**: 1

- `src/flaas/scan.py:25`

## Line: `ok=False,`

**Occurrences**: 1

- `src/flaas/scan.py:81`

## Line: `ok=True,`

**Occurrences**: 1

- `src/flaas/scan.py:65`

## Line: `out = write_actions(actions, out_actions, live_fingerprint=scan_live().fingerprint)`

**Occurrences**: 1

- `src/flaas/plan.py:66`

## Line: `out = write_analysis(args.wav, args.out)`

**Occurrences**: 1

- `src/flaas/cli.py:111`

## Line: `out = write_check(args.wav, args.out)`

**Occurrences**: 1

- `src/flaas/cli.py:116`

## Line: `out.parent.mkdir(parents=True, exist_ok=True)`

**Occurrences**: 4

- `src/flaas/actions.py:29`
- `src/flaas/analyze.py:48`
- `src/flaas/check.py:34`
- `src/flaas/scan.py:75`

## Line: `p.print_help()`

**Occurrences**: 1

- `src/flaas/cli.py:163`

## Line: `param: str`

**Occurrences**: 2

- `src/flaas/actions.py:12`
- `src/flaas/apply.py:15`

## Line: `param="Gain",`

**Occurrences**: 1

- `src/flaas/plan.py:62`

## Line: `param=a["param"],`

**Occurrences**: 1

- `src/flaas/apply.py:30`

## Line: `pass_lufs = abs(a.lufs_i - targets.master_lufs) <= 0.5`

**Occurrences**: 1

- `src/flaas/check.py:20`

## Line: `pass_lufs: bool`

**Occurrences**: 1

- `src/flaas/check.py:11`

## Line: `pass_lufs=pass_lufs,`

**Occurrences**: 1

- `src/flaas/check.py:24`

## Line: `pass_peak = a.peak_dbfs <= targets.stem_peak_ceiling_dbfs`

**Occurrences**: 1

- `src/flaas/check.py:21`

## Line: `pass_peak: bool`

**Occurrences**: 1

- `src/flaas/check.py:12`

## Line: `pass_peak=pass_peak,`

**Occurrences**: 1

- `src/flaas/check.py:25`

## Line: `path = write_model_cache(args.out)`

**Occurrences**: 1

- `src/flaas/cli.py:106`

## Line: `path: str`

**Occurrences**: 1

- `src/flaas/audio_io.py:9`

## Line: `path=str(p),`

**Occurrences**: 1

- `src/flaas/audio_io.py:18`

## Line: `path_out: str | Path = "data/actions/actions.json",`

**Occurrences**: 1

- `src/flaas/actions.py:24`

## Line: `payload = ActionsFile(`

**Occurrences**: 1

- `src/flaas/actions.py:30`

## Line: `payload = ScanResult(`

**Occurrences**: 1

- `src/flaas/scan.py:80`

## Line: `payload = scan_live()`

**Occurrences**: 1

- `src/flaas/scan.py:78`

## Line: `peak_dbfs = -float("inf") if peak == 0.0 else float(20.0 * np.log10(peak))`

**Occurrences**: 1

- `src/flaas/analyze.py:29`

## Line: `peak_dbfs: float`

**Occurrences**: 2

- `src/flaas/analyze.py:18`
- `src/flaas/check.py:14`

## Line: `peak_dbfs=a.peak_dbfs,`

**Occurrences**: 1

- `src/flaas/check.py:27`

## Line: `peak_dbfs=peak_dbfs,`

**Occurrences**: 1

- `src/flaas/analyze.py:41`

## Line: `port: int = 11000`

**Occurrences**: 1

- `src/flaas/osc.py:9`

## Line: `port: int = 11000  # AbletonOSC listen port`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:14`

## Line: `pr = get_param_range(0, 0, UTILITY_GAIN_PARAM_ID, target=target)`

**Occurrences**: 1

- `src/flaas/apply.py:58`

## Line: `pr = get_param_range(track_id, device_id, UTILITY_GAIN_PARAM_ID, target=target)`

**Occurrences**: 2

- `src/flaas/plan.py:23`
- `src/flaas/util.py:18`

## Line: `print("- Bit Depth: 24-bit")`

**Occurrences**: 1

- `src/flaas/export_guide.py:7`

## Line: `print("- Convert to Mono: Off")`

**Occurrences**: 1

- `src/flaas/export_guide.py:11`

## Line: `print("- Create Analysis File: Off")`

**Occurrences**: 1

- `src/flaas/export_guide.py:12`

## Line: `print("- Dither: Off")`

**Occurrences**: 1

- `src/flaas/export_guide.py:9`

## Line: `print("- Export to: repo/output/ (keep filename stable)")`

**Occurrences**: 1

- `src/flaas/export_guide.py:13`

## Line: `print("- File Type: WAV")`

**Occurrences**: 1

- `src/flaas/export_guide.py:8`

## Line: `print("- Normalize: Off")`

**Occurrences**: 1

- `src/flaas/export_guide.py:10`

## Line: `print("- Render Length: full song (all stems same length)")`

**Occurrences**: 1

- `src/flaas/export_guide.py:5`

## Line: `print("- Render Start: 1.1.1")`

**Occurrences**: 1

- `src/flaas/export_guide.py:4`

## Line: `print("- Rendered Track: Master")`

**Occurrences**: 1

- `src/flaas/export_guide.py:3`

## Line: `print("- Sample Rate: 48000 Hz")`

**Occurrences**: 1

- `src/flaas/export_guide.py:6`

## Line: `print("0.0.2")`

**Occurrences**: 1

- `src/flaas/cli.py:87`

## Line: `print("ABLETON EXPORT GUIDE (MVP manual step)")`

**Occurrences**: 1

- `src/flaas/export_guide.py:2`

## Line: `print("DONE: planned (dry-run, no OSC)")`

**Occurrences**: 1

- `src/flaas/loop.py:21`

## Line: `print("PASS" if ok else "FAIL")`

**Occurrences**: 1

- `src/flaas/verify_audio.py:13`

## Line: `print("sent")`

**Occurrences**: 4

- `src/flaas/cli.py`: lines 102, 134, 139, 153

## Line: `print(f"APPLIED: Utility.Gain {cur_linear:.3f} -> {new_linear:.3f} (norm {cur_norm:.3f}->{new_norm:.3f})")`

**Occurrences**: 1

- `src/flaas/apply.py:70`

## Line: `print(f"CUR_LINEAR: {r.cur_linear:.3f}  DELTA: {r.delta_linear:.3f}")`

**Occurrences**: 1

- `src/flaas/plan.py:69`

## Line: `print(f"DONE: planned+applied (norm={new_norm:.3f})")`

**Occurrences**: 1

- `src/flaas/loop.py:26`

## Line: `print(f"DRY_RUN: {a.track_role} :: {a.device}.{a.param} += {a.delta_db:.2f}")`

**Occurrences**: 1

- `src/flaas/apply.py:39`

## Line: `print(f"FILE: {a.file}")`

**Occurrences**: 1

- `src/flaas/verify_audio.py:9`

## Line: `print(f"LUFS: {a.lufs_i:.2f} (target {c.target_lufs:.2f})  pass={c.pass_lufs}")`

**Occurrences**: 1

- `src/flaas/verify_audio.py:10`

## Line: `print(f"MEASURE: LUFS={a.lufs_i:.2f} peak_dBFS={a.peak_dbfs:.2f}")`

**Occurrences**: 1

- `src/flaas/loop.py:16`

## Line: `print(f"PEAK: {a.peak_dbfs:.2f} dBFS (limit {c.target_peak_dbfs:.2f}) pass={c.pass_peak}")`

**Occurrences**: 1

- `src/flaas/verify_audio.py:11`

## Line: `print(f"SKIP: unsupported action {a}")`

**Occurrences**: 1

- `src/flaas/apply.py:72`

## Line: `print(f"STOP: utility gain already near max (norm={cur_norm:.3f})")`

**Occurrences**: 1

- `src/flaas/loop.py:12`

## Line: `print(f"ok: {resp}")`

**Occurrences**: 1

- `src/flaas/cli.py:99`

## Line: `print(str(out))`

**Occurrences**: 3

- `src/flaas/cli.py`: lines 112, 117, 122

## Line: `print(str(path))`

**Occurrences**: 1

- `src/flaas/cli.py:107`

## Line: `print(v)`

**Occurrences**: 1

- `src/flaas/cli.py:148`

## Line: `print_export_guide()`

**Occurrences**: 1

- `src/flaas/cli.py:157`

## Line: `q.put(tuple(args))`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:31`

## Line: `q: "queue.Queue[tuple[Any, ...]]" = queue.Queue()`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:26`

## Line: `raw = err_db / 12.0`

**Occurrences**: 1

- `src/flaas/plan.py:40`

## Line: `return`

**Occurrences**: 15

- `src/flaas/cli.py`: lines 88, 103, 108, 113, 118, 123, 130, 135, 140, 144, 149, 154, 158
- `src/flaas/loop.py`: lines 13, 22

## Line: `return (v - pr.min) / (pr.max - pr.min)`

**Occurrences**: 1

- `src/flaas/param_map.py:21`

## Line: `return 0 if ok else 1`

**Occurrences**: 1

- `src/flaas/verify_audio.py:14`

## Line: `return 0.0`

**Occurrences**: 1

- `src/flaas/param_map.py:20`

## Line: `return AnalysisResult(`

**Occurrences**: 1

- `src/flaas/analyze.py:35`

## Line: `return AudioData(`

**Occurrences**: 1

- `src/flaas/audio_io.py:17`

## Line: `return CheckResult(`

**Occurrences**: 1

- `src/flaas/check.py:22`

## Line: `return ParamRange(min=float(mins[idx]), max=float(maxs[idx]))`

**Occurrences**: 1

- `src/flaas/param_map.py:14`

## Line: `return PlanGainResult(`

**Occurrences**: 1

- `src/flaas/plan.py:48`

## Line: `return ScanResult(`

**Occurrences**: 1

- `src/flaas/scan.py:64`

## Line: `return args`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:51`

## Line: `return float(resp[3])`

**Occurrences**: 1

- `src/flaas/verify.py:9`

## Line: `return fp, actions`

**Occurrences**: 1

- `src/flaas/apply.py:34`

## Line: `return hashlib.sha256(s.encode("utf-8")).hexdigest()`

**Occurrences**: 1

- `src/flaas/scan.py:33`

## Line: `return mono, int(sr)`

**Occurrences**: 1

- `src/flaas/audio_io.py:28`

## Line: `return out`

**Occurrences**: 5

- `src/flaas/actions.py:37`
- `src/flaas/analyze.py:51`
- `src/flaas/check.py:37`
- `src/flaas/plan.py:70`
- `src/flaas/scan.py:90`

## Line: `return pr.min + cur_norm * (pr.max - pr.min)`

**Occurrences**: 1

- `src/flaas/plan.py:26`

## Line: `run_loop(args.wav, dry=args.dry)`

**Occurrences**: 1

- `src/flaas/cli.py:143`

## Line: `samples: int`

**Occurrences**: 2

- `src/flaas/analyze.py:16`
- `src/flaas/audio_io.py:12`

## Line: `samples=info.samples,`

**Occurrences**: 1

- `src/flaas/analyze.py:39`

## Line: `samples=int(info.frames),`

**Occurrences**: 1

- `src/flaas/audio_io.py:21`

## Line: `schema_version: str`

**Occurrences**: 1

- `src/flaas/actions.py:17`

## Line: `schema_version: str = "1.0",`

**Occurrences**: 1

- `src/flaas/actions.py:26`

## Line: `schema_version=schema_version,`

**Occurrences**: 1

- `src/flaas/actions.py:31`

## Line: `server = ThreadingOSCUDPServer(("0.0.0.0", listen_port), disp)`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:35`

## Line: `server.server_close()`

**Occurrences**: 2

- `src/flaas/osc_rpc.py`: lines 46, 50

## Line: `server.shutdown()`

**Occurrences**: 2

- `src/flaas/osc_rpc.py`: lines 45, 49

## Line: `set_utility_gain_linear(args.track_id, args.device_id, args.gain_linear, target=RpcTarget(host=args.host, port=args.port))`

**Occurrences**: 1

- `src/flaas/cli.py:138`

## Line: `set_utility_gain_norm(0, 0, 0.5, target=RpcTarget(host=args.host, port=args.port))`

**Occurrences**: 1

- `src/flaas/cli.py:152`

## Line: `set_utility_gain_norm(args.track_id, args.device_id, args.gain_norm, target=RpcTarget(host=args.host, port=args.port))`

**Occurrences**: 1

- `src/flaas/cli.py:133`

## Line: `set_utility_gain_norm(track_id, device_id, n, target=target)`

**Occurrences**: 1

- `src/flaas/util.py:20`

## Line: `sr: int`

**Occurrences**: 2

- `src/flaas/analyze.py:14`
- `src/flaas/audio_io.py:10`

## Line: `sr=info.sr,`

**Occurrences**: 1

- `src/flaas/analyze.py:37`

## Line: `sr=int(info.samplerate),`

**Occurrences**: 1

- `src/flaas/audio_io.py:19`

## Line: `stem_peak_ceiling_dbfs: float = -6.0`

**Occurrences**: 1

- `src/flaas/targets.py:8`

## Line: `sub = p.add_subparsers(dest="cmd")`

**Occurrences**: 1

- `src/flaas/cli.py:18`

## Line: `t = threading.Thread(target=server.serve_forever, daemon=True)`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:36`

## Line: `t.start()`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:37`

## Line: `target: OscTarget = OscTarget(),`

**Occurrences**: 1

- `src/flaas/apply.py:43`

## Line: `target: OscTarget,`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:17`

## Line: `target_lufs: float`

**Occurrences**: 2

- `src/flaas/check.py:15`
- `src/flaas/plan.py:18`

## Line: `target_lufs=float(targets.master_lufs),`

**Occurrences**: 1

- `src/flaas/plan.py:51`

## Line: `target_lufs=targets.master_lufs,`

**Occurrences**: 1

- `src/flaas/check.py:28`

## Line: `target_osc: OscTarget = OscTarget(),`

**Occurrences**: 1

- `src/flaas/plan.py:32`

## Line: `target_peak_dbfs: float`

**Occurrences**: 1

- `src/flaas/check.py:16`

## Line: `target_peak_dbfs=targets.stem_peak_ceiling_dbfs,`

**Occurrences**: 1

- `src/flaas/check.py:29`

## Line: `targets: Targets = DEFAULT_TARGETS,`

**Occurrences**: 1

- `src/flaas/plan.py:30`

## Line: `timeout_sec: float = 2.0,`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:21`

## Line: `timeout_sec=args.timeout,`

**Occurrences**: 1

- `src/flaas/cli.py:97`

## Line: `track_id: int`

**Occurrences**: 1

- `src/flaas/scan.py:18`

## Line: `track_names = list(names)[:num_tracks]`

**Occurrences**: 1

- `src/flaas/scan.py:38`

## Line: `track_role: str`

**Occurrences**: 2

- `src/flaas/actions.py:10`
- `src/flaas/apply.py:13`

## Line: `track_role="MASTER",`

**Occurrences**: 1

- `src/flaas/plan.py:60`

## Line: `track_role=a["track_role"],`

**Occurrences**: 1

- `src/flaas/apply.py:28`

## Line: `tracks.append(TrackInfo(track_id=tid, name=str(tname), num_devices=num_devices, devices=devices))`

**Occurrences**: 1

- `src/flaas/scan.py:59`

## Line: `tracks: list[TrackInfo]`

**Occurrences**: 1

- `src/flaas/scan.py:29`

## Line: `tracks: list[TrackInfo] = []`

**Occurrences**: 1

- `src/flaas/scan.py:40`

## Line: `tracks=[],`

**Occurrences**: 1

- `src/flaas/scan.py:85`

## Line: `tracks=tracks,`

**Occurrences**: 1

- `src/flaas/scan.py:69`

## Line: `true_peak_ceiling_dbfs: float = -1.0  # placeholder until TP estimator exists`

**Occurrences**: 1

- `src/flaas/targets.py:7`

## Line: `try:`

**Occurrences**: 2

- `src/flaas/osc_rpc.py:42`
- `src/flaas/scan.py:77`

## Line: `v = verify_master_utility_gain(args.track_id, args.device_id, target=RpcTarget(host=args.host, port=args.port))`

**Occurrences**: 1

- `src/flaas/cli.py:147`

## Line: `value: Any = 1,`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:19`

## Line: `wav: str | Path,`

**Occurrences**: 1

- `src/flaas/plan.py:29`

## Line: `x = x.astype(np.float32)`

**Occurrences**: 1

- `src/flaas/audio_io.py:26`

