# Unique Lines: Safety

**Total unique lines**: 19

---

## Line: `clamp_linear: float = 0.25,`

**Occurrences**: 1

- `src/flaas/plan.py:31`

## Line: `clamped = (delta != raw)`

**Occurrences**: 1

- `src/flaas/plan.py:46`

## Line: `clamped: bool`

**Occurrences**: 1

- `src/flaas/plan.py:19`

## Line: `clamped=clamped,`

**Occurrences**: 1

- `src/flaas/plan.py:52`

## Line: `delta = -clamp_linear`

**Occurrences**: 1

- `src/flaas/plan.py:45`

## Line: `delta = clamp_linear`

**Occurrences**: 1

- `src/flaas/plan.py:43`

## Line: `delta_linear ~= (target_lufs - measured_lufs) / 12, then clamped to ±clamp_linear.`

**Occurrences**: 1

- `src/flaas/plan.py:36`

## Line: `for i in range(min(len(dev_names), len(dev_class))):`

**Occurrences**: 1

- `src/flaas/scan.py:56`

## Line: `if delta < -clamp_linear:`

**Occurrences**: 1

- `src/flaas/plan.py:44`

## Line: `if delta > clamp_linear:`

**Occurrences**: 1

- `src/flaas/plan.py:42`

## Line: `if r.clamped:`

**Occurrences**: 1

- `src/flaas/plan.py:67`

## Line: `peak = float(np.max(np.abs(mono)))`

**Occurrences**: 1

- `src/flaas/analyze.py:28`

## Line: `print(f"WARNING: delta clamped to {r.delta_linear:.3f} (raw would exceed clamp).")`

**Occurrences**: 1

- `src/flaas/plan.py:68`

## Line: `raise RuntimeError(f"Live fingerprint mismatch: expected {expected_fp}, got {current_fp}")`

**Occurrences**: 1

- `src/flaas/apply.py:55`

## Line: `raise SystemExit(verify_audio(args.wav))`

**Occurrences**: 1

- `src/flaas/cli.py:161`

## Line: `raise TimeoutError(f"Timed out waiting for reply on :{listen_port} for {address}") from e`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:47`

## Line: `raise ValueError("empty audio")`

**Occurrences**: 1

- `src/flaas/analyze.py:26`

## Line: `v = float(max(0.0, min(1.0, gain_norm_0_1)))`

**Occurrences**: 1

- `src/flaas/util.py:9`

## Line: `v = max(pr.min, min(pr.max, float(x)))`

**Occurrences**: 1

- `src/flaas/param_map.py:18`

