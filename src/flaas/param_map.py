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
    idx = 2 + int(param_id)
    return ParamRange(min=float(mins[idx]), max=float(maxs[idx]))

def linear_to_norm(x: float, pr: ParamRange) -> float:
    # map [min,max] to [0,1]
    v = max(pr.min, min(pr.max, float(x)))
    if pr.max == pr.min:
        return 0.0
    return (v - pr.min) / (pr.max - pr.min)
