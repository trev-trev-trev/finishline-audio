from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once
from flaas.targets import MASTER_TRACK_ID, resolve_utility_device_id

UTILITY_GAIN_PARAM_ID = 9

def verify_master_utility_gain(
    track_id: int | None = None,
    device_id: int | None = None,
    target: OscTarget = OscTarget()
) -> float:
    """
    Verify master Utility gain parameter value.
    
    Args:
        track_id: Track ID (defaults to MASTER_TRACK_ID = -1000)
        device_id: Device ID (defaults to dynamically resolved Utility index)
        target: OSC target
    
    Returns:
        Normalized parameter value (0.0 - 1.0)
    """
    # Default to master track
    if track_id is None:
        track_id = MASTER_TRACK_ID
    
    # Default to dynamically resolved Utility device
    if device_id is None:
        device_id = resolve_utility_device_id(target)
    
    resp = request_once(target, "/live/device/get/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)
    # (track_id, device_id, param_id, value)
    return float(resp[3])
