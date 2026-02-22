from __future__ import annotations
from dataclasses import dataclass
from flaas.osc_rpc import OscTarget, request_once

@dataclass(frozen=True)
class ParamRange:
    min: float
    max: float

def get_param_range(track_id: int, device_id: int, param_id: int, target: OscTarget = OscTarget(), timeout_sec: float = 3.0) -> ParamRange:
    mins = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)
    maxs = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)
    # responses: (track_id, device_id, [values...])
    idx = 2 + int(param_id)
    if idx >= len(mins) or idx >= len(maxs):
        raise IndexError(f"param_id {param_id} out of range (mins={len(mins)-2}, maxs={len(maxs)-2})")
    return ParamRange(min=float(mins[idx]), max=float(maxs[idx]))

def db_to_norm(db: float, pr: ParamRange) -> float:
    v = max(pr.min, min(pr.max, float(db)))
    if pr.max == pr.min:
        return 0.0
    return (v - pr.min) / (pr.max - pr.min)

def norm_to_db(norm: float, pr: ParamRange) -> float:
    n = max(0.0, min(1.0, float(norm)))
    return pr.min + n * (pr.max - pr.min)
