from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

from flaas.analyze import analyze_wav
from flaas.targets import Targets, DEFAULT_TARGETS
from flaas.actions import GainAction, write_actions
from flaas.scan import scan_live
from flaas.osc_rpc import OscTarget, request_once
from flaas.param_map import get_param_range

MASTER_TRACK_ID = -1000
UTILITY_GAIN_PARAM_ID = 9


def _resolve_utility_device_id(track_id: int, target: OscTarget = OscTarget()) -> int:
    """
    Resolve Utility device ID on the given track by querying device names.
    
    Returns device index if found.
    Raises SystemExit(20) if Utility device not found.
    """
    try:
        response = request_once(
            target,
            "/live/track/get/devices/name",
            [track_id],
            timeout_sec=3.0
        )
        # Response format: (track_id, name0, name1, name2, ...)
        # Drop the first element (track_id), keep device names
        names = list(response)[1:]
        
        for idx, name in enumerate(names):
            if str(name).strip().lower() == "utility":
                return idx
        
        # Utility not found
        print(f"ERROR: Utility device not found on track {track_id}", file=sys.stderr)
        print(f"Available devices: {names}", file=sys.stderr)
        raise SystemExit(20)
        
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: Failed to query devices on track {track_id}: {e}", file=sys.stderr)
        raise SystemExit(20)

@dataclass(frozen=True)
class PlanGainResult:
    delta_linear: float
    lufs_i: float
    target_lufs: float
    clamped: bool
    cur_linear: float

def _get_current_utility_linear(track_id: int, device_id: int, target: OscTarget = OscTarget()) -> float:
    """Get current Utility gain in linear space."""
    pr = get_param_range(track_id, device_id, UTILITY_GAIN_PARAM_ID, target=target)
    cur = request_once(target, "/live/device/get/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)
    cur_norm = float(cur[3])
    return pr.min + cur_norm * (pr.max - pr.min)

def plan_utility_gain_delta_for_master(
    wav: str | Path,
    targets: Targets = DEFAULT_TARGETS,
    clamp_linear: float = 0.25,
    target_osc: OscTarget = OscTarget(),
) -> PlanGainResult:
    """
    Compute LUFS error and convert to a SMALL delta (bounded) to avoid runaway stacking.
    delta_linear ~= (target_lufs - measured_lufs) / 12, then clamped to ±clamp_linear.
    
    Uses MASTER_TRACK_ID (-1000) and dynamically resolves Utility device index.
    """
    # Resolve Utility device ID on master track
    utility_device_id = _resolve_utility_device_id(MASTER_TRACK_ID, target=target_osc)
    
    a = analyze_wav(wav)
    err_db = targets.master_lufs - a.lufs_i
    raw = err_db / 12.0
    delta = raw
    if delta > clamp_linear:
        delta = clamp_linear
    if delta < -clamp_linear:
        delta = -clamp_linear
    clamped = (delta != raw)
    cur_linear = _get_current_utility_linear(
        track_id=MASTER_TRACK_ID,
        device_id=utility_device_id,
        target=target_osc
    )
    return PlanGainResult(
        delta_linear=float(delta),
        lufs_i=float(a.lufs_i),
        target_lufs=float(targets.master_lufs),
        clamped=clamped,
        cur_linear=float(cur_linear),
    )

def write_plan_gain_actions(wav: str | Path, out_actions: str | Path = "data/actions/actions.json") -> Path:
    r = plan_utility_gain_delta_for_master(wav)
    actions = [
        GainAction(
            track_role="MASTER",
            device="Utility",
            param="Gain",
            delta_db=r.delta_linear,
        )
    ]
    out = write_actions(actions, out_actions, live_fingerprint=scan_live().fingerprint)
    if r.clamped:
        print(f"WARNING: delta clamped to {r.delta_linear:.3f} (raw would exceed clamp).")
    print(f"CUR_LINEAR: {r.cur_linear:.3f}  DELTA: {r.delta_linear:.3f}")
    return out
