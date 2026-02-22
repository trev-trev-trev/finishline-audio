from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once

UTILITY_GAIN_PARAM_ID = 9

def verify_master_utility_gain(track_id: int = 0, device_id: int = 0, target: OscTarget = OscTarget()) -> float:
    resp = request_once(target, "/live/device/get/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)
    # (track_id, device_id, param_id, value)
    return float(resp[3])
