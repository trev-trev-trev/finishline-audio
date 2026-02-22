# Unique Lines: Osc Calls

**Total unique lines**: 17

---

## Line: `client.send_message("/live/device/set/parameter/value", [0, 0, UTILITY_GAIN_PARAM_ID, float(new_norm)])`

**Occurrences**: 1

- `src/flaas/apply.py:69`

## Line: `client.send_message("/live/device/set/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID, v])`

**Occurrences**: 1

- `src/flaas/util.py:11`

## Line: `client.send_message(address, value)`

**Occurrences**: 2

- `src/flaas/osc.py:13`
- `src/flaas/osc_rpc.py:40`

## Line: `cur = request_once(target, "/live/device/get/parameter/value", [0,0,UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)`

**Occurrences**: 1

- `src/flaas/apply.py:62`

## Line: `cur = request_once(target, "/live/device/get/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)`

**Occurrences**: 1

- `src/flaas/plan.py:24`

## Line: `dc = request_once(target, "/live/track/get/devices/class_name", [tid], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/scan.py:49`

## Line: `def request_once(`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:16`

## Line: `def send_ping(target: OscTarget, address: str = "/live/test", value: Any = "ok") -> None:`

**Occurrences**: 1

- `src/flaas/osc.py:11`

## Line: `dn = request_once(target, "/live/track/get/devices/name", [tid], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/scan.py:48`

## Line: `maxs = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/param_map.py:12`

## Line: `mins = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/param_map.py:11`

## Line: `names = request_once(target, "/live/song/get/track_names", [], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/scan.py:37`

## Line: `nd = request_once(target, "/live/track/get/num_devices", [tid], timeout_sec=timeout_sec)`

**Occurrences**: 1

- `src/flaas/scan.py:44`

## Line: `num_tracks = int(request_once(target, "/live/song/get/num_tracks", None, timeout_sec=timeout_sec)[0])`

**Occurrences**: 1

- `src/flaas/scan.py:36`

## Line: `resp = request_once(`

**Occurrences**: 1

- `src/flaas/cli.py:92`

## Line: `resp = request_once(target, "/live/device/get/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)`

**Occurrences**: 1

- `src/flaas/verify.py:7`

## Line: `send_ping(FireAndForgetTarget(host=args.host, port=args.port), value=args.arg)`

**Occurrences**: 1

- `src/flaas/cli.py:101`

