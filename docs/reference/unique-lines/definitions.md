# Unique Lines: Definitions

**Total unique lines**: 35

---

## Line: `class ActionsFile:`

**Occurrences**: 1

- `src/flaas/actions.py:16`

## Line: `class AnalysisResult:`

**Occurrences**: 1

- `src/flaas/analyze.py:12`

## Line: `class AudioData:`

**Occurrences**: 1

- `src/flaas/audio_io.py:8`

## Line: `class CheckResult:`

**Occurrences**: 1

- `src/flaas/check.py:9`

## Line: `class DeviceInfo:`

**Occurrences**: 1

- `src/flaas/scan.py:11`

## Line: `class GainAction:`

**Occurrences**: 1

- `src/flaas/actions.py:9`

## Line: `class LoadedAction:`

**Occurrences**: 1

- `src/flaas/apply.py:12`

## Line: `class OscTarget:`

**Occurrences**: 2

- `src/flaas/osc.py:7`
- `src/flaas/osc_rpc.py:12`

## Line: `class ParamRange:`

**Occurrences**: 1

- `src/flaas/param_map.py:6`

## Line: `class PlanGainResult:`

**Occurrences**: 1

- `src/flaas/plan.py:15`

## Line: `class ScanResult:`

**Occurrences**: 1

- `src/flaas/scan.py:24`

## Line: `class Targets:`

**Occurrences**: 1

- `src/flaas/targets.py:5`

## Line: `class TrackInfo:`

**Occurrences**: 1

- `src/flaas/scan.py:17`

## Line: `def _get_current_utility_linear(track_id: int = 0, device_id: int = 0, target: OscTarget = OscTarget()) -> float:`

**Occurrences**: 1

- `src/flaas/plan.py:22`

## Line: `def _handler(_addr: str, *args: Any) -> None:`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:30`

## Line: `def _read_actions_file(path: str | Path) -> tuple[str | None, list[LoadedAction]]:`

**Occurrences**: 1

- `src/flaas/apply.py:20`

## Line: `def _sha256(s: str) -> str:`

**Occurrences**: 1

- `src/flaas/scan.py:32`

## Line: `def apply_actions_dry_run(path: str | Path = "data/actions/actions.json") -> None:`

**Occurrences**: 1

- `src/flaas/apply.py:36`

## Line: `def apply_actions_osc(`

**Occurrences**: 1

- `src/flaas/apply.py:41`

## Line: `def get_param_range(track_id: int, device_id: int, param_id: int, target: OscTarget = OscTarget(), timeout_sec: float = 3.0) -> ParamRange:`

**Occurrences**: 1

- `src/flaas/param_map.py:10`

## Line: `def linear_to_norm(x: float, pr: ParamRange) -> float:`

**Occurrences**: 1

- `src/flaas/param_map.py:16`

## Line: `def main() -> None:`

**Occurrences**: 1

- `src/flaas/cli.py:16`

## Line: `def print_export_guide() -> None:`

**Occurrences**: 1

- `src/flaas/export_guide.py:1`

## Line: `def read_audio_info(path: str | Path) -> AudioData:`

**Occurrences**: 1

- `src/flaas/audio_io.py:14`

## Line: `def read_mono_float(path: str | Path) -> tuple[np.ndarray, int]:`

**Occurrences**: 1

- `src/flaas/audio_io.py:24`

## Line: `def run_loop(wav: str | Path, dry: bool = False) -> None:`

**Occurrences**: 1

- `src/flaas/loop.py:9`

## Line: `def scan_live(target: OscTarget = OscTarget(), timeout_sec: float = 2.0) -> ScanResult:`

**Occurrences**: 1

- `src/flaas/scan.py:35`

## Line: `def set_utility_gain_linear(track_id: int, device_id: int, gain_linear: float, target: OscTarget = OscTarget()) -> None:`

**Occurrences**: 1

- `src/flaas/util.py:13`

## Line: `def set_utility_gain_norm(track_id: int, device_id: int, gain_norm_0_1: float, target: OscTarget = OscTarget()) -> None:`

**Occurrences**: 1

- `src/flaas/util.py:8`

## Line: `def verify_audio(path: str | Path) -> int:`

**Occurrences**: 1

- `src/flaas/verify_audio.py:6`

## Line: `def verify_master_utility_gain(track_id: int = 0, device_id: int = 0, target: OscTarget = OscTarget()) -> float:`

**Occurrences**: 1

- `src/flaas/verify.py:6`

## Line: `def write_actions(`

**Occurrences**: 1

- `src/flaas/actions.py:22`

## Line: `def write_analysis(path_in: str | Path, path_out: str | Path = "data/reports/analysis.json") -> Path:`

**Occurrences**: 1

- `src/flaas/analyze.py:46`

## Line: `def write_check(path_in: str | Path, path_out: str | Path = "data/reports/check.json") -> Path:`

**Occurrences**: 1

- `src/flaas/check.py:32`

## Line: `def write_model_cache(path: str | Path = "data/caches/model_cache.json") -> Path:`

**Occurrences**: 1

- `src/flaas/scan.py:73`

