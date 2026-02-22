from __future__ import annotations
from dataclasses import dataclass
from flaas.osc_rpc import OscTarget, request_once

@dataclass(frozen=True)
class ParamRange:
    min: float
    max: float

def get_param_range(track_id: int, device_id: int, param_id: int, target: OscTarget = OscTarget(), timeout_sec: float = 3.0) -> ParamRange:
    mn = request_once(target, "/live/device/get/parameter/min", [track_id, device_id, param_id], timeout_sec=timeout_sec)
    mx = request_once(target, "/live/device/get/parameter/max", [track_id, device_id, param_id], timeout_sec=timeout_sec)
    # responses: (track_id, device_id, param_id, value)
    return ParamRange(min=float(mn[3]), max=float(mx[3]))

def db_to_norm(db: float, pr: ParamRange) -> float:
    # clamp into range then scale
    v = max(pr.min, min(pr.max, db))
    if pr.max == pr.min:
        return 0.0
    return (v - pr.min) / (pr.max - pr.min)

def norm_to_db(norm: float, pr: ParamRange) -> float:
    n = max(0.0, min(1.0, float(norm)))
    return pr.min + n * (pr.max - pr.min)
